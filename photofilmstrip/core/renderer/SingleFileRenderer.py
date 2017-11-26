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

from photofilmstrip.core.BaseRenderer import BaseRenderer, \
    FinalizeHandler


class SingleFileRenderer(BaseRenderer, FinalizeHandler):

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
        self._counter += 1

        newFilename = os.path.join(self.GetOutputPath(),
                                   '%09d.%s' % (self._counter,
                                                "jpg"))

        pilImg.save(newFilename, "JPEG", quality=95)

    def Finalize(self):
        pass

    def ProcessAbort(self):
        pass
