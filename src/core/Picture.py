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
    
    EFFECT_NONE        = 0
    EFFECT_BLACK_WHITE = 1
    EFFECT_SEPIA       = 2
    
    def __init__(self, filename):
        Observable.__init__(self)
        self._filename = filename
        self._startRect = wx.Rect(0, 0, 1280, 720)
        self._targetRect = wx.Rect(0, 0, 1280, 720)
        
        self.__bmp = None
        self._img = None

        self._duration = 7.0
        self._rotation = 0
        self._comment = u""
        self._effect = Picture.EFFECT_NONE
        self._width = -1
        self._height = -1
        
    def GetFilename(self):
        return self._filename
    
    def SetStartRect(self, rect):
        if rect == self._startRect:
            return
        self._startRect = rect
        self.Notify("start")
    def GetStartRect(self):
        return self._startRect
        
    def SetTargetRect(self, rect):
        if rect == self._targetRect:
            return
        self._targetRect = rect
        self.Notify("target")
    def GetTargetRect(self):
        return self._targetRect
    
    def SetDuration(self, duration):
        if duration == self._duration:
            return
        self._duration = duration
        self.Notify("duration")
    def GetDuration(self):
        return self._duration
    
    def SetComment(self, comment):
        if comment == self._comment:
            return
        self._comment = comment
        self.Notify('comment')
    def GetComment(self):
        return self._comment
    
    def SetEffect(self, effect):
        if effect == self._effect:
            return
        self._effect = effect
        self._img = None
        self.__bmp = None
        self.Notify('effect')
        self.Notify("bitmap")
    def GetEffect(self):
        return self._effect

    def SetRotation(self, rotation):
        for i in range(abs(rotation)):
            self.__Rotate(rotation > 0)
        self.Notify("rotation")
    def GetRotation(self):
        return self._rotation
    
    def SetWidth(self, width):
        self._width = width
    def GetWidth(self):
        return self._width
    
    def SetHeight(self, height):
        self._height = height
    def GetHeight(self):
        return self._height
    
    def __Rotate(self, clockwise=True):
        if clockwise:
            self._rotation += 1
        else:
            self._rotation -= 1
        if self._rotation > 3:
            self._rotation = 0
        if self._rotation < -3:
            self._rotation = 0
        self._img = self.GetImage().Rotate90(clockwise)
        self.__bmp = None
    
    def Rotate(self, clockwise=True):
        self.__Rotate(clockwise)
        self.Notify("bitmap")
        
    def GetImage(self):
        if self._img is None:
            self._img = wx.Image(self._filename)
            self._width = self._img.GetWidth()
            self._height = self._img.GetHeight()
            if self.GetEffect() == Picture.EFFECT_BLACK_WHITE:
                self._img = self._img.ConvertToGreyscale()
        return self._img
    
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


class DummyPicture(Picture):
    
    def __init__(self, filename):
        Picture.__init__(self, filename)

    def GetImage(self):
        if self._img is None:
            if self.GetWidth() == -1:
                w1 = self.GetStartRect()[0] + self.GetStartRect()[2]
                h1 = self.GetStartRect()[1] + self.GetStartRect()[3]
                w2 = self.GetTargetRect()[0] + self.GetTargetRect()[2]
                h2 = self.GetTargetRect()[1] + self.GetTargetRect()[3]
                width = max(w1, w2)
                height = max(h1, h2)
            else:
                width = self.GetWidth()
                height = self.GetHeight()

            bmp2 = wx.ArtProvider_GetBitmap(wx.ART_MISSING_IMAGE, wx.ART_OTHER, (32, 32))
            img = bmp2.ConvertToImage()
            img.Rescale(height / 2, height / 2)
            bmp2 = img.ConvertToBitmap()

            bmp = wx.EmptyBitmap(width, height)
            dc = wx.MemoryDC()
            dc.SelectObject(bmp)
            dc.SetBackground(wx.Brush(wx.Colour(100, 100, 100)))
            dc.Clear()
            dc.DrawImageLabel("", bmp2, wx.Rect(0, 0, width, height),
                              wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL, 0)
            dc.SelectObject(wx.NullBitmap)
            img = bmp.ConvertToImage()
            
            self._img = img
        
        return self._img
