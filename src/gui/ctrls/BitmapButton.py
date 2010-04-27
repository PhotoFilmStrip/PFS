# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2010 Jens Goepfert
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


class BitmapButton(wx.Panel):
    def __init__(self, parent, id=wx.NewId(), bitmap=wx.NullBitmap, name="", 
                 pos=wx.DefaultPosition, 
                 size=wx.DefaultSize, 
                 style=0):
        wx.Panel.__init__(self, parent, size=bitmap.GetSize(), style=wx.TRANSPARENT_WINDOW)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)

        self.bmpDefault = bitmap
        self.bmpHover = wx.NullBitmap
        self.bmpCurrent = self.bmpDefault
        self.currentImage = self.bmpCurrent.ConvertToImage()
        if not self.currentImage.HasAlpha():
            self.currentImage.InitAlpha()
        self.isHovered = False
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeave)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_MOTION, self.CheckPosition)

    def CheckPosition(self, event):    
        if not self.currentImage.HasAlpha() or self.currentImage.GetAlpha(event.GetX(), event.GetY()) > 0:
            if not self.isHovered:
                if self.bmpHover != wx.NullBitmap:
                    self.bmpCurrent = self.bmpHover
                self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
                self.Refresh()
                self.isHovered = True
        else:
            if self.isHovered:
                self.bmpCurrent = self.bmpDefault
                self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW)) 
                self.Refresh()       
                self.isHovered = False     
        event.Skip()
    
    def OnPaint(self, event):
        dc = wx.PaintDC(self)
#        dc.SetBackground(wx.WHITE_BRUSH)
#        dc.Clear()
        dc.DrawBitmap(self.bmpCurrent, 0, 0, True)

    def SetBitmapHover(self, bmp):
        self.bmpHover = bmp
        
    def OnLeave(self, event):
        if self.isHovered:
            self.bmpCurrent = self.bmpDefault
            self.SetCursor(wx.StockCursor(wx.CURSOR_ARROW)) 
            self.Refresh()
            self.isHovered = False
        event.Skip()
        
    def OnLeftDown(self, event):
        if self.isHovered:
            evt = wx.CommandEvent(wx.EVT_BUTTON.typeId, self.GetId())
            evt.SetEventObject(self)
            self.AddPendingEvent(evt)

