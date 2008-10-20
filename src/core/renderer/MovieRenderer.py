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
        fr = self.GetFrameRate()
        if fr == 25.0:
            framerate = "25:1"
            mode = "p"
        else:
            framerate = "30000:1001"
            mode = "n"
        
#              'yuvscaler -v 0 -n %(mode)s -O "SIZE_%(width)dx%(height)d" | '\
        cmd = 'ppmtoy4m -v 0 -F %(framerate)s -S 420mpeg2 %(path)s%(sep)soutput.ppm | '\
              'mpeg2enc -v 0 -M 3 -f 3 -4 1 -2 1 -q7 -P -g 6 -G 18 -a 1 -V 300 -n %(mode)s -b %(bitrate)d -o %(path)s%(sep)soutput.m2v' % \
                            {"path": self.GetOutputPath(),
                             "sep": os.sep,
                             "mode": mode,
                             "width": self.GetResolution()[0],
                             "height": self.GetResolution()[1],
                             "bitrate": self._bitrate,
                             "framerate": framerate}
        os.system(cmd)

        os.remove("%s%soutput.ppm" % (self.GetOutputPath(), os.sep))
    
