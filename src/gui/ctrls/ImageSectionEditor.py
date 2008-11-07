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
    
    def __init__(self, parent, id=wx.ID_ANY, 
                 pos=wx.DefaultPosition, size=wx.DefaultSize, 
                 style=wx.TAB_TRAVERSAL, name='panel'):
        wx.Panel.__init__(self, parent, id, pos, size, style, name)
        
        self.SetMinSize(wx.Size(400, 300))
        self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        self._image    = None
        self._bmpScaled= None
        self._sectRect = wx.Rect(0, 0, 1280, 720)
        self._zoom     = 1
        
        self._deltaX   = None
        self._deltaY   = None 

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MOTION, self.OnMotion)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)
        self.Bind(wx.EVT_SIZE, self.OnResize)
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

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
            
    def __DrawSection(self, dc):
        if self._image is None:
            return
        
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        
        left, top = self.__GetBmpTopLeft()
        for i in range(5):
            if i < 2:
                dc.SetPen(wx.WHITE_PEN)
            else:
                dc.SetPen(wx.Pen(wx.Colour(0, 0, 0, 255 / i )))

            dc.DrawRectangle(left + (self._sectRect.GetLeft() * self._zoom) - i,
                             top + (self._sectRect.GetTop() * self._zoom) - i,
                             self._sectRect.GetWidth() * self._zoom + i*2,
                             self._sectRect.GetHeight() * self._zoom + i*2)

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
        
    def __ClientToImage(self, px, py):
        bmpLeft, bmpTop = self.__GetBmpTopLeft()
        nx = (px - bmpLeft) / self._zoom
        ny = (py - bmpTop) / self._zoom
        return nx, ny

    def OnLeftDown(self, event):
        px, py = event.GetPosition().Get()
        cpx, cpy = self.__ClientToImage(px, py)

        if self._sectRect.ContainsXY(cpx, cpy):
            self._deltaX = cpx - self._sectRect.GetLeft()
            self._deltaY = cpy - self._sectRect.GetTop()

        event.Skip()

    def OnMotion(self, event):
        if self._image is not None:
            px, py = event.GetPosition().Get()
            cpx, cpy = self.__ClientToImage(px, py)
            if self._sectRect.ContainsXY(cpx, cpy):
                self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
            else:
                self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW))
        
            if event.LeftIsDown() and self._deltaX is not None:
                left = cpx - self._deltaX
                top = cpy - self._deltaY
                
                self._sectRect.SetLeft(left)
                self._sectRect.SetTop(top)
                
                self._SendRectChangedEvent()
                
                self.Refresh()

    def OnLeftUp(self, event):
        self._deltaX = None
        self._deltaY = None
        
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
        self.Refresh()
            
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
            self._sectRect = wx.Rect(0, 0, self._image.GetWidth(), self._image.GetWidth() / (16.0 / 9.0))
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
        self.Refresh()
            
    def __KeepRectInImage(self):
        if self._image is None:
            return
        
        left = self._sectRect.GetLeft()
        top = self._sectRect.GetTop()
        width = self._sectRect.GetWidth()
        height = self._sectRect.GetHeight()
        
        if width > self._image.GetWidth():
            width = self._image.GetWidth()
            height = width / (16.0 / 9.0)
        if height > self._image.GetHeight():
            height = self._image.GetHeight()
            width = height / (16.0 / 9.0)

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
    
          