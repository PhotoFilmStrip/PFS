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

import Image

from core.BaseRenderer import BaseRenderer


class SingleFileRenderer(BaseRenderer):
    
    def __init__(self):
        BaseRenderer.__init__(self)
        self._counter = 0
    
    @staticmethod
    def GetName():
        return _(u"Single pictures")
    
    @staticmethod
    def GetProperties():
        return ["ResampleFilter"]
    
    @staticmethod
    def GetDefaultProperty(prop):
        if prop == "ResampleFilter":
            return "Antialias"
        else:
            return BaseRenderer.GetDefaultProperty(prop)

    def Prepare(self):
        pass
    
    def ProcessCropAndResize(self, image, cropRect, size):
        box = [int(cropRect[0]), int(cropRect[1]), 
               int(cropRect[0] + cropRect[2]), int(cropRect[1] + cropRect[3])]
        subImg = image.crop(box)
        
        filtr = Image.NEAREST
        if not self._draft:
            filterStr = self.GetProperty("ResampleFilter").lower()

            # Begin Optimizations
            if cropRect[2] > size[0] * 3:
                # downscale more than factor 3, prescaling
                subImg = subImg.resize((size[0] * 2, size[1] * 2))#, Image.BILINEAR)
            if cropRect[2] < size[0]:
                # upscaling
                filterStr = "bicubic"
            # End Optimizations
            
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
        image.save(newFilename, format, quality=90)
    
    def Finalize(self):
        pass

    def ProcessAbort(self):
        pass
