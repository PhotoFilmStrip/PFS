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
import logging

import wx

from core.BaseRenderer import BaseRenderer
from core.Picture import Picture


class SingleFileRenderer(BaseRenderer):
    
    def __init__(self):
        BaseRenderer.__init__(self)
        self._counter = 0
        self._useResample = True
    
    def SetUseResample(self, value):
        self._useResample = value
    
    def CheckDependencies(self):
        pass
    
    def Prepare(self):
        pass
    
    def ProcessPrepare(self, filename, rotation, effect):
        img = wx.Image(filename)
        
        for i in range(abs(rotation)):
            img = img.Rotate90(rotation > 0)
            
        if effect == Picture.EFFECT_BLACK_WHITE:
            img = img.ConvertToGreyscale()

        return img
    
    def ProcessCropAndResize(self, preparedResult, cropRect, size):
        self._counter += 1
        
        subImg = preparedResult.GetSubImage(cropRect)
        
        if not self._useResample:
            subImg.Rescale(size[0], size[1], wx.IMAGE_QUALITY_HIGH)

        newFilename = '%s/%09d.pnm' % (self.GetOutputPath(), self._counter)
        subImg.SaveFile(newFilename, wx.BITMAP_TYPE_PNM)
        
        if self._useResample:
            os.system("convert %s -depth 8 -filter Sinc -resize %dx%d! %s" % (newFilename, 
                                                                              size[0], size[1], 
                                                                              newFilename))
        
        if not os.path.exists(newFilename):
            logging.getLogger('CropAndResize').warning("imagefile '%s' not created!", newFilename)
        
        return newFilename

    def ProcessTransition(self, fileListFrom, fileListTo):
        files = []
        count = len(fileListFrom)
        for idx in range(count):
            f1 = fileListFrom[idx]
            f2 = fileListTo[idx]
            
            cmd = "composite %s %s -depth 8 -quality 100 -dissolve %d %s" % (f2, f1, (100 / count) * idx, f1)
            logging.getLogger('Transition').debug("execute: %s", cmd)
            os.system(cmd)
            logging.getLogger('Transition').debug("delete: %s", f2)
            os.remove(f2)

            files.append(f1)
        return files
    
    def ProcessFinalize(self, filename):
        pass
    
    def Finalize(self):
        pass
