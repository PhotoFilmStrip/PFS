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
import cStringIO

import Image, ImageDraw, ImageFont

from lib.common.ObserverPattern import Observable


class Picture(Observable):
    
    EFFECT_NONE        = 0
    EFFECT_BLACK_WHITE = 1
    EFFECT_SEPIA       = 2
    
    def __init__(self, filename):
        Observable.__init__(self)
        self._filename   = filename
        self._startRect  = (0, 0, 1280, 720)
        self._targetRect = (0, 0, 1280, 720)
        self._isDummy    = False
        
        self._img      = None
        
        # to buffer wx bitmaps
        self._bmp      = None
        self._bmpThumb = None

        self._duration = 7.0
        self._rotation = 0
        self._comment  = u""
        self._effect   = Picture.EFFECT_NONE
        self._width    = -1
        self._height   = -1
        
    def __Reset(self):
        self._img = None
        self._bmp = None
        self._bmpThumb = None
        
    def GetFilename(self):
        return self._filename
    
    def SetStartRect(self, rect):
        if rect == self._startRect or self._isDummy:
            return
        self._startRect = rect
        self.Notify("start")
    def GetStartRect(self):
        return self._startRect
        
    def SetTargetRect(self, rect):
        if rect == self._targetRect or self._isDummy:
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
        self.__Reset()
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
        self.__Reset()
    
    def Rotate(self, clockwise=True):
        self.__Rotate(clockwise)
        self.Notify("bitmap")
        
    def GetImage(self):
        if self._img is not None:
            return self._img

        try:
            img = Image.open(self._filename)
            self._isDummy = False
        except IOError, err:
            img = self.__CreateDummyImage(str(err))
            self._isDummy = True
        
        img = img.rotate(self._rotation * -90)
        
        if self._effect == Picture.EFFECT_BLACK_WHITE:
            img = img.convert("L")
            img = img.convert("RGB")

        elif self._effect == Picture.EFFECT_SEPIA:
            def make_linear_ramp(white):
                # putpalette expects [r,g,b,r,g,b,...]
                ramp = []
                r, g, b = white
                for i in range(255):
                    ramp.extend((r*i/255, g*i/255, b*i/255))
                return ramp

            # make sepia ramp (tweak color as necessary)
            sepia = make_linear_ramp((255, 240, 192))
            img = img.convert("L")
            img.putpalette(sepia)
            img = img.convert("RGB")
        self._img = img
        return img
    
    def GetThumbnail(self, width, height):
        img = self.GetImage()
        img = img.copy()
        img.thumbnail((width, height))
        newImg = Image.new(img.mode, (width, height), 0xFFFFFF)
        newImg.paste(img, (0, 0))
        return newImg

    def ImageToStream(self, img, format="JPEG"):
        fd = cStringIO.StringIO()
        img.save(fd, format)
        fd.seek(0)
        return fd

    def GetBitmap(self):
        import wx
        if self._bmp is None:
            img = self.GetImage()
            wxImg = wx.ImageFromStream(self.ImageToStream(img), wx.BITMAP_TYPE_JPEG)
            self._bmp = wxImg.ConvertToBitmap() 
        return  self._bmp
    
    def GetScaledBitmap(self, width, height):
        import wx
        if self._bmpThumb is None:
            img = self.GetThumbnail(width, height)
            wxImg = wx.ImageFromStream(self.ImageToStream(img), wx.BITMAP_TYPE_JPEG)
            self._bmpThumb = wxImg.ConvertToBitmap() 
        return self._bmpThumb


    def __CreateDummyImage(self, message):
        width = 400
        height = 300
        img = Image.new("RGB", (width, height), (255, 255, 255))

        draw = ImageDraw.Draw(img)
        textWidth, textHeight = draw.textsize(message)
        x = (width - textWidth) / 2
        y = (height - textHeight * 2)
        draw.text((x, y), message, fill=(0, 0, 0))

        sz = width / 2
        draw.ellipse(((width - sz) / 2, (height - sz) / 2, 
                      (width + sz) / 2, (height + sz) / 2), 
                      fill=(255, 0, 0))

        sz = width / 7
        draw.line((width / 2 - sz, height / 2 - sz, width / 2 + sz, height / 2 + sz), fill=(255, 255, 255), width=20)
        draw.line((width / 2 + sz, height / 2 - sz, width / 2 - sz, height / 2 + sz), fill=(255, 255, 255), width=20)

        del draw
        
        return img
