# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2011 Jens Goepfert
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
    
    def ProcessFinalize(self, backendCtx):
        self._counter += 1
        imgFormat = "JPEG"
        
        newFilename = os.path.join(self.GetOutputPath(), 
                                   '%09d.%s' % (self._counter, 
                                                imgFormat.lower()))
        fd = open(newFilename, "wb")
        backendCtx.ToStream(fd, imgFormat, quality=90)
        fd.close()
    
    def Finalize(self):
        pass

    def ProcessAbort(self):
        pass
