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
from subprocess import Popen, PIPE, STDOUT

import wx

from core.BaseRenderer import BaseRenderer
from core.Picture import Picture


class SingleFileRenderer(BaseRenderer):
    
    def __init__(self):
        BaseRenderer.__init__(self)
        self._counter = 0
    
    @staticmethod
    def CheckDependencies(msgList):
        proc = Popen("convert -h", stdout=PIPE, stderr=STDOUT, shell=True)
        proc.stdout.read()
        if proc.wait() != 0:
            msgList.append("convert (imagemagick) required!")
            return False
        proc = Popen("composite -h", stdout=PIPE, stderr=STDOUT, shell=True)
        proc.stdout.read()
        if proc.wait() != 0:
            msgList.append("composite (imagemagick) required!")
            return False
        return True
    
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
        if prop == "ResampleFilter":
            return "Sinc"
        return BaseRenderer.GetDefaultProperty(prop)

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
        
        if not self.GetProperty("UseResample"):
            subImg.Rescale(size[0], size[1], wx.IMAGE_QUALITY_HIGH)

        newFilename = os.path.join(self.GetOutputPath(), '%09d.pnm' % self._counter)
        subImg.SaveFile(newFilename, wx.BITMAP_TYPE_PNM)
        
        if self.GetProperty("UseResample"):
            cmd = "convert \"%(path)s\" -depth 8 " \
                          "-filter %(filter)s " \
                          "-resize %(width)dx%(height)d! \"%(path)s\"" % \
                            {'path': newFilename,
                             'filter': SingleFileRenderer.GetProperty("ResampleFilter"),
                             'width': size[0], 
                             'height': size[1]}
            proc = Popen(cmd, shell=True)
            exitCode = proc.wait()
            if exitCode != 0:
                raise RuntimeError("%s returned exitcode %d!" % (cmd, exitCode))
        
        if not os.path.exists(newFilename):
            raise RuntimeError("imagefile '%s' not created!" % newFilename)
        
        return newFilename

    def ProcessTransition(self, fileListFrom, fileListTo):
        files = []
        count = len(fileListFrom)
        for idx in range(count):
            f1 = fileListFrom[idx]
            f2 = fileListTo[idx]
            
            cmd = "composite \"%s\" \"%s\" -depth 8 -quality 100 -dissolve %d \"%s\"" % (f2, f1, (100 / count) * idx, f1)
            proc = Popen(cmd, shell=True)
            exitCode = proc.wait()
            if exitCode != 0:
                raise RuntimeError("%s returned exitcode %d!" % (cmd, exitCode))
            
            os.remove(f2)
            files.append(f1)
        return files
    
    def ProcessFinalize(self, filename):
        pass
    
    def Finalize(self):
        pass

    def ProcessAbort(self):
        pass
