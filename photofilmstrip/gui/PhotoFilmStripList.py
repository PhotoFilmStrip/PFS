# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import os

import wx

from photofilmstrip.gui.util.ImageCache import ImageCache, EVT_THUMB_READY
from photofilmstrip.gui.helper import ChopText

EVT_CHANGED_TYPE = wx.NewEventType()
EVT_CHANGED = wx.PyEventBinder(EVT_CHANGED_TYPE, 1)


class ChangedEvent(wx.PyCommandEvent):

    def __init__(self, wxId):
        wx.PyCommandEvent.__init__(self, EVT_CHANGED_TYPE, wxId)


class PhotoFilmStripList(wx.ScrolledWindow):

    GAP = 10
    BORDER = 45
    THUMB_HEIGHT = 120
    HOLE_WIDTH = 11
    HOLE_HEIGHT = 16
    HOLE_PADDING = 13  # distance between holes
    HOLE_MARGIN = 6  # distance to thumb
    LABEL_MARGIN = 8

    STRIP_HEIGHT = THUMB_HEIGHT + 2 * BORDER

    def __init__(self, parent, id=-1,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=wx.HSCROLL | wx.VSCROLL, name='PhotoFilmStripList'):
        wx.ScrolledWindow.__init__(self, parent, id, pos, size, style, name)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetBackgroundColour(wx.BLACK)
        clientSize = wx.Size(-1, self.STRIP_HEIGHT + wx.SystemSettings.GetMetric(wx.SYS_HSCROLL_Y))
        self.SetSizeHints(clientSize, clientSize)

        self.__frozen = False
        self.__pictures = []
        self.__selIdxs = []
        self.__hvrIdx = -1

        self.__dragIdx = None
        self.__dropIdx = None
        self.__dragBmp = None
        self.__dragBmpIdx = None
        self.__dragX = 0
        self.__dragOffX = 0

        self.__UpdateVirtualSize()

        self.SetScrollRate(1, 0)

        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvent)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.OnCaptureLost)

        ImageCache().RegisterWin(self)
        ImageCache().thumb = wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE,
              wx.ART_TOOLBAR, (120, 120))
        self.Bind(EVT_THUMB_READY, self.__OnThumbReady)

    def Freeze(self, *args):
        self.__frozen = True

    def Thaw(self, *args):
        self.__frozen = False
        self.__UpdateVirtualSize()

    def IsFrozen(self, *args):
        return self.__frozen

    def __OnThumbReady(self, event):
        self.__UpdateVirtualSize()

    def OnPaint(self, event):
        pdc = wx.BufferedPaintDC(self)
        try:
            dc = wx.GCDC(pdc)
        except Exception:
            dc = pdc

        dc.SetBackground(wx.BLACK_BRUSH)
        dc.Clear()

        vx = self.GetViewStart()[0]
        clientWidth = self.GetClientSize()[0]

        diaRect = wx.Rect(-vx, 0, 0, self.STRIP_HEIGHT)

        for idx, pic in enumerate(self.__pictures):
            bmp = ImageCache().GetThumbBmp(pic)

            # if the picture cannot be loaded GetWidth may return -1
            bmpWidth = bmp.GetWidth()

            diaRect.SetWidth(bmpWidth + self.GAP)

            if idx == self.__dropIdx and self.__dragIdx > idx:
                diaRect.Offset(self.__dragBmp.GetWidth(), 0)

            if diaRect.right + 1 >= 0 and idx != self.__dragIdx:
                if diaRect.left <= clientWidth:
                    label = os.path.splitext(os.path.basename(pic.GetFilename()))[0]
                    diaNo = idx + 1

                    if idx >= self.__dropIdx and idx < self.__dragIdx:
                        diaNo += 1

                    if idx <= self.__dropIdx and idx > self.__dragIdx:
                        diaNo -= 1

                    self.__DrawDia(dc, diaRect, diaRect.x + vx, bmp, str(diaNo), label, idx in self.__selIdxs, idx == self.__hvrIdx)
                else:
                    break

            if idx != self.__dragIdx or self.__dragIdx == self.__dropIdx:
                diaRect.Offset(diaRect.width, 0)

            if idx == self.__dropIdx and self.__dragIdx < idx:
                diaRect.Offset(self.__dragBmp.GetWidth(), 0)

        if self.__dragIdx is not None:
            dc.DrawBitmap(self.__dragBmp, self.__dragX - self.__dragOffX - vx, 0, True)

    def __CreateDiaBmp(self, picIdx, selected=False, highlighted=False, dropIdx=None):
        pic = self.__pictures[picIdx]
        thumbBmp = ImageCache().GetThumbBmp(pic)
        diaRect = self.GetDiaRect(picIdx)
        holeOffset = diaRect.x

        bmp = wx.Bitmap(diaRect.width, diaRect.height)
        diaNo = str(picIdx + 1)
        label = os.path.splitext(os.path.basename(pic.GetFilename()))[0]

        dc = wx.MemoryDC(bmp)
        try:
            dc = wx.GCDC(dc)
        except Exception:
            pass

        if dropIdx is not None:
            diaNo = str(dropIdx + 1)
            dropRect = self.GetDiaRect(dropIdx)

            if dropIdx > picIdx:
                holeOffset = dropRect.right + 1 - diaRect.width

        diaRect.SetX(0)
        self.__DrawDia(dc, diaRect, holeOffset, thumbBmp, diaNo, label, selected, highlighted)
        return bmp

    def __DrawDia(self, dc, rect, holeOffset, thumbBmp, diaNo, label, selected=False, highlighted=False):
        font = wx.SystemSettings.GetFont(wx.SYS_ANSI_FIXED_FONT)
        font.SetPointSize(9)
        dc.SetFont(font)

        colour = wx.Colour(235, 235, 235)

        bmpX = rect.x + self.GAP / 2
        bmpY = (rect.height - thumbBmp.GetHeight()) / 2

        holeX = rect.x + self.GAP / 2 - (holeOffset % (self.HOLE_WIDTH + self.HOLE_PADDING))

        dc.SetClippingRegion(rect.GetX(), rect.GetY(), rect.GetWidth(), rect.GetHeight())

        if selected:
            dc.SetBackground(wx.Brush(wx.Colour(38, 54, 70)))
            dc.Clear()
            dc.SetPen(wx.Pen(wx.Colour(237, 156, 0)))
            dc.SetBrush(wx.Brush(wx.Colour(237, 156, 0)))
            dc.DrawRectangle(rect.x, 0, rect.right + 1, 3)
            dc.DrawRectangle(rect.x, rect.bottom - 2, rect.right + 1, rect.bottom)
        else:
            dc.SetBackground(wx.BLACK_BRUSH)
            dc.Clear()

        dc.SetTextForeground(wx.Colour(237, 156, 0))
        dc.SetBrush(wx.Brush(colour))
        dc.SetPen(wx.Pen(colour))

        diaNoWidth, textHeight = dc.GetTextExtent(diaNo)
        label, labelWidth = ChopText(dc, label, thumbBmp.GetWidth())

        dc.DrawBitmap(thumbBmp, bmpX, bmpY, True)
        dc.DrawText(diaNo, rect.x + (rect.width - diaNoWidth) / 2, self.LABEL_MARGIN - 3)
        dc.DrawText(label, rect.x + (rect.width - labelWidth) / 2, rect.height - self.LABEL_MARGIN - textHeight)

        while holeX <= rect.right + 1:
            dc.DrawRoundedRectangle(holeX, self.BORDER - self.HOLE_MARGIN - self.HOLE_HEIGHT, self.HOLE_WIDTH, self.HOLE_HEIGHT, 2)
            dc.DrawRoundedRectangle(holeX, self.BORDER + self.THUMB_HEIGHT + self.HOLE_MARGIN, self.HOLE_WIDTH, self.HOLE_HEIGHT, 2)
            holeX += self.HOLE_WIDTH + self.HOLE_PADDING

        if highlighted:
            dc.SetPen(wx.TRANSPARENT_PEN)
            dc.SetBrush(wx.Brush(wx.Colour(77, 136, 196, 80)))
            dc.DrawRectangle(rect)

        dc.DestroyClippingRegion()

    def _SendChangedEvent(self):
        evt = ChangedEvent(self.GetId())
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)

    def __Scroll(self, value):
        sp = self.GetScrollPos(wx.HORIZONTAL)
        self.Scroll(sp + value, -1)

    def OnMouseWheel(self, event):
        rot = event.GetWheelRotation()
        linesPer = 40  # event.GetLinesPerAction()
        if rot > 0:
            self.__Scroll(-linesPer)
        else:
            self.__Scroll(linesPer)

    def OnMouseEvent(self, event):
        mPos = event.GetPosition()
        unscrolledPos = self.CalcUnscrolledPosition(mPos)
        idx = self.HitTest(mPos)
        if event.Moving():
            if idx != self.__hvrIdx:
                self.__hvrIdx = idx
                self.Refresh()

        if event.Dragging():
            if idx != -1:
                self.__dropIdx = idx

            if mPos.x < 10:
                self.__Scroll(-40)
            elif mPos.x > self.GetClientSize()[0] - 10:
                self.__Scroll(40)

            self.__dragX = unscrolledPos.x
            if self.__dragIdx is None:
                if idx != -1:
                    self.__dragIdx = idx
                    self.__dragBmp = self.__CreateDiaBmp(idx, True, True)
                    self.__dragBmpIdx = idx
                    rect = self.GetDiaRect(idx)
                    self.__dragOffX = self.__dragX - rect.GetLeft()
                    self.CaptureMouse()

            elif self.__dragBmpIdx != self.__dropIdx:
                self.__dragBmpIdx = self.__dropIdx
                self.__dragBmp = self.__CreateDiaBmp(self.__dragIdx, True, True, self.__dropIdx)

            self.Refresh()

        if event.Leaving():
            self.__hvrIdx = -1
            self.Refresh()

        if event.LeftDown() and not event.Dragging():
            if idx != -1:
                if event.ControlDown():
                    self.Select(idx, idx not in self.__selIdxs, False)
                elif event.ShiftDown():
                    if not self.__selIdxs:
                        # nothing selected
                        self.Select(idx)
                    else:
                        step = 1 if idx > self.__selIdxs[0] else -1
                        for ct, _idx in enumerate(xrange(self.__selIdxs[0],
                                                         idx + step,
                                                         step)):
                            self.Select(_idx, deselectOthers=ct == 0)
                else:
                    self.Select(idx)

        if event.LeftUp() and self.__dragIdx is not None:
            self.__FinishDnD()

        event.Skip()

    def OnCaptureLost(self, event):
        self.__dragIdx = None
        self.__dropIdx = None
        self.Refresh()
        event.Skip()

    def OnKeyDown(self, event):
        if event.HasModifiers():
            event.Skip()
            return

        key = event.GetKeyCode()
        if self.__selIdxs:
            if event.ShiftDown():
                # if add to selection use last selected item as reference
                sel = self.__selIdxs[-1]
            else:
                sel = self.__selIdxs[0]
        else:
            sel = -1
        if key == wx.WXK_LEFT:
            if sel > 0:
                self.Select(sel - 1,
                            deselectOthers=not event.ShiftDown())
                self.EnsureVisible(sel - 1)

        elif key == wx.WXK_RIGHT:
            if sel < self.GetItemCount() - 1:
                self.Select(sel + 1,
                            deselectOthers=not event.ShiftDown())
                self.EnsureVisible(sel + 1)

        elif key == wx.WXK_END:
            self.Select(self.GetItemCount() - 1)
            self.EnsureVisible(self.GetItemCount() - 1)

        elif key == wx.WXK_HOME:
            self.Select(0)
            self.EnsureVisible(0)

        elif key == wx.WXK_ESCAPE:
            if self.__dragIdx is not None:
                self.__FinishDnD(abort=True)

        else:
            event.Skip()

    def __FinishDnD(self, abort=False):
        if self.__dragIdx is not None:
            if self.HasCapture():
                self.ReleaseMouse()

            idx = self.__dragIdx
            if not abort:
                self.MovePicture(self.__dragIdx, self.__dropIdx)
                self.Select(self.__dropIdx)
                idx = self.__dropIdx

            self.__dragIdx = None
            self.__dropIdx = None

            self.Refresh()
            self.EnsureVisible(idx)

    def EnsureVisible(self, idx):
        rect = self.GetDiaRect(idx)
        left = rect.GetLeft()
        vs = self.GetViewStart()[0]
        ch = self.GetClientSize()[0]
        if left < vs:
            self.Scroll(left, 0)
        elif left > vs + ch:
            self.Scroll(rect.GetRight() - ch, 0)

    def __UpdateVirtualSize(self):
        width = 0
        for pic in self.__pictures:
            bmp = ImageCache().GetThumbBmp(pic)
            # if the picture cannot be loaded GetWidth may return -1
            width += bmp.GetWidth() + self.GAP

        self.SetVirtualSize((width, self.STRIP_HEIGHT))
        self.Refresh()

    def GetThumbSize(self, pic):
        aspect = float(pic.GetWidth()) / float(pic.GetHeight())
        thumbHeight = self.THUMB_HEIGHT
        thumbWidth = int(round(thumbHeight * aspect))
        return thumbWidth, thumbHeight

    def GetDiaRect(self, idx):
        sx = 0
        for picIdx, pic in enumerate(self.__pictures):
            thumbWidth = ImageCache().GetThumbBmp(pic).GetWidth()

            if idx == picIdx:
                rect = wx.Rect(sx, 0, thumbWidth + self.GAP, self.STRIP_HEIGHT)
                return rect

            sx += thumbWidth + self.GAP

    def HitTest(self, pos):
        pos = self.CalcUnscrolledPosition(pos)
        sx = 0
        for idx, pic in enumerate(self.__pictures):
            thumbWidth = ImageCache().GetThumbBmp(pic).GetWidth()

            rect = wx.Rect(sx, 0, thumbWidth + self.GAP, self.STRIP_HEIGHT)
            if rect.Contains(pos):
                return idx

            sx += thumbWidth + self.GAP
        return -1

#    def AddPicture(self, pic):
#        self.__pictures.append(pic)
#        self.__UpdateVirtualSize()
#        self._SendChangedEvent()

    def InsertPicture(self, idx, pic):
        self.__pictures.insert(idx, pic)

        for i in xrange(len(self.__selIdxs)):
            if self.__selIdxs[i] >= idx \
            and self.__selIdxs[i] + 1 not in self.__selIdxs:
                self.__selIdxs[i] += 1

        if not self.IsFrozen():
            self.__UpdateVirtualSize()
        self._SendChangedEvent()

    def DeleteItem(self, idx):
        self.__pictures.pop(idx)

        firstSel = 0
        if self.__selIdxs:
            firstSel = self.__selIdxs[0]
        if firstSel >= len(self.__pictures):
            firstSel = len(self.__pictures) - 1

        if idx in self.__selIdxs:
            self.__selIdxs.remove(idx)

        if firstSel != idx \
        and firstSel not in self.__selIdxs:
            self.__selIdxs.insert(0, firstSel)

        if len(self.__selIdxs) == 0:
            self.__selIdxs.append(firstSel)

        for i in xrange(len(self.__selIdxs)):
            if self.__selIdxs[i] > idx \
            and self.__selIdxs[i] - 1 not in self.__selIdxs:
                self.__selIdxs[i] -= 1

        if len(self.__pictures) == 0:
            self.__selIdxs = []

        if self.__hvrIdx >= len(self.__pictures):
            self.__hvrIdx = -1

        self.__UpdateVirtualSize()
        self._SendChangedEvent()

        evt = wx.ListEvent(wx.EVT_LIST_ITEM_SELECTED.typeId, self.GetId())
        self.GetEventHandler().ProcessEvent(evt)

    def DeleteAllItems(self):
        self.__selIdxs = []
        self.__pictures = []
        self.__UpdateVirtualSize()
        self._SendChangedEvent()

    def GetItemCount(self):
        return len(self.__pictures)

    def GetPicture(self, idx):
        try:
            return self.__pictures[idx]
        except IndexError:
            return None

    def SetPicture(self, idx, pic):
        if idx in xrange(len(self.__pictures)):
            self.__pictures[idx] = pic
            self.Refresh()

    def GetPictures(self):
        return self.__pictures[:]

    def GetSelected(self):
        return self.__selIdxs[:]

    def GetSelectedPictures(self):
        selPics = []
        for idx in self.__selIdxs:
            pic = self.GetPicture(idx)
            if pic is not None:
                selPics.append(pic)
        return selPics

    def Select(self, idx, on=True, deselectOthers=True):
        if idx in xrange(len(self.__pictures)):
            if deselectOthers:
                newSel = []
            else:
                newSel = self.__selIdxs[:]
            if on and idx not in newSel:
                newSel.append(idx)
            elif not on and idx in newSel and len(newSel) > 1:
                # must have more than one selected item to make sure
                # there is at least one selected
                newSel.remove(idx)

            evt = None
            if newSel != self.__selIdxs:
                evt = wx.ListEvent(wx.EVT_LIST_ITEM_SELECTED.typeId, self.GetId())
#                evt.m_itemIndex = newSelIdx
#                evt.m_oldItemIndex = self.__selIdx

            self.__selIdxs = newSel
            self.Refresh()

            if evt:
                self.GetEventHandler().ProcessEvent(evt)
            return True
        else:
            return False

    def SwapPictures(self, idxFrom, idxTo):
        picFrom = self.__pictures[idxFrom]
        picTo = self.__pictures[idxTo]
        self.__pictures[idxFrom] = picTo
        self.__pictures[idxTo] = picFrom

        evt = None
        try:
            p = self.__selIdxs.index(idxFrom)
            self.__selIdxs[p] = idxTo
            evt = wx.ListEvent(wx.EVT_LIST_ITEM_SELECTED.typeId, self.GetId())
            evt.m_itemIndex = idxTo
            evt.m_oldItemIndex = idxFrom
        except ValueError:
            pass

        self.Refresh()
        self._SendChangedEvent()
        if evt:
            self.GetEventHandler().ProcessEvent(evt)

    def MovePicture(self, idxFrom, idxTo):
        pic = self.__pictures.pop(idxFrom)
        self.__pictures.insert(idxTo, pic)

        evt = None
        try:
            p = self.__selIdxs.index(idxFrom)
            self.__selIdxs[p] = idxTo
            evt = wx.ListEvent(wx.EVT_LIST_ITEM_SELECTED.typeId, self.GetId())
            evt.m_itemIndex = idxTo
            evt.m_oldItemIndex = idxFrom
        except ValueError:
            pass

        self.Refresh()
        self._SendChangedEvent()
        if evt:
            self.GetEventHandler().ProcessEvent(evt)


# FIXME: should be fixed height
ImageCache.THUMB_SIZE = PhotoFilmStripList.THUMB_HEIGHT
