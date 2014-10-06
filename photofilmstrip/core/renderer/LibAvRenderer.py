# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2014 Jens Goepfert
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

import logging
import os
import re
import threading
import Queue
import cStringIO
from subprocess import Popen, PIPE, STDOUT

from photofilmstrip.core.Aspect import Aspect
from photofilmstrip.core.OutputProfile import OutputProfile
from photofilmstrip.core.renderer.RendererException import RendererException
from photofilmstrip.core.BaseRenderer import BaseRenderer


class ResultFeeder(threading.Thread):
    def __init__(self, renderer):
        threading.Thread.__init__(self, name="ResultFeeder")
        self.resQueue = Queue.Queue(20)
        self.active = 1
        self.renderer = renderer
        
    def run(self):
        while 1:
            result = None
            try:
                result = self.resQueue.get(True, 1.0)
            except Queue.Empty:
                if self.active:
                    continue
                else:
                    break

            logging.getLogger("ResultFeeder").debug("result queue size: %s; result size %s",
                                                    self.resQueue.qsize(), 
                                                    len(result))
            self.renderer.GetSink().write(result)


class LibAvRenderer(BaseRenderer):
    
    def __init__(self):
        BaseRenderer.__init__(self)
        
        self._encOut = None
        self._encErr = None
        
        self._procEncoder = None
        
    @staticmethod
    def CheckDependencies(msgList):
        try:
            proc = Popen(["avconv"], stdout=PIPE, stderr=STDOUT, shell=False)
            output = proc.communicate()[0]
        except Exception, err:
            logging.debug("checking for libav-tools failed: %s", err)
            output = ""
        if output.find("avconv") == -1:
            msgList.append(_(u"libav (libav-tools) required!"))

    @staticmethod
    def GetProperties():
        return ["Bitrate", "RenderSubtitle"]

    @staticmethod
    def GetDefaultProperty(prop):
        if prop == "RenderSubtitle":
            return "false"
        return BaseRenderer.GetDefaultProperty(prop)

    def ProcessFinalize(self, pilImg):
#        pilImg.save(self._procEncoder.stdin, 'JPEG', quality=95)
#        return
        res = cStringIO.StringIO()
        pilImg.save(res, 'JPEG', quality=95)
        self._feeder.resQueue.put(res.getvalue())
    
    def __CleanUp(self):
        if self._procEncoder is None:
            return
        
        self._feeder.active = 0
        self._feeder.join()
        
        self._procEncoder.communicate()

        for log in [self._encOut, self._encErr]:
            if log:
                log.close()
        self._procEncoder = None
        
    def ProcessAbort(self):
        self.__CleanUp()

    def Prepare(self):
        self._encOut = open(os.path.join(self.GetOutputPath(), "libav_out.log"), 'w')
        self._encErr = open(os.path.join(self.GetOutputPath(), "labav_err.log"), 'w')
        
        cmd = self._GetCmd()
        self._procEncoder = Popen(cmd, stdin=PIPE, stdout=self._encOut, stderr=self._encErr, shell=False)#, bufsize=-1)
        
        self._feeder = ResultFeeder(self)
        self._feeder.start()
        
    def GetSink(self):
        return self._procEncoder.stdin
    
    def Finalize(self):
        self.__CleanUp()
        
        if not (self.__class__.GetProperty("RenderSubtitle").lower() in ["0", _(u"no"), "false"]):
            # delete subtitle file, if subtitle is rendered in video
            srtPath = os.path.join(self.GetOutputPath(), "output.srt")
            if os.path.exists(srtPath):
                os.remove(srtPath)

    def _GetCmd(self):
        raise NotImplementedError()
    
    def _GetSubArgs(self):
        if not (self.__class__.GetProperty("RenderSubtitle").lower() in ["0", _(u"no"), "false"]):
            subArgs = ["-c:s", os.path.join(self.GetOutputPath(), "output.srt"),
                       "-subcp", "utf8"]
        else:
            subArgs = []
        return subArgs
    
    def _GetAudioArgs(self):
        if self.GetAudioFile() is None:
            audioArgs = []
        else:
            audioArgs = ["-i", self.GetAudioFile()]
        return audioArgs
    
    def _GetFrameRate(self):
        if self.GetProfile().GetVideoNorm() == OutputProfile.PAL:
            framerate = "25/1"
        else:
            framerate = "30000/1001"
        return framerate
    
    def _GetBitrate(self):
        if self.__class__.GetProperty("Bitrate") == self.__class__.GetDefaultProperty("Bitrate"):
            bitrate = self.GetProfile().GetBitrate()
        else:
            try:
                bitrate = int(self.__class__.GetProperty("Bitrate"))
            except:
                raise RendererException(_(u"Bitrate must be a number!"))
        return bitrate


class MPEGRenderer(LibAvRenderer):
    
    def __init__(self):
        LibAvRenderer.__init__(self)
        
    @staticmethod
    def GetName():
        return _(u"MPEG(1/2)-Video (MPG)")
    
    @staticmethod
    def GetProperties():
        return LibAvRenderer.GetProperties()

    @staticmethod
    def GetDefaultProperty(prop):
        return LibAvRenderer.GetDefaultProperty(prop)

    def _GetCmd(self):
        cmd = ["avconv", "-y", "-f", "mjpeg", "-i", "pipe:0", "-r", "25"]
        cmd += self._GetAudioArgs()
        cmd += self._GetSubArgs()

        aspect = "%.3f" % Aspect.ToFloat(self._aspect)
        profile = self.GetProfile()

        if profile.GetVideoNorm() == OutputProfile.PAL:
            videonorm = "pal"
            keyint = 15
        else:
            videonorm = "ntsc"
            keyint = 18
            
        if profile.GetName() == "VCD":
            cmd += ["-target", '%s-vcd' % videonorm]
#            lavcopts = "vcodec=mpeg1video:keyint=%(keyint)s:vrc_buf_size=327:vrc_minrate=1152:vbitrate=1152:vrc_maxrate=1152:acodec=mp2:abitrate=224:aspect=%(aspect)s" % {"keyint": keyint,
#                                                                                                                                                                           "aspect": aspect}
        elif profile.GetName() == "SVCD":
            cmd += ["-target", '%s-svcd' % videonorm]
#            lavcopts = "vcodec=mpeg2video:mbd=2:keyint=%(keyint)s:vrc_buf_size=917:vrc_minrate=600:vbitrate=2500:vrc_maxrate=2500:acodec=mp2:abitrate=224:aspect=%(aspect)s" % {"keyint": keyint,
#                                                                                                                                                                                "aspect": aspect}
        elif profile.GetName() == "DVD":
            cmd += ["-target", '%s-dvd' % videonorm]
#            lavcopts = "vcodec=mpeg2video:vrc_buf_size=1835:vrc_maxrate=9800:vbitrate=5000:keyint=%(keyint)s:vstrict=0:acodec=ac3:abitrate=192:aspect=%(aspect)s" % {"keyint": keyint,
#                                                                                                                                                                     "aspect": aspect}
        else:
            raise RendererException(_(u'MPEG format supports only VCD, SVCD and DVD profile!'))
            
#              "-vf scale=%(resx)d:%(resy)d,harddup " \
#              "-of mpeg -mpegopts format=%(format)s " \
#              "-ofps %(framerate)s " \
        cmd += [os.path.join(self.GetOutputPath(), "output.mpg")]
        print cmd
        return cmd


class MPEG4AC3Renderer(LibAvRenderer):
    
    def __init__(self):
        LibAvRenderer.__init__(self)
        
    @staticmethod
    def GetName():
        return _(u"MPEG4-XVid/AC3 (AVI)")

    @staticmethod
    def GetProperties():
        return LibAvRenderer.GetProperties() + ["FFOURCC"]

    @staticmethod
    def GetDefaultProperty(prop):
        if prop == "FFOURCC":
            return "XVID"
        return LibAvRenderer.GetDefaultProperty(prop)

    def _GetCmd(self):
        cmd = ["avconv", "-y", "-f", "mjpeg", "-i", "pipe:0", "-r", "25"]
        cmd += self._GetAudioArgs()
        cmd += self._GetSubArgs()
        cmd += ["-c:a", "ac3", #"-srate", "44100",
                "-c:v", "libx264",
                "-b:v", "%sk" % self._GetBitrate(),
#                "-vf", "fps=%s" % self._GetFrameRate(), 
#                "-ffourcc", MPEG4AC3Renderer.GetProperty('FFOURCC'),
#                "-ofps", self._GetFrameRate(),
                os.path.join(self.GetOutputPath(), "output.avi")]
        return cmd


class MEncoderMP3Renderer(LibAvRenderer):
    
    def __init__(self):
        LibAvRenderer.__init__(self)
        
#     @staticmethod
#     def CheckDependencies(msgList):
#         LibAvRenderer.CheckDependencies(msgList)
#         if msgList:
#             return
#         
#         try:
#             proc = Popen(["mencoder", "-oac", "help"], stdout=PIPE, stderr=STDOUT, shell=False)
#             output = proc.communicate()[0]
#         except Exception, err:
#             logging.debug("checking for mencoder (mp3support) failed: %s", err)
#             output = ""
#            
#         if output.find("mp3lame") == -1:
#             msgList.append(_(u"mencoder with MP3 support (mp3lame) required!"))


class MPEG4MP3Renderer(MEncoderMP3Renderer):
    
    def __init__(self):
        MEncoderMP3Renderer.__init__(self)
        
    @staticmethod
    def GetName():
        return _(u"MPEG4-XVid/MP3 (AVI)")

    @staticmethod
    def GetProperties():
        return MEncoderMP3Renderer.GetProperties() + ["FFOURCC"]

    @staticmethod
    def GetDefaultProperty(prop):
        if prop == "FFOURCC":
            return "XVID"
        return MEncoderMP3Renderer.GetDefaultProperty(prop)

    def _GetCmd(self):
        cmd = ["avconv", "-y", "-f", "mjpeg", "-i", "pipe:0", "-r", "25"]
        cmd += self._GetAudioArgs()
        cmd += self._GetSubArgs()
        cmd += ["-c:a", "libmp3lame", "-ar", "44100",
                "-c:v", "libx264",
                "-b:v", "%sk" % self._GetBitrate(),
#                "-vf", "fps=%s" % self._GetFrameRate(), 
#                "-ffourcc", MPEG4AC3Renderer.GetProperty('FFOURCC'),
#                "-ofps", self._GetFrameRate(),
                os.path.join(self.GetOutputPath(), "output.avi")]
        return cmd

        
class FlashMovieRenderer(MEncoderMP3Renderer):
    
    def __init__(self):
        MEncoderMP3Renderer.__init__(self)
        
    @staticmethod
    def GetName():
        return _(u"Flash-Video (FLV)")
    
    @staticmethod
    def GetProperties():
        return MEncoderMP3Renderer.GetProperties()

    @staticmethod
    def GetDefaultProperty(prop):
        return MEncoderMP3Renderer.GetDefaultProperty(prop)

    def _GetCmd(self):
        cmd = ["mencoder", "-demuxer", "lavf", "-fps", "25", "-lavfdopts", "format=mjpeg"]
        cmd += self._GetAudioArgs()
        cmd += self._GetSubArgs()
        cmd += ["-oac", "mp3lame", "-lameopts", "cbr:br=128", "-srate", "44100",
                "-ovc", "lavc", 
                "-lavcopts", "vcodec=flv:vbitrate=%d:mbd=2:mv0:trell:v4mv:cbp:last_pred=3" % self._GetBitrate(),
                "-of", "lavf",
                "-ofps", self._GetFrameRate(),
                "-o", os.path.join(self.GetOutputPath(), "output.flv"),
                "-"]
        return cmd


class MJPEGRenderer(LibAvRenderer):
    
    def __init__(self):
        LibAvRenderer.__init__(self)
        
    @staticmethod
    def GetName():
        return _(u"Motion-JPEG (AVI)")
    
    @staticmethod
    def GetProperties():
        return LibAvRenderer.GetProperties()

    @staticmethod
    def GetDefaultProperty(prop):
        return LibAvRenderer.GetDefaultProperty(prop)

    def _GetCmd(self):
        cmd = ["mencoder", "-demuxer", "lavf", "-fps", "25", "-lavfdopts", "format=mjpeg"]
        cmd += self._GetAudioArgs()
        cmd += self._GetSubArgs()
        cmd += ["-oac", "pcm", "-srate", "44100",
                "-ovc", "lavc", 
                "-lavcopts", "vcodec=mjpeg",
                "-of", "lavf",
                "-ofps", self._GetFrameRate(),
                "-o", os.path.join(self.GetOutputPath(), "output.avi"),
                "-"]
        return cmd
