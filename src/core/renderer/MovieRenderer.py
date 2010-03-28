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
import sys
import re
from subprocess import Popen, PIPE, STDOUT

from core.OutputProfile import OutputProfile
from core.renderer.SingleFileRenderer import SingleFileRenderer


if sys.platform == "win32":
    appDir = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "..")
    path = []
    path.append(os.path.join(appDir, "extBin", "mplayer"))
    os.putenv("PATH", ";".join(path)) 


class MovieRenderer(SingleFileRenderer):
    
    def __init__(self):
        SingleFileRenderer.__init__(self)
        
        self._encOut = None
        self._encErr = None
        
        self._procEncoder = None
        
    @staticmethod
    def GetName():
        return _(u"Video clip")
    
    @staticmethod
    def CheckDependencies(msgList):
        SingleFileRenderer.CheckDependencies(msgList)
        
        proc = Popen("mencoder", stdout=PIPE, stderr=STDOUT, shell=True)
        proc.wait()
        output = proc.stdout.read()
        if not re.search("^(mplayer|mencoder)", output, re.I):
            msgList.append(_(u"mencoder (mencoder) required!"))

    @staticmethod
    def GetProperties():
        return SingleFileRenderer.GetProperties() + ["Bitrate", "FFOURCC", "RenderSubtitle"]

    @staticmethod
    def GetDefaultProperty(prop):
        if prop == "FFOURCC":
            return "XVID"
        if prop == "RenderSubtitle":
            return False
        return SingleFileRenderer.GetDefaultProperty(prop)

    def ProcessFinalize(self, image):
        image.save(self._procEncoder.stdin, "JPEG")
    
    def _CleanUp(self):
        self._procEncoder.communicate()

        for log in [self._encOut, self._encErr]:
            if log:
                log.close()
        
    def ProcessAbort(self):
        self._CleanUp()

    def Prepare(self):
        self._encOut = open(os.path.join(self.GetOutputPath(), "mencoder_out.log"), 'w')
        self._encErr = open(os.path.join(self.GetOutputPath(), "mencoder_err.log"), 'w')
        
        if self.PProfile.PName in ["VCD", "SVCD", "DVD"]:
            cmd = self.__ProcessMpegOutput()
        else:
            cmd = self.__ProcessAviOutput()

        self._procEncoder = Popen(cmd, stdin=PIPE, stdout=self._encOut, stderr=self._encErr, shell=True)
        
    def Finalize(self):
        self._CleanUp()
        
        if MovieRenderer.GetProperty("RenderSubtitle"):
            path = "%s%soutput.srt" % (self.GetOutputPath(), os.sep)
            if os.path.exists(path):
                os.remove(path)

    def __ProcessMpegOutput(self):
        aspect = "%.3f" % self._aspect
        if self.PProfile.PVideoNorm == OutputProfile.PAL:
            framerate = "25"
            keyint = 15
            res = self.PProfile.PResPal
        else:
            framerate = "30000/1001"
            keyint = 18
            res = self.PProfile.PResNtsc
            
        if self.PProfile.PName == "VCD":
            format = "xvcd"
            srate = "44100"
            lavcopts = "vcodec=mpeg1video:keyint=%(keyint)s:vrc_buf_size=327:vrc_minrate=1152:vbitrate=1152:vrc_maxrate=1152:acodec=mp2:abitrate=224:aspect=%(aspect)s" % {"keyint": keyint,
                                                                                                                                                                           "aspect": aspect}
        elif self.PProfile.PName == "SVCD":
            format = "xsvcd"
            srate = "44100"
            lavcopts = "vcodec=mpeg2video:mbd=2:keyint=%(keyint)s:vrc_buf_size=917:vrc_minrate=600:vbitrate=2500:vrc_maxrate=2500:acodec=mp2:abitrate=224:aspect=%(aspect)s" % {"keyint": keyint,
                                                                                                                                                                                "aspect": aspect}
        elif self.PProfile.PName == "DVD":
            format = "dvd:tsaf"
            srate = "48000"
            lavcopts = "vcodec=mpeg2video:vrc_buf_size=1835:vrc_maxrate=9800:vbitrate=5000:keyint=%(keyint)s:vstrict=0:acodec=ac3:abitrate=192:aspect=%(aspect)s" % {"keyint": keyint,
                                                                                                                                                                     "aspect": aspect}
        else:
            raise RuntimeError('format not supported')
            
        if MovieRenderer.GetProperty("RenderSubtitle"):
            subArgs = "-sub \"%s%soutput.srt\"" % (self.GetOutputPath(), os.sep)
        else:
            subArgs = ""

        if self.PAudioFile is None:
            audioArgs = ""
        else:
            audioArgs = "-audiofile \"%s\"" % self.PAudioFile
        
#              "-vf scale=%(resx)d:%(resy)d,harddup " \
#              "-of mpeg -mpegopts format=%(format)s " \
        cmd = "mencoder -cache 1024 -demuxer lavf -lavfdopts format=mjpeg "\
              "%(audioArgs)s " \
              "%(subArgs)s " \
              "-oac lavc -ovc lavc " \
              "-of lavf -lavfopts format=mpg " \
              "-srate %(srate)s -af lavcresample=%(srate)s " \
              "-lavcopts %(lavcopts)s " \
              "-ofps %(framerate)s " \
              "-o \"%(path)s%(sep)soutput.mpg\" -" % {'path': self.GetOutputPath(),
                                                      'sep': os.sep,
                                                      'audioArgs': audioArgs,
                                                      "subArgs": subArgs,
                                                      'framerate': framerate,
                                                      'format': format,
                                                      'resx': res[0],
                                                      'resy': res[1],
                                                      'srate': srate,
                                                      'lavcopts': lavcopts}
        
        return cmd


    def __ProcessAviOutput(self):
        if self.PProfile.PVideoNorm == OutputProfile.PAL:
            framerate = "25:1"
        else:
            framerate = "30000:1001"
            
        if MovieRenderer.GetProperty("Bitrate") == MovieRenderer.GetDefaultProperty("Bitrate"):
            bitrate = self.PProfile.PBitrate
        else:
            bitrate = MovieRenderer.GetProperty("Bitrate")

        if MovieRenderer.GetProperty("RenderSubtitle"):
            subArgs = "-sub \"%s%soutput.srt\"" % (self.GetOutputPath(), os.sep)
        else:
            subArgs = ""

        if self.PAudioFile is None:
            audioArgs = ""
        else:
            audioArgs = "-oac copy -audiofile \"%s\"" % self.PAudioFile
        
        cmd = "mencoder -cache 1024 -demuxer lavf -lavfdopts format=mjpeg " \
              "%(audioArgs)s " \
              "%(subArgs)s " \
              "-ovc lavc -lavcopts vcodec=mpeg4:vbitrate=%(bitrate)d:vhq:autoaspect -ffourcc %(ffourcc)s " \
              "-o \"%(path)s%(sep)soutput.avi\" -" % {'path': self.GetOutputPath(),
                                                      'sep': os.sep,
                                                      'ffourcc': MovieRenderer.GetProperty('FFOURCC'),
                                                      'bitrate': bitrate,
                                                      'audioArgs': audioArgs,
                                                      "subArgs": subArgs,
                                                      'framerate': framerate}
        return cmd
