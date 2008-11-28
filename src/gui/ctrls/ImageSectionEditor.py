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

import time

import wx


EVT_RECT_CHANGED_TYPE  = wx.NewEventType()
EVT_RECT_CHANGED       = wx.PyEventBinder(EVT_RECT_CHANGED_TYPE, 1)


class RectChangedEvent(wx.PyCommandEvent):
    def __init__(self, wxId, rect):
        wx.PyCommandEvent.__init__(self, EVT_RECT_CHANGED_TYPE, wxId)
        self._rect = rect

    def GetRect(self):
        return self._rect


class ImageSectionEditor(wx.Panel):
    
    BORDER_TOLERANCE = 20
    
    POSITION_INSIDE  = 0x01
    
    POSITION_TOP     = 0x10
    POSITION_BOTTOM  = 0x20
    POSITION_LEFT    = 0x40
    POSITION_RIGHT   = 0x80
    
    INFO_TIME_OUT    = 2.0
    
    RATIO = 16.0 / 9.0
            
    
    def __init__(self, parent, id=wx.ID_ANY, 
                 pos=wx.DefaultPosition, size=wx.DefaultSize, 
                 style=wx.TAB_TRAVERSAL, name='panel'):
        wx.Panel.__init__(self, parent, id, pos, size, style, name)
        
        self.SetMinSize(wx.Size(400, 300))
        self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        self._image     = None
        self._bmpScaled = None
        self._sectRect  = wx.Rect(0, 0, 1280, 720)
        self._zoom      = 1
        self._infoTimer = wx.Timer(self)
        self._lastRectUpdate = 0
        
        self._action    = None
        self._startX    = None
        self._startY    = None
        self._startRect = None
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_TIMER, self.OnInfoTimer)

    def SetBitmap(self, bmp):
        if bmp is None:
            self._image = None
        else:
            self._image = bmp.ConvertToImage()
            self.__Scale()
            self.__KeepRectInImage()
        self.Refresh()
    
    def __Scale(self):
        if self._image is None:
            return

        cw, ch = self.GetClientSize().Get()
        iw, ih = self._image.GetSize().Get()
        rx = float(cw) / float(iw)
        ry = float(ch) / float(ih)
        
        newWidth = cw
        newHeight = ih * rx
        self._zoom = rx
        
        if newHeight > ch:
            newHeight = ch
            newWidth = iw * ry
            self._zoom = ry 
        
        img = self._image.Scale(newWidth, newHeight)
        self._bmpScaled = img.ConvertToBitmap()
        
    def __DrawBitmap(self, dc):
        if self._image is not None:
            left, top = self.__GetBmpTopLeft()
            dc.DrawBitmap(self._bmpScaled, left, top)
            
    def __GetBmpTopLeft(self):
        if self._bmpScaled is None:
            return 0, 0
        cw, ch = self.GetClientSize().Get()
        iw, ih = self._bmpScaled.GetSize().Get()
        left = (cw - iw) / 2.0
        top = (ch - ih) / 2.0
        return int(left), int(top)
    
    def __SectRectToClientRect(self):
        left, top = self.__GetBmpTopLeft()
        sectRect = wx.Rect(left + (self._sectRect.GetLeft() * self._zoom),
                           top + (self._sectRect.GetTop() * self._zoom),
                           self._sectRect.GetWidth() * self._zoom,
                           self._sectRect.GetHeight() * self._zoom)
        return sectRect
            
    def __DrawSection(self, dc):
        if self._image is None:
            return
        
        sectRect = self.__SectRectToClientRect()
        
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        iRect = wx.RectPS(sectRect.GetPosition(), sectRect.GetSize())
        for i in range(5):
            if i < 2:
                dc.SetPen(wx.WHITE_PEN)
            else:
                dc.SetPen(wx.Pen(wx.Colour(0, 0, 0, 255 / i )))
            iRect.Inflate(1, 1)
            dc.DrawRectangleRect(iRect)

        now = time.time()
        alpha = 255
        if now - self._lastRectUpdate > self.INFO_TIME_OUT / 2:
            alpha = (1 - ((now - self._lastRectUpdate) - (self.INFO_TIME_OUT / 2)) / (self.INFO_TIME_OUT / 2)) * 255
        if alpha < 0:
            alpha = 0
        dc.SetTextForeground(wx.Colour(255, 255, 255, alpha))
        font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FIXED_FONT)
        font.SetPointSize(16)
        font.SetWeight(wx.BOLD)
        dc.SetFont(font)
        dc.SetPen(wx.WHITE_PEN)
        dc.DrawRectangleRect(sectRect)
        dc.DrawLabel("%d, %d - %d x %d" % tuple(self._sectRect), 
                     sectRect,
                     wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)

    def OnPaint(self, event):
        sz = self.GetClientSize()

        pdc = wx.BufferedPaintDC(self)
        try:
            dc = wx.GCDC(pdc)
        except StandardError:
            dc = pdc

        dc.SetBrush(wx.GREY_BRUSH)
        dc.DrawRectangle(0, 0, sz[0], sz[1])
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
        nx = (px - bmpLeft) / self._zoom
        ny = (py - bmpTop) / self._zoom
        return nx, ny

    def __FindPosition(self, cpx, cpy):
        tlx, tly = self._sectRect.GetTopLeft().Get()
        brx, bry = self._sectRect.GetBottomRight().Get()
            
        #first Check the Corners
        #topleft
        if abs(cpx - tlx) < self.BORDER_TOLERANCE and abs(cpy - tly) < self.BORDER_TOLERANCE:
            return self.POSITION_TOP | self.POSITION_LEFT
        #topright
        elif abs(cpx - brx) < self.BORDER_TOLERANCE and abs(cpy - tly) < self.BORDER_TOLERANCE:
            return self.POSITION_TOP | self.POSITION_RIGHT
        #bottom left
        elif abs(cpx - tlx) < self.BORDER_TOLERANCE and abs(cpy - bry) < self.BORDER_TOLERANCE:
            return self.POSITION_BOTTOM | self.POSITION_LEFT
        #bottom right
        elif abs(cpx - brx) < self.BORDER_TOLERANCE and abs(cpy - bry) < self.BORDER_TOLERANCE:
            return self.POSITION_BOTTOM | self.POSITION_RIGHT
        
        #then the Borders
        #left
        elif abs(cpx - tlx) < self.BORDER_TOLERANCE and (tly < cpy < bry):
            return self.POSITION_LEFT
        #right
        elif abs(cpx - brx) < self.BORDER_TOLERANCE and (tly < cpy < bry):
            return self.POSITION_RIGHT
        #top
        elif abs(cpy - tly) < self.BORDER_TOLERANCE and (tlx < cpx < brx):
            return self.POSITION_TOP
        #bottom
        elif abs(cpy - bry) < self.BORDER_TOLERANCE and (tlx < cpx < brx):
            return self.POSITION_BOTTOM            
        
        elif self._sectRect.ContainsXY(cpx, cpy):
            return self.POSITION_INSIDE
        else:                
            return None

    def __SelectCursor(self, position):
        #the cornsers
        if position in [self.POSITION_TOP | self.POSITION_LEFT, self.POSITION_BOTTOM | self.POSITION_RIGHT]:
            self.SetCursor(wx.StockCursor(wx.CURSOR_SIZENWSE))
        elif position in [self.POSITION_BOTTOM | self.POSITION_LEFT, self.POSITION_TOP | self.POSITION_RIGHT]:
            self.SetCursor(wx.StockCursor(wx.CURSOR_SIZENESW))
        
        #the Borders
        if position in [self.POSITION_LEFT, self.POSITION_RIGHT]:
            self.SetCursor(wx.StockCursor(wx.CURSOR_SIZEWE))
        elif position in [self.POSITION_TOP, self.POSITION_BOTTOM]:
            self.SetCursor(wx.StockCursor(wx.CURSOR_SIZENS))
        
        elif position == self.POSITION_INSIDE:
            self.SetCursor(wx.StockCursor(wx.CURSOR_SIZING))
        else:                
            self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
            
    def OnLeftDown(self, event):
        if self._image is None:
            return
        px, py = event.GetPosition().Get()
        cpx, cpy = self.__ClientToImage(px, py)

        self._action = self.__FindPosition(cpx, cpy)
        if self._action is not None:
            self._startX = cpx
            self._startY = cpy
            self._startRect = wx.Rect(*self._sectRect.Get())

        event.Skip()
    
    def OnMotion(self, event):
        if self._image is None:
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
                                
            elif self._action == self.POSITION_TOP | self.POSITION_LEFT:
                deltaX = cpx - self._startX
                deltaY = cpy - self._startY
                
                if deltaX < deltaY:
                    self._sectRect.Set(self._startRect.GetLeft() + deltaX,
                                   self._startRect.GetTop() + deltaX / self.RATIO,
                                   self._startRect.GetWidth() - deltaX,
                                   self._startRect.GetHeight() - deltaX / self.RATIO)
                else:
                    self._sectRect.Set(self._startRect.GetLeft() + deltaY * self.RATIO,
                                   self._startRect.GetTop() + deltaY,
                                   self._startRect.GetWidth() - deltaY * self.RATIO,
                                   self._startRect.GetHeight() - deltaY)
                                  
            elif self._action == self.POSITION_TOP:
                delta = cpy - self._startY

                #prevent top from getting lower then bottom
                maxDelta = self._startRect.GetBottom() - self._startRect.GetTop() - 5
                if delta > maxDelta:
                    delta = maxDelta            
                
                self._sectRect.Set(self._startRect.GetLeft() + delta * self.RATIO / 2,
                                   self._startRect.GetTop() + delta,
                                   self._startRect.GetWidth() - delta * self.RATIO,
                                   self._startRect.GetHeight() - delta)

            elif self._action == self.POSITION_BOTTOM:
                delta = cpy - self._startY
                
                #prevent bottom from getting higher then top
                minDelta = self._startRect.GetTop() - self._startRect.GetBottom() + 5
                if delta < minDelta:
                    delta = minDelta
                
                self._sectRect.Set(self._startRect.GetLeft() - delta * self.RATIO / 2,
                                   self._startRect.GetTop(),
                                   self._startRect.GetWidth() + delta * self.RATIO,
                                   self._startRect.GetHeight() + delta)
                
            elif self._action == self.POSITION_LEFT:
                delta = cpx - self._startX
                
                #prevent left from getting more righter then right
                maxDelta = self._startRect.GetRight() - self._startRect.GetLeft() - 5
                if delta > maxDelta:
                    delta = maxDelta
                
                self._sectRect.Set(self._startRect.GetLeft() + delta,
                                   self._startRect.GetTop() + delta / self.RATIO / 2,
                                   self._startRect.GetWidth() - delta,
                                   self._startRect.GetHeight() - delta / self.RATIO)
            elif self._action == self.POSITION_RIGHT:
                delta = cpx - self._startX
                
                #prevent right from getting more left then left
                minDelta = self._startRect.GetLeft() - self._startRect.GetRight() + 5
                if delta < minDelta:
                    delta = minDelta
                
                self._sectRect.Set(self._startRect.GetLeft(),
                                   self._startRect.GetTop() - delta / self.RATIO / 2,
                                   self._startRect.GetWidth() + delta,
                                   self._startRect.GetHeight() + delta / self.RATIO)
                

#           
            #TODO: andere Actions handhaben
            
            self._SendRectChangedEvent()
            
            self.__UpdateSectRect()

    def OnLeftUp(self, event):
        if self._action is not None:
            px, py = event.GetPosition().Get()
            cpx, cpy = self.__ClientToImage(px, py)
            position = self.__FindPosition(cpx, cpy)
            self.__SelectCursor(position)
        self._action = None
        self._startX = None
        self._startY = None
        
        event.Skip()
            
    def _SendRectChangedEvent(self):
        if self._image is None:
            return
        self.__KeepRectInImage()
        evt = RectChangedEvent(self.GetId(), self._sectRect)
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)        
            
    def OnMouseWheel(self, event):
        rotation = event.GetWheelRotation()
        
        if rotation > 0: 
            self._sectRect.Inflate(16, 9)
        else:
            self._sectRect.Inflate(-16, -9)
        
        self._SendRectChangedEvent()
        self.__UpdateSectRect()
            
    def OnResize(self, event):
        self.__Scale()
        self.Refresh()
        event.Skip()

    def OnKeyDown(self, event):
        key = event.GetKeyCode()
        if key == wx.WXK_NUMPAD_ADD:
            self._sectRect.Inflate(16, 9)
        elif key == wx.WXK_NUMPAD_SUBTRACT:
            self._sectRect.Inflate(-16, -9)
        elif key == wx.WXK_NUMPAD_DIVIDE:
            self._sectRect.SetWidth(1280)
            self._sectRect.SetHeight(720)
        elif key == wx.WXK_NUMPAD_MULTIPLY:
            self._sectRect = wx.Rect(0, 0, self._image.GetWidth(), self._image.GetWidth() / self.RATIO)
        elif key == wx.WXK_LEFT:
            if event.ShiftDown():
                self._sectRect.OffsetXY(-50, 0)
            else:
                self._sectRect.OffsetXY(-10, 0)
        elif key == wx.WXK_UP:
            if event.ShiftDown():
                self._sectRect.OffsetXY(0, -50)
            else:
                self._sectRect.OffsetXY(0, -10)
        elif key == wx.WXK_RIGHT:
            if event.ShiftDown():
                self._sectRect.OffsetXY(50, 0)
            else:
                self._sectRect.OffsetXY(10, 0)
        elif key == wx.WXK_DOWN:
            if event.ShiftDown():
                self._sectRect.OffsetXY(0, 50)
            else:
                self._sectRect.OffsetXY(0, 10)
        else:
            event.Skip()
            return
        
        self._SendRectChangedEvent()
        self.__UpdateSectRect()
            
    def __KeepRectInImage(self):
        if self._image is None:
            return
        
        left = self._sectRect.GetLeft()
        top = self._sectRect.GetTop()
        width = self._sectRect.GetWidth()
        height = self._sectRect.GetHeight()
        
        if width > self._image.GetWidth():
            width = self._image.GetWidth()
            height = width / RATIO
        if height > self._image.GetHeight():
            height = self._image.GetHeight()
            width = height / RATIO

        if left < 0:
            left = 0
        if left + width > self._image.GetWidth():
            left = self._image.GetWidth() - width

        if top < 0:
            top = 0
        if top + height > self._image.GetHeight():
            top = self._image.GetHeight() - height
            
        self._sectRect = wx.Rect(left, top, width, height)
        
# ============================

    def GetSection(self):
        return self._sectRect
    
    def SetSection(self, rect):
        self._sectRect = wx.RectPS(rect.GetPosition(), rect.GetSize())
        self._SendRectChangedEvent()
        self.Refresh()
    
    def GetImage(self):
        return self._image
    
          