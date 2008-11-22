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

import Image

from core.BaseRenderer import BaseRenderer
from core.Picture import Picture


class SingleFileRenderer(BaseRenderer):
    
    def __init__(self):
        BaseRenderer.__init__(self)
        self._counter = 0
    
    @staticmethod
    def GetName():
        return _(u"Single pictures")
    
    @staticmethod
    def GetProperties():
        return ["UseResample", "ResampleFilter"]
    
    @staticmethod
    def GetDefaultProperty(prop):
        if prop == "UseResample":
            return True
        elif prop == "ResampleFilter":
            return "Antialias"
        else:
            return BaseRenderer.GetDefaultProperty(prop)

    def Prepare(self):
        pass
    
    def ProcessPrepare(self, filename, rotation, effect):
        img = Image.open(filename)
        img.rotate(rotation * -90)
        
#        if effect == Picture.EFFECT_BLACK_WHITE:
#            img = img.convert("L")

        return img
    
    def ProcessCropAndResize(self, preparedResult, cropRect, size):
        box = [int(cropRect[0]), int(cropRect[1]), 
               int(cropRect[0] + cropRect[2]), int(cropRect[1] + cropRect[3])]
        subImg = preparedResult.crop(box)
        
        filtr = Image.NEAREST
        if self.GetProperty("UseResample"):
            filterStr = self.GetProperty("ResampleFilter").lower()
            if filterStr == "bilinear":
                filtr = Image.BILINEAR
            elif filterStr == "bicubic":
                filtr = Image.BICUBIC
            elif filterStr == "antialias":
                filtr = Image.ANTIALIAS
        return subImg.resize(size, filtr)

    def ProcessFinalize(self, image):
        self._counter += 1
        format = "JPEG"
        newFilename = os.path.join(self.GetOutputPath(), 
                                   '%09d.%s' % (self._counter, 
                                                format.lower()))
        image.save(newFilename, format)
    
    def Finalize(self):
        pass

    def ProcessAbort(self):
        pass
