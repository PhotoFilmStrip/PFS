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

from core.renderer.SingleFileRenderer import SingleFileRenderer


class MovieRenderer(SingleFileRenderer):
    
    def __init__(self):
        SingleFileRenderer.__init__(self)
        self._bitrate = 2000
        
    def SetBitrate(self, bitrate):
        self._bitrate = bitrate

    def ProcessFinalize(self, filename):
        cmd = 'convert ppm:"%s" - >> %s%soutput.ppm' % (filename, os.path.dirname(filename), os.sep)
        os.system(cmd)
        os.remove(filename)
    
    def Finalize(self):
        cmd = 'ppmtoy4m -v 0 -F 25:1 -S 420mpeg2 %(path)s%(sep)soutput.ppm | '\
              'yuvscaler -v 0 -n p -O "SIZE_%(width)dx%(height)d" | '\
              'mpeg2enc -v 0 -M 2 -a 1 -V 230 -b %(bitrate)d -o %(path)s%(sep)soutput.m2v' % \
                            {"path": self.GetOutputPath(),
                             "sep": os.sep,
                             "width": self.GetResolution()[0],
                             "height": self.GetResolution()[1],
                             "bitrate": self._bitrate}
        os.system(cmd)

        os.remove("%s%soutput.ppm" % (self.GetOutputPath(), os.sep))
    
