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

import logging
import random

import Image, ImageDraw

from lib.common.ObserverPattern import Observable

from core.util import RotateExif
from core.Aspect import Aspect


class Picture(Observable):
    
    EFFECT_NONE        = 0
    EFFECT_BLACK_WHITE = 1
    EFFECT_SEPIA       = 2
    
    TRANS_NONE = 0
    TRANS_FADE = 1
    TRANS_ROLL = 2
    
    def __init__(self, filename):
        Observable.__init__(self)
        self._filename   = filename
        self._startRect  = (0, 0, 1280, 720)
        self._targetRect = (0, 0, 1280, 720)
        self._isDummy    = False
        
        self._duration = 7.0
        self._rotation = 0
        self._comment  = u""
        self._effect   = Picture.EFFECT_NONE
        self._width    = -1
        self._height   = -1
        
        self._trans    = Picture.TRANS_FADE
        self._transDur = 1.0
        
    def __Reset(self):
        pass
        
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
        if self._width == -1:
            self.GetImage()
        return self._width
    
    def SetHeight(self, height):
        self._height = height
    def GetHeight(self):
        if self._height == -1:
            self.GetImage()
        return self._height
    
    def SetTransition(self, transition):
        if transition == self._trans:
            return
        self._trans = transition
        self.Notify('transition')
    def GetTransition(self):
        return self._trans
    
    def SetTransitionDuration(self, transDur):
        if transDur == self._transDur:
            return
        self._transDur = transDur
        self.Notify('duration')
    def GetTransitionDuration(self):
        if self._trans == Picture.TRANS_NONE:
            return 0.0
        return self._transDur
    
    def AutoPath(self, aspect):
        ratio = Aspect.ToFloat(aspect)
        width = self.GetWidth()
        height = self.GetHeight()
        if width < height:
            # portrait
            self._startRect = (0, 0, width, width / ratio)
            self._targetRect = (0, height - (width / ratio), width, width / ratio)
        else:
            scaledWidth = width * 0.75
            self._startRect = (0, 0, width, width / ratio)
            d = random.randint(0, 3)
            if d == 0:
                self._targetRect = (0, 0, scaledWidth, scaledWidth / ratio)
            elif d == 1:
                self._targetRect = (0, height - (scaledWidth / ratio), scaledWidth, scaledWidth / ratio)
            elif d == 2:
                self._targetRect = (width - (scaledWidth / ratio), 0, scaledWidth, scaledWidth / ratio)
            elif d == 3:
                self._targetRect = (width - (scaledWidth / ratio), height - (scaledWidth / ratio), scaledWidth, scaledWidth / ratio)

        if random.randint(0, 1):
            self._targetRect, self._startRect = self._startRect, self._targetRect

        self.Notify("start")
        self.Notify("target")
    
    def __Rotate(self, clockwise=True):
        if clockwise:
            self._rotation += 1
        else:
            self._rotation -= 1
        if self._rotation > 3:
            self._rotation = 0
        if self._rotation < -3:
            self._rotation = 0

        self._width, self._height = self._height, self._width
        self.__Reset()
    
    def Rotate(self, clockwise=True):
        self.__Rotate(clockwise)
        self.Notify("bitmap")
        
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

    def GetImage(self):
        img = self.__GetImage()
        img = self.__ProcessImage(img)
            
        self._width = img.size[0]
        self._height = img.size[1]
        
        return img
        
    def __GetImage(self):
        try:
            img = Image.open(self.GetFilename())
            self._isDummy = False
        except StandardError, err:
            logging.debug("PILBackend.GetImage(%s): %s", self.GetFilename(), err, exc_info=1)
            img = self.__CreateDummyImage(str(err))
            self._isDummy = True
        return img

    def __ProcessImage(self, img):
        if not self._isDummy:
            img = RotateExif(img)
            rotation = self.GetRotation() * -90
            if rotation != 0:
                img = img.rotate(rotation)

        if self._effect == Picture.EFFECT_BLACK_WHITE:
            img = img.convert("L")

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

        return img.convert("RGB")
    
    def GetThumbnail(self, width=None, height=None):
        img = self.__GetImage()

        aspect = float(img.size[0]) / float(img.size[1])
        if width is not None and height is not None:
            thumbWidth = width
            thumbHeight = height
        elif width is not None:
            thumbWidth = width
            thumbHeight = int(round(thumbWidth / aspect))
        elif height is not None:
            thumbHeight = height
            thumbWidth = int(round(thumbHeight * aspect))
            
        # prescale image to speed up processing
        img.thumbnail((max(thumbWidth, thumbHeight), max(thumbWidth, thumbHeight)), Image.NEAREST)
        img = self.__ProcessImage(img)
        
        # make the real thumbnail
        img.thumbnail((thumbWidth, thumbHeight), Image.NEAREST)
        
#        newImg = Image.new("RGB", (thumbWidth, thumbHeight), 0)
#        newImg.paste(img, (abs(thumbWidth - img.size[0]) / 2, 
#                           abs(thumbHeight - img.size[1]) / 2))
#        img = newImg
        
        return img
