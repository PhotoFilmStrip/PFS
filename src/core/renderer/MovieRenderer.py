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
from subprocess import Popen, PIPE, STDOUT

from core.OutputProfile import OutputProfile
from core.renderer.SingleFileRenderer import SingleFileRenderer


if sys.platform == "win32":
    appDir = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "..")
    path = []
    path.append(os.path.join(appDir, "extBin", "mjpegtools", "bin"))
    path.append(os.path.join(appDir, "extBin", "mplayer"))
    os.putenv("PATH", ";".join(path)) 


class MovieRenderer(SingleFileRenderer):
    
    def __init__(self):
        SingleFileRenderer.__init__(self)
        
        self._ppmErr = None
        self._encOut = None
        self._encErr = None
        
        self._procPpmIn   = None
        self._procEncoder = None
        
    @staticmethod
    def CheckDependencies(msgList):
        SingleFileRenderer.CheckDependencies(msgList)
        
        proc = Popen("ppmtoy4m -h", stdout=PIPE, stderr=STDOUT, shell=True)
        proc.stdout.read()
        if proc.wait() != 0:
            msgList.append(_(u"ppmtoy4m (mjpegtools) required!"))

    @staticmethod
    def GetProperties():
        return SingleFileRenderer.GetProperties() + ["Bitrate"]

    def ProcessFinalize(self, image):
        image.save(self._procPpmIn.stdin, "PPM")
    
    def _CleanUp(self):
        self._procPpmIn.communicate()
        self._procEncoder.communicate()

        for log in [self._ppmErr, self._encOut, self._encErr]:
            if log:
                log.close()
        
    def ProcessAbort(self):
        self._CleanUp()


class MPEG2Renderer(MovieRenderer):
    
    def __init__(self):
        MovieRenderer.__init__(self)
        
    @staticmethod
    def CheckDependencies(msgList):
        MovieRenderer.CheckDependencies(msgList)

        proc = Popen("mpeg2enc -h", stdout=PIPE, stderr=STDOUT, shell=True)
        proc.stdout.read()
        if proc.wait() != 0:
            msgList.append(_(u"mpeg2enc (mjpegtools) required!"))

    @staticmethod
    def GetName():
        return _(u"MPEG2-Video")
    
    def Prepare(self):
        self._ppmErr = open(os.path.join(self.GetOutputPath(), "ppmtoy4m_err.log"), 'w')
        self._encOut = open(os.path.join(self.GetOutputPath(), "mpeg2enc_out.log"), 'w')
        self._encErr = open(os.path.join(self.GetOutputPath(), "mpeg2enc_err.log"), 'w')

        if self.PProfile.PVideoNorm == OutputProfile.PAL:
            framerate = "25:1"
            mode = "p"
        else:
            framerate = "30000:1001"
            mode = "n"
            
        profs = ["$$$", "VCD", "$$$", "$$$", "SVCD", "$$$", "$$$", "$$$", "DVD"]
        if not self.PProfile.PName in profs:
            raise RuntimeError('format not supported')
        
        if MPEG2Renderer.GetProperty("Bitrate") == MPEG2Renderer.GetDefaultProperty("Bitrate"):
            bitrate = self.PProfile.PBitrate
        else:
            bitrate = MPEG2Renderer.GetProperty("Bitrate")

#        cmd = 'yuvscaler -v 0 -n %(mode)s -O %(profile)s |'\
        cmd = 'mpeg2enc -v 0 -M 3 ' \
                       '-4 1 -2 1 -P -g 6 -G 18 ' \
                       '-f %(profileIdx)d -a 3 ' \
                       '-n %(mode)s ' \
                       '-b %(bitrate)d ' \
                       '-o \"%(path)s%(sep)soutput.m2v\"' % \
                            {"path": self.GetOutputPath(),
                             "sep": os.sep,
                             "mode": mode,
                             'profileIdx': profs.index(self.PProfile.PName),
                             "bitrate": bitrate}

        ppmCmd = "ppmtoy4m -v 0 -F %(framerate)s -S 420mpeg2" % {'framerate': framerate}
        self._procEncoder = Popen(cmd, stdin=PIPE, stdout=self._encOut, stderr=self._encErr, shell=True)
        self._procPpmIn = Popen(ppmCmd, stdin=PIPE, stdout=self._procEncoder.stdin, stderr=self._ppmErr, shell=True)

    def Finalize(self):
        self._CleanUp()

        if self.PAudioFile is None:
            return
        
        audioLog = open(os.path.join(self.GetOutputPath(), "audio.log"), 'w')
        
#        cmd = "mplayer -ao pcm:file=Zieldatei.wav Quelldatei.rm"
#        cmd = "lame --decode Beispiel.mp3 Beispiel.wav" 
        cmd = "mpg123 -w \"%(path)s%(sep)saudio.wav\" \"%(audioFile)s\"" % \
                        {"path": self.GetOutputPath(),
                         "sep": os.sep,
                         "audioFile": self.PAudioFile}
        proc = Popen(cmd, stdout=audioLog, stderr=audioLog, shell=True)
        exitCode = proc.wait() 
        if exitCode != 0:
            raise RuntimeError('MP3 to WAV failed')

        cmd = "mp2enc -o \"%(path)s%(sep)saudio.mp2\" < \"%(path)s%(sep)saudio.wav\"" % \
                        {"path": self.GetOutputPath(),
                         "sep": os.sep}
        proc = Popen(cmd, stdout=audioLog, stderr=audioLog, shell=True)
        exitCode = proc.wait() 
        if exitCode != 0:
            raise RuntimeError('WAV to MP2 failed')
        
        profs = ["$$$", "VCD", "$$$", "$$$", "SVCD", "$$$", "$$$", "$$$", "DVD"]
        cmd = "mplex \"%(path)s%(sep)soutput.m2v\" \"%(path)s%(sep)saudio.mp2\" " \
                    "-v 0 -f %(profileIdx)d -o \"%(path)s%(sep)soutput.mpg\"" % \
                        {"path": self.GetOutputPath(),
                         "sep": os.sep,
                         'profileIdx': profs.index(self.PProfile.PName)}
        proc = Popen(cmd, stdout=audioLog, stderr=audioLog, shell=True)
        exitCode = proc.wait() 
        if exitCode != 0:
            raise RuntimeError('mplex failed')
        
        audioLog.close()


class MPEG4Renderer(MovieRenderer):
    
    def __init__(self):
        MovieRenderer.__init__(self)
        
    @staticmethod
    def CheckDependencies(msgList):
        MovieRenderer.CheckDependencies(msgList)

        proc = Popen("mencoder", stdout=PIPE, stderr=STDOUT, shell=True)
        proc.wait()
        output = proc.stdout.read()
        if not output.startswith("MEncoder"):
            msgList.append(_(u"mencoder (mencoder) required!"))

    @staticmethod
    def GetProperties():
        return MovieRenderer.GetProperties() + ["FFOURCC", "RenderSubtitle"]

    @staticmethod
    def GetDefaultProperty(prop):
        if prop == "FFOURCC":
            return "XVID"
        if prop == "RenderSubtitle":
            return False
        return MovieRenderer.GetDefaultProperty(prop)

    @staticmethod
    def GetName():
        return _(u"MPEG4-Video (XVid)")

    def Prepare(self):
        self._ppmErr = open(os.path.join(self.GetOutputPath(), "ppmtoy4m_err.log"), 'w')
        self._encOut = open(os.path.join(self.GetOutputPath(), "mencoder_out.log"), 'w')
        self._encErr = open(os.path.join(self.GetOutputPath(), "mencoder_err.log"), 'w')
        
        if self.PProfile.PVideoNorm == OutputProfile.PAL:
            framerate = "25:1"
        else:
            framerate = "30000:1001"
            
        if MPEG4Renderer.GetProperty("Bitrate") == MPEG4Renderer.GetDefaultProperty("Bitrate"):
            bitrate = self.PProfile.PBitrate
        else:
            bitrate = MPEG4Renderer.GetProperty("Bitrate")

        if MPEG4Renderer.GetProperty("RenderSubtitle"):
            subArgs = "-sub \"%s%soutput.srt\"" % (self.GetOutputPath(), os.sep)
        else:
            subArgs = ""

        if self.PAudioFile is None:
            audioArgs = ""
        else:
            audioArgs = "-oac copy -audiofile \"%s\"" % self.PAudioFile
        
        cmd = "mencoder -cache 1024 " \
              "%(audioArgs)s " \
              "%(subArgs)s " \
              "-ovc lavc -lavcopts vcodec=mpeg4:vbitrate=%(bitrate)d:vhq:autoaspect -ffourcc %(ffourcc)s " \
              "-o \"%(path)s%(sep)soutput.avi\" -" % {'path': self.GetOutputPath(),
                                                      'sep': os.sep,
                                                      'ffourcc': MPEG4Renderer.GetProperty('FFOURCC'),
                                                      'bitrate': bitrate,
                                                      'audioArgs': audioArgs,
                                                      "subArgs": subArgs}

        ppmCmd = "ppmtoy4m -v 0 -F %(framerate)s -S 420mpeg2" % {'framerate': framerate}
        self._procEncoder = Popen(cmd, stdin=PIPE, stdout=self._encOut, stderr=self._encErr, shell=True)
        self._procPpmIn = Popen(ppmCmd, stdin=PIPE, stdout=self._procEncoder.stdin, stderr=self._ppmErr, shell=True)

    def Finalize(self):
        self._CleanUp()
        
        if MPEG4Renderer.GetProperty("RenderSubtitle"):
            path = "%s%soutput.srt" % (self.GetOutputPath(), os.sep)
            if os.path.exists(path):
                os.remove(path)
