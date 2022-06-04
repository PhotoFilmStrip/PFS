# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#

import re
import threading
import time

import wx

import photofilmstrip.res.cursors as cursors

from photofilmstrip.lib.common.ObserverPattern import Observable, Observer

from photofilmstrip.core.Aspect import Aspect
from photofilmstrip.core import PILBackend

from photofilmstrip.gui.util.ImageCache import ImageCache

EVT_RECT_CHANGED_TYPE = wx.NewEventType()
EVT_RECT_CHANGED = wx.PyEventBinder(EVT_RECT_CHANGED_TYPE, 1)


class RectChangedEvent(wx.PyCommandEvent):

    def __init__(self, wxId, rect):
        wx.PyCommandEvent.__init__(self, EVT_RECT_CHANGED_TYPE, wxId)
        self._rect = rect
        self._checkImageDimensionLock = False

    def GetRect(self):
        return self._rect

    def SetCheckImageDimensionLock(self, value):
        self._checkImageDimensionLock = value

    def CheckImageDimensionLock(self):
        return self._checkImageDimensionLock


class ImageSectionEditor(wx.Panel, Observer):

    BORDER_TOLERANCE = 20

    POSITION_INSIDE = 0x01

    POSITION_TOP = 0x10
    POSITION_BOTTOM = 0x20
    POSITION_LEFT = 0x40
    POSITION_RIGHT = 0x80

    INFO_TIME_OUT = 2.0

    def __init__(self, parent, id=wx.ID_ANY,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0, name='panel'):
        wx.Panel.__init__(self, parent, id, pos, size, style, name)
        Observer.__init__(self)

        self.SetSizeHints(200, 150)
        self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        self.RATIO = 16.0 / 9.0
        self._imgProxy = None
        self._sectRect = wx.Rect(0, 0, 1280, 720)
        self._zoom = 1
        self._infoTimer = wx.Timer(self)
        self._lastRectUpdate = 0

        self._action = None
        self._startX = None
        self._startY = None
        self._startRect = None

        self._lock = True

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_TIMER, self.OnInfoTimer)
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.OnCaptureLost)

    def ObservableUpdate(self, obj, arg):
        self.__Scale()
        self.__KeepRectInImage()
        self.Refresh()

    def SetAspect(self, aspect):
        self.RATIO = Aspect.ToFloat(aspect)
        self.__KeepRectInImage()
        self.Refresh()

    def SetImgProxy(self, imgProxy):
        self._imgProxy = imgProxy

    def __Scale(self):
        if not self._imgProxy.IsOk():
            return

        cw, ch = self.GetClientSize().Get()
        iw, ih = self._imgProxy.GetSize()
        rx = cw / iw
        ry = ch / ih

        newWidth = cw
        newHeight = ih * rx
        self._zoom = rx

        if newHeight > ch:
            newHeight = ch
            newWidth = iw * ry
            self._zoom = ry

        self._imgProxy.Scale(int(round(newWidth)), int(round(newHeight)))

    def __DrawBitmap(self, dc):
        if self._imgProxy.IsOk():
            left, top = self.__GetBmpTopLeft()
            dc.DrawBitmap(self._imgProxy.GetBitmap(), left, top)

    def __GetBmpTopLeft(self):
        if not self._imgProxy.IsOk():
            return 0, 0
        cw, ch = self.GetClientSize().Get()
        iw, ih = self._imgProxy.GetCurrentSize()
        left = (cw - iw) / 2.0
        top = (ch - ih) / 2.0
        return int(round(left)), int(round(top))

    def __SectRectToClientRect(self):
        left, top = self.__GetBmpTopLeft()
        sectRect = wx.Rect(left + int(round(self._sectRect.GetLeft() * self._zoom)),
                           top + int(round(self._sectRect.GetTop() * self._zoom)),
                           int(round(self._sectRect.GetWidth() * self._zoom)),
                           int(round(self._sectRect.GetHeight() * self._zoom)))
        return sectRect

    def __DrawSection(self, dc):
        if not self._imgProxy.IsOk():
            return

        sectRect = self.__SectRectToClientRect()

        # draw main rectangle
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        iRect = wx.Rect(sectRect.GetPosition(), sectRect.GetSize())
        dc.SetPen(wx.WHITE_PEN)
        iRect.Inflate(1, 1)
        dc.DrawRectangle(iRect)

        # draw rule of thirds guides
        ss = sectRect.GetSize()
        dc.DrawRectangle(wx.Rect(sectRect.GetPosition() + wx.Size((0, ss[1] / 3)), wx.Size((ss[0], ss[1] / 3))))
        dc.DrawRectangle(wx.Rect(sectRect.GetPosition() + wx.Size((ss[0] / 3, 0)), wx.Size((ss[0] / 3, ss[1]))))

        # draw background
        color = wx.Colour(0, 0, 0, 153)
        dc.SetBrush(wx.Brush(color))
        dc.SetPen(wx.TRANSPARENT_PEN)  # wx.Pen(color))
        # left
        left, top = self.__GetBmpTopLeft()
        bmpWidth, bmpHeight = self._imgProxy.GetCurrentSize()
        dc.DrawRectangle(left, top, iRect.x - left, bmpHeight)
        lWidth = left + bmpWidth - iRect.GetWidth() - iRect.x
        left = iRect.x + iRect.GetWidth()
        dc.DrawRectangle(left, top, lWidth, bmpHeight)
        dc.DrawRectangle(iRect.x, top, iRect.GetWidth(), iRect.y - top)
        dc.DrawRectangle(iRect.x, iRect.y + iRect.GetHeight(),
                         iRect.GetWidth(),
                         top + bmpHeight - iRect.GetHeight() - iRect.y)

        now = time.time()
        alpha = 255
        if now - self._lastRectUpdate > self.INFO_TIME_OUT // 2:
            alpha = (1 - ((now - self._lastRectUpdate) - (self.INFO_TIME_OUT // 2)) / (self.INFO_TIME_OUT // 2)) * 255
            alpha = int(round(alpha))
        if alpha < 0:
            alpha = 0
        dc.SetTextForeground(wx.Colour(255, 255, 255, alpha))
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        font.SetPointSize(16)
        font.SetWeight(wx.BOLD)
        dc.SetFont(font)
        dc.SetPen(wx.WHITE_PEN)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle(sectRect)
        dc.DrawLabel("%d, %d - %d x %d" % tuple(self._sectRect),
                     sectRect,
                     wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)

    def OnPaint(self, event):
        sz = self.GetClientSize()

        pdc = wx.BufferedPaintDC(self)
        try:
            dc = wx.GCDC(pdc)
        except Exception:
            dc = pdc

        isModalDialogShown = False
        for win in wx.GetTopLevelWindows():
            if isinstance(win, wx.Dialog) and win.IsModal():
                isModalDialogShown = True
                break

        dc.SetBrush(wx.BLACK_BRUSH)
        dc.DrawRectangle(0, 0, sz[0], sz[1])
        if not self.IsEnabled() and not isModalDialogShown:
            # a modal dialog set this window to disabled (not enabled), but
            # this windows is set to disabled if no selection can
            # be made (multiple selected images)
            # this rectangle should only be drawn if this windows is set to
            # disabled programmatically and not when a modal dialog is shown
            dc.SetBrush(wx.Brush(wx.Colour(90, 90, 90, 255),
                                 wx.HORIZONTAL_HATCH))
            dc.DrawRectangle(0, 0, sz[0], sz[1])
        elif self._imgProxy is not None:
            self.__DrawBitmap(dc)
            self.__DrawSection(dc)

        event.Skip()

    def __UpdateSectRect(self):
        self._lastRectUpdate = time.time()
        if not self._infoTimer.IsRunning():
            self._infoTimer.Start(50)
        self.Refresh()

    def OnInfoTimer(self, event):
        if (time.time() - self._lastRectUpdate) > self.INFO_TIME_OUT:
            self._infoTimer.Stop()
#        iRect = self.__SectRectToClientRect()
#        iRect.Inflate((220 - iRect.GetWidth()) / 2, (50 - iRect.GetHeight()) / 2)
#        self.RefreshRect(iRect)
        self.Refresh()
        event.Skip()

    def __ClientToImage(self, px, py):
        bmpLeft, bmpTop = self.__GetBmpTopLeft()
        nx = int(round((px - bmpLeft) / self._zoom))
        ny = int(round((py - bmpTop) / self._zoom))
        return nx, ny

    def __FindPosition(self, cpx, cpy):
        tlx, tly = self._sectRect.GetTopLeft().Get()
        brx, bry = self._sectRect.GetBottomRight().Get()

        # first Check the Corners
        # topleft
        if abs(cpx - tlx) < self.BORDER_TOLERANCE and abs(cpy - tly) < self.BORDER_TOLERANCE:
            return self.POSITION_TOP | self.POSITION_LEFT
        # topright
        elif abs(cpx - brx) < self.BORDER_TOLERANCE and abs(cpy - tly) < self.BORDER_TOLERANCE:
            return self.POSITION_TOP | self.POSITION_RIGHT
        # bottom left
        elif abs(cpx - tlx) < self.BORDER_TOLERANCE and abs(cpy - bry) < self.BORDER_TOLERANCE:
            return self.POSITION_BOTTOM | self.POSITION_LEFT
        # bottom right
        elif abs(cpx - brx) < self.BORDER_TOLERANCE and abs(cpy - bry) < self.BORDER_TOLERANCE:
            return self.POSITION_BOTTOM | self.POSITION_RIGHT

        # then the Borders
        # left
        elif abs(cpx - tlx) < self.BORDER_TOLERANCE and (tly < cpy < bry):
            return self.POSITION_LEFT
        # right
        elif abs(cpx - brx) < self.BORDER_TOLERANCE and (tly < cpy < bry):
            return self.POSITION_RIGHT
        # top
        elif abs(cpy - tly) < self.BORDER_TOLERANCE and (tlx < cpx < brx):
            return self.POSITION_TOP
        # bottom
        elif abs(cpy - bry) < self.BORDER_TOLERANCE and (tlx < cpx < brx):
            return self.POSITION_BOTTOM

        elif self._sectRect.Contains(cpx, cpy):
            return self.POSITION_INSIDE
        else:
            return None

    def __SelectCursor(self, position):
        # the cornsers
        if position == self.POSITION_TOP | self.POSITION_LEFT:
            self.SetCursor(cursors.GetNW())
        elif position == self.POSITION_BOTTOM | self.POSITION_RIGHT:
            self.SetCursor(cursors.GetSE())
        elif position == self.POSITION_BOTTOM | self.POSITION_LEFT:
            self.SetCursor(cursors.GetSW())
        elif position == self.POSITION_TOP | self.POSITION_RIGHT:
            self.SetCursor(cursors.GetNE())

        # the Borders
        elif position in [self.POSITION_LEFT, self.POSITION_RIGHT]:
            self.SetCursor(wx.Cursor(wx.CURSOR_SIZEWE))
        elif position in [self.POSITION_TOP, self.POSITION_BOTTOM]:
            self.SetCursor(wx.Cursor(wx.CURSOR_SIZENS))

        elif position == self.POSITION_INSIDE:
            self.SetCursor(cursors.GetMOVE())
        else:
            self.SetCursor(wx.Cursor(wx.CURSOR_ARROW))

    def OnCaptureLost(self, event):  # pylint: disable=unused-argument
        if self._action is not None:
            self.__SelectCursor(None)
        self._action = None
        self._startX = None
        self._startY = None

    def OnLeftDown(self, event):
        if not self._imgProxy.IsOk():
            return
        px, py = event.GetPosition().Get()
        cpx, cpy = self.__ClientToImage(px, py)

        self._action = self.__FindPosition(cpx, cpy)
        if self._action is not None:
            self.CaptureMouse()
            self._startX = cpx
            self._startY = cpy
            self._startRect = wx.Rect(*self._sectRect.Get())

        event.Skip()

    def OnMotion(self, event):
        if not self._imgProxy.IsOk():
            return

        px, py = event.GetPosition().Get()
        cpx, cpy = self.__ClientToImage(px, py)
        if self._action is None:
            position = self.__FindPosition(cpx, cpy)
            self.__SelectCursor(position)
        else:
            if self._action == self.POSITION_INSIDE:
                deltaX = cpx - self._startX
                deltaY = cpy - self._startY

                self._sectRect.SetX(self._startRect.GetX() + deltaX)
                self._sectRect.SetY(self._startRect.GetY() + deltaY)

            else:
                # calculate dx aka delta x
                if self._action & self.POSITION_LEFT:
                    dx = self._startX - cpx
                elif self._action & self.POSITION_RIGHT:
                    dx = cpx - self._startX
                else:
                    dx = None

                # calculate dy aka delta y
                if self._action & self.POSITION_TOP:
                    dy = self._startY - cpy
                elif self._action & self.POSITION_BOTTOM:
                    dy = cpy - self._startY
                else:
                    dy = None

                # choose which one to use
                if dy is None or (dx is not None and dx > dy * self.RATIO):
                    width = self._startRect.GetWidth() + dx
                    height = width / self.RATIO
                    dy = dx / self.RATIO
                else:
                    height = self._startRect.GetHeight() + dy
                    width = height * self.RATIO
                    dx = dy * self.RATIO

                # check size
                recalcDelta = False
                if width < 100:
                    width = 100
                    height = width / self.RATIO
                    recalcDelta = True
                else:
                    if width > self._imgProxy.GetWidth() and self._lock:
                        width = self._imgProxy.GetWidth()
                        height = width / self.RATIO
                        recalcDelta = True
                    if height > self._imgProxy.GetHeight() and self._lock:
                        height = self._imgProxy.GetHeight()
                        width = height * self.RATIO
                        recalcDelta = True

                if recalcDelta:
                    dx = width - self._startRect.GetWidth()
                    dy = height - self._startRect.GetHeight()

                # now that we have the width and height, find out the position

                sx = self._startRect.GetX()
                sy = self._startRect.GetY()

                # we need an algorithm for this
                if self._action == self.POSITION_TOP | self.POSITION_LEFT:
                    nx = sx - dx
                    ny = sy - dy
                elif self._action == self.POSITION_TOP | self.POSITION_RIGHT:
                    nx = sx
                    ny = sy - dy
                elif self._action == self.POSITION_BOTTOM | self.POSITION_RIGHT:
                    nx = sx
                    ny = sy
                elif self._action == self.POSITION_BOTTOM | self.POSITION_LEFT:
                    nx = sx - dx
                    ny = sy
                elif self._action == self.POSITION_LEFT:
                    nx = sx - dx
                    ny = sy - dy / 2
                elif self._action == self.POSITION_RIGHT:
                    nx = sx
                    ny = sy - dy / 2
                elif self._action == self.POSITION_TOP:
                    nx = sx - dx / 2
                    ny = sy - dy
                elif self._action == self.POSITION_BOTTOM:
                    nx = sx - dx / 2
                    ny = sy

                # check pos
                if self._lock:
                    if nx < 0:
                        nx = 0
                    elif nx + width > self._imgProxy.GetWidth():
                        nx = self._imgProxy.GetWidth() - width

                    if ny < 0:
                        ny = 0
                    elif ny + height > self._imgProxy.GetHeight():
                        ny = self._imgProxy.GetHeight()

                # everything should be ok now
                self._sectRect.SetX(int(round(nx)))
                self._sectRect.SetY(int(round(ny)))
                self._sectRect.SetWidth(int(round(width)))
                self._sectRect.SetHeight(int(round(height)))
#
            self._SendRectChangedEvent()

            self.__UpdateSectRect()

    def OnLeftUp(self, event):
        if self._action is not None:
            px, py = event.GetPosition().Get()
            cpx, cpy = self.__ClientToImage(px, py)
            position = self.__FindPosition(cpx, cpy)
            self.__SelectCursor(position)
            if self.HasCapture():
                self.ReleaseMouse()
        self._action = None
        self._startX = None
        self._startY = None

        event.Skip()

    def _SendRectChangedEvent(self, checkImageDimensionLock=False):
        if not self._imgProxy.IsOk():
            return
        self.__KeepRectInImage()
        evt = RectChangedEvent(self.GetId(), self._sectRect)
        evt.SetCheckImageDimensionLock(checkImageDimensionLock)
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)

    def OnMouseWheel(self, event):
        rotation = event.GetWheelRotation()

        step = 20
        if rotation > 0:
            self._sectRect.Inflate(step, int(round(step / self.RATIO)))
        else:
            self._sectRect.Inflate(-step, -int(round(step / self.RATIO)))

        self._SendRectChangedEvent()
        self.__UpdateSectRect()

    def OnResize(self, event):
        if self._imgProxy is not None:
            self.__Scale()
            self.Refresh()
        event.Skip()

    def OnKeyDown(self, event):
        key = event.GetKeyCode()
        step = 20
        if key == wx.WXK_NUMPAD_ADD:
            self._sectRect.Inflate(step, int(round(step / self.RATIO)))
        elif key == wx.WXK_NUMPAD_SUBTRACT:
            self._sectRect.Inflate(-step, -int(round(step / self.RATIO)))
        elif key == wx.WXK_NUMPAD_DIVIDE:
            width = 1280
            self._sectRect.SetWidth(width)
            self._sectRect.SetHeight(int(round(width / self.RATIO)))
        elif key == wx.WXK_NUMPAD_MULTIPLY:
            self._sectRect = wx.Rect(0, 0, self._imgProxy.GetWidth(), int(round(self._imgProxy.GetWidth() / self.RATIO)))
        elif key == wx.WXK_LEFT:
            if event.ShiftDown():
                self._sectRect.Offset(-50, 0)
            else:
                self._sectRect.Offset(-10, 0)
        elif key == wx.WXK_UP:
            if event.ShiftDown():
                self._sectRect.Offset(0, -50)
            else:
                self._sectRect.Offset(0, -10)
        elif key == wx.WXK_RIGHT:
            if event.ShiftDown():
                self._sectRect.Offset(50, 0)
            else:
                self._sectRect.Offset(10, 0)
        elif key == wx.WXK_DOWN:
            if event.ShiftDown():
                self._sectRect.Offset(0, 50)
            else:
                self._sectRect.Offset(0, 10)
        elif event.GetModifiers() == wx.MOD_CONTROL and key == ord('C'):
            self.OnCopy(event)
        elif event.GetModifiers() == wx.MOD_CONTROL and key == ord('V'):
            self.OnPaste(event)
        else:
            event.Skip()
            return

        self._SendRectChangedEvent()
        self.__UpdateSectRect()

    def __KeepRectInImage(self):
        if not self._imgProxy.IsOk():
            return

        left = self._sectRect.GetLeft()
        top = self._sectRect.GetTop()
        width = self._sectRect.GetWidth()
        height = self._sectRect.GetHeight()

        if self._lock:
            if width > self._imgProxy.GetWidth():
                width = self._imgProxy.GetWidth()
                height = int(round(width / self.RATIO))
            if height > self._imgProxy.GetHeight():
                height = self._imgProxy.GetHeight()
                width = int(round(height * self.RATIO))

            if left < 0:
                left = 0
            if left + width > self._imgProxy.GetWidth():
                left = self._imgProxy.GetWidth() - width

            if top < 0:
                top = 0
            if top + height > self._imgProxy.GetHeight():
                top = self._imgProxy.GetHeight() - height

        self._sectRect = wx.Rect(left, top, width, height)

    def OnCopy(self, event):
        data = "%d, %d - %d x %d" % tuple(self._sectRect)
        if wx.TheClipboard.Open():
            try:
                do = wx.TextDataObject()
                do.SetText(data)
                wx.TheClipboard.SetData(do)
            finally:
                wx.TheClipboard.Close()

    def OnPaste(self, event):
        if wx.TheClipboard.Open():
            try:
                do = wx.TextDataObject()
                data = None
                if wx.TheClipboard.GetData(do):
                    data = do.GetText()
                    sectData = re.findall(r"([-]?\d+), ([-]?\d+) - (\d+) x (\d+)", data)
                    if sectData:
                        sectData = sectData[0]
                        try:
                            rect = wx.Rect(int(sectData[0]), int(sectData[1]),
                                           int(sectData[2]), int(sectData[3]))
                            self._lock = False
                            self.SetSection(rect)
                            self._SendRectChangedEvent(checkImageDimensionLock=True)
                        except ValueError:
                            pass
            finally:
                wx.TheClipboard.Close()

# ============================

    def GetSection(self):
        return self._sectRect

    def SetSection(self, rect):
        self._sectRect = wx.Rect(rect.GetPosition(), rect.GetSize())
        self.Refresh()

    def SetLock(self, lock):
        self._lock = lock


class ScaleThread(threading.Thread):

    def __init__(self, picture, callbackOnDone):
        threading.Thread.__init__(self, name="reload %s" % picture.GetFilename())
        self._picture = picture
        self._abort = False
        self._callbackOnDone = callbackOnDone

    def Abort(self):
        self._abort = True

    def run(self):
        self._abort = False
        for __ in range(20):
            time.sleep(0.1)
            if self._abort:
                return

        pilImg = PILBackend.GetImage(self._picture)
        wxImg = wx.Image(PILBackend.ImageToStream(pilImg), wx.BITMAP_TYPE_JPEG)

        if not self._abort:
            self._callbackOnDone(wxImg)


class ImageProxy(Observable):

    def __init__(self):
        Observable.__init__(self)
        self._curThread = None

        self._picture = None
        self._wxImg = None
        self._wxBmp = None
        self._curSize = -1, -1

    def Destroy(self):
        if self._curThread:
            self._curThread.Abort()
            self._curThread.join()

    def IsOk(self):
        return self._picture is not None

    def OnThreadDone(self, img):
        self._wxImg = img
        wx.CallAfter(self.Notify)

    def SetPicture(self, picture):
        self._picture = picture
        if self._picture is not None:
            self._wxImg = ImageCache().GetImage(picture)

            if self._curThread is not None:
                self._curThread.Abort()

            self._curThread = ScaleThread(picture, self.OnThreadDone)
            self._curThread.start()

        self.Notify()

    def GetWidth(self):
        return self._picture.GetWidth()

    def GetHeight(self):
        return self._picture.GetHeight()

    def GetSize(self):
        return self.GetWidth(), self.GetHeight()

    def Scale(self, width, height):
        if not (width > 0 and height > 0):
            return
        img = self._wxImg.Scale(width, height)
        self._wxBmp = img.ConvertToBitmap()
        self._curSize = width, height

    def GetCurrentSize(self):
        return self._curSize

    def GetBitmap(self):
        return  self._wxBmp
