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

from lib.common.ObserverPattern import Observable


class Picture(Observable):
    
    def __init__(self, filename):
        Observable.__init__(self)
        self._filename = filename
        self._startRect = wx.Rect(0, 0, 1280, 720)
        self._targetRect = wx.Rect(0, 0, 1280, 720)
        
        self.__bmp = None
        self.__img = None

        self._duration = 5.0
        self._rotation = 0
        self._comment = u""
        
    def GetFilename(self):
        return self._filename
    
    def SetStartRect(self, rect):
        self._startRect = rect
        self.Notify("start")
    def GetStartRect(self):
        return self._startRect
        
    def SetTargetRect(self, rect):
        self._targetRect = rect
        self.Notify("target")
    def GetTargetRect(self):
        return self._targetRect
    
    def SetDuration(self, duration):
        self._duration = duration
        self.Notify("duration")
    def GetDuration(self):
        return self._duration
    
    def SetComment(self, comment):
        self._comment = comment
        self.Notify('comment')
    def GetComment(self):
        return self._comment
    
    def SetRotation(self, rotation):
#        self._rotation = rotation
        for i in range(abs(rotation)):
            self.__Rotate(rotation > 0)
        self.Notify("rotation")
    def GetRotation(self):
        return self._rotation
    
    def __Rotate(self, clockwise=True):
        if clockwise:
            self._rotation += 1
        else:
            self._rotation -= 1
        if self._rotation > 3:
            self._rotation = 0
        if self._rotation < -3:
            self._rotation = 0
        self.__img = self.GetImage().Rotate90(clockwise)
        self.__bmp = None
    
    def Rotate(self, clockwise=True):
        self.__Rotate(clockwise)
        self.Notify("bitmap")
        
    def GetImage(self):
        if self.__img is None:
            self.__img = wx.Image(self._filename)
        return self.__img
    
    def GetBitmap(self):
        if self.__bmp is None:
            self.__bmp = self.GetImage().ConvertToBitmap() 
        return self.__bmp
    
    def GetScaledBitmap(self, width, height):
        bmp = wx.EmptyBitmap(width, height)
        dc = wx.MemoryDC(bmp)
        dc.SetPen(wx.CYAN_PEN)
        dc.SetBrush(wx.CYAN_BRUSH)
        dc.DrawRectangle(0, 0, width, height)
        img = self.GetImage()

        cw, ch = width, height
        iw, ih = img.GetSize().Get()
        rx = float(cw) / float(iw)
        ry = float(ch) / float(ih)
        
        newWidth = cw
        newHeight = ih * rx
        
        if newHeight > ch:
            newHeight = ch
            newWidth = iw * ry
        
        newImg = img.Scale(newWidth, newHeight)
        dc.DrawBitmap(newImg.ConvertToBitmap(), 0, 0)
        return bmp
