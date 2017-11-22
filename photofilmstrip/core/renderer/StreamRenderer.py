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

import sys

from photofilmstrip.core.renderer.SingleFileRenderer import SingleFileRenderer
from photofilmstrip.core.BaseRenderer import FinalizeHandler


class StreamRenderer(SingleFileRenderer, FinalizeHandler):
    
    def __init__(self):
        SingleFileRenderer.__init__(self)
    
    @staticmethod
    def GetName():
        return u"Stream output"
    
    @staticmethod
    def GetProperties():
        return SingleFileRenderer.GetProperties() + ["Format"]

    @staticmethod
    def GetDefaultProperty(prop):
        if prop == "Format":
            return "PPM"
        else:
            return SingleFileRenderer.GetDefaultProperty(prop)

    def GetFinalizeHandler(self):
        return self

    def UseSmartFinalize(self):
        '''
        overrides FinalizeHandler.UseSmartFinalize
        :param pilImg:
        '''
        return False

    def ProcessFinalize(self, pilImg):
        '''
        overrides FinalizeHandler.ProcessFinalize
        :param pilImg:
        '''
        imgFormat = self.GetProperty("Format")
        if imgFormat in ["JPEG", "PPM"]:
            pilImg.save(sys.stdout, imgFormat)
        else:
            raise RuntimeError("unsupported format: %s", imgFormat)
