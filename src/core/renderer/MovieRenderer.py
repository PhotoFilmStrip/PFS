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

import os, logging
from subprocess import Popen, PIPE

from core.renderer.SingleFileRenderer import SingleFileRenderer


class MovieRenderer(SingleFileRenderer):
    
    def __init__(self):
        SingleFileRenderer.__init__(self)
        self._bitrate = 2000
        
        self._procPpmIn   = None
        self._procEncoder = None
        
    @staticmethod
    def CheckDependencies():
        pass

    @staticmethod
    def GetName():
        return _(u"MPEG-Video")
    
    @staticmethod
    def GetProperties():
        return SingleFileRenderer.GetProperties() + ["Bitrate"]

    def SetBitrate(self, bitrate):
        self._bitrate = bitrate

    def ProcessFinalize(self, filename):
        cmd = 'convert ppm:"%s" - ' % (filename)
        conv = Popen(cmd, stdout=self._procPpmIn.stdin, shell=True)
        exitCode = conv.wait() 
        if exitCode == 0:
            os.remove(filename)
        else:
            logging.getLogger('MovieRenderer').error("command '%s' returned exitcode: %d", cmd, exitCode)
    
    def Prepare(self):
        fr = self.GetFrameRate()
        if fr == 25.0:
            framerate = "25:1"
            mode = "p"
        else:
            framerate = "30000:1001"
            mode = "n"
            
        profs = ["VCD", "SVCD", "DVD"]
        if self.GetProfileName() in profs:
            cmd = 'yuvscaler -v 0 -n %(mode)s -O %(profile)s |'\
                  'mpeg2enc -v 0 -M 3 ' \
                           '-4 1 -2 1 -P -g 6 -G 18 ' \
                           '-f %(profileIdx)d -a 3 ' \
                           '-n %(mode)s ' \
                           '-b %(bitrate)d ' \
                           '-o %(path)s%(sep)soutput.m2v' % \
                                {"path": self.GetOutputPath(),
                                 "sep": os.sep,
                                 "mode": mode,
                                 'profile': self.GetProfileName(),
                                 'profileIdx': profs.index(self.GetProfileName()) + 6,
                                 "bitrate": self._bitrate}
        else:
            cmd = "mencoder -cache 1024 " \
                  "-ovc lavc -lavcopts vcodec=mpeg4:vbitrate=%(bitrate)d:vhq:autoaspect -ffourcc XVID " \
                  "-o %(path)s%(sep)soutput.avi -" % {'path': self.GetOutputPath(),
                                                      'sep': os.sep,
                                                      'bitrate': self._bitrate}

        ppmCmd = "ppmtoy4m -v 0 -F %(framerate)s -S 420mpeg2" % {'framerate': framerate}
        self._procEncoder = Popen(cmd, stdin=PIPE, shell=True)
        self._procPpmIn = Popen(ppmCmd, stdin=PIPE, stdout=self._procEncoder.stdin, shell=True)

    def Finalize(self):
        self._procPpmIn.communicate()
        self._procEncoder.communicate()

    def ProcessAbort(self):
        self._procEncoder.stdin.close()
        self._procPpmIn.stdin.close()
#        self.Finalize()
