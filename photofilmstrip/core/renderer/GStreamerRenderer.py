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
import threading

import Queue
import cStringIO

import gi
gi.require_version('Gst', '1.0')

from gi.repository import Gst
from gi.repository import GObject

Gst.init(None)

from photofilmstrip.core.Aspect import Aspect
from photofilmstrip.core.OutputProfile import OutputProfile
from photofilmstrip.core.BaseRenderer import BaseRenderer, RendererException
from photofilmstrip.core.Subtitle import SrtParser


NOT_SET = object()


class _GStreamerRenderer(BaseRenderer):
    
    def __init__(self):
        BaseRenderer.__init__(self)
        self._Log = _GStreamerRenderer.Log
        self.resQueue = Queue.Queue(20)
        
        self.active = None
        self.finished = None
        self.ready = None
        self.pipeline = None
        self.idxFrame = 0
        self.idxAudioFile = 0
        self.imgDuration = None
        self.finalTime = None
        self.gtkMainloop = None
        self.textoverlay = None
        self.srtParse = None
        
    @staticmethod
    def CheckDependencies(msgList):
        if Gst is None or GObject is None:
            _GStreamerRenderer.Log(logging.DEBUG, "checking for gstreamer failed!")
            msgList.append(_(u"GStreamer (python-gst-1.0) required!"))
        else:
            to = Gst.ElementFactory.find("textoverlay")
            if to is None:
                _GStreamerRenderer.Log(logging.WARN, "GStreamer element textoverlay not found! Subtitles cannot rendered into video file.")

    @staticmethod
    def GetProperties():
        return ["Bitrate", "RenderSubtitle"]

    @staticmethod
    def GetDefaultProperty(prop):
        if prop == "RenderSubtitle":
            return "false"
        return BaseRenderer.GetDefaultProperty(prop)

    def ProcessFinalize(self, pilImg):
        res = cStringIO.StringIO()
        pilImg.save(res, 'JPEG', quality=95)
        self.resQueue.put(res.getvalue())
    
    def __CleanUp(self):
        if self.ready is None:
            return
        
        self.ready.wait()
        self.gtkMainloop.quit()
        
        self.active = None
        self.finished = None
        self.ready = None
        self.pipeline = None
        self.idxFrame = 0
        self.idxAudioFile = 0
        self.imgDuration = None
        self.finalTime = None
        self.gtkMainloop = None
        self.textoverlay = None
        self.srtParse = None
        
        if not (self.__class__.GetProperty("RenderSubtitle").lower() in ["0", _(u"no"), "false"]):
            # delete subtitle file, if subtitle is rendered in video
            srtPath = os.path.join(self.GetOutputPath(), "output.srt")
            if os.path.exists(srtPath):
                os.remove(srtPath)

    def ProcessAbort(self):
        if self.active:
            self.active = False
        
        self.__CleanUp()

    def Prepare(self):
        GObject.threads_init()

        self.ready = threading.Event()
        self.ready.set()
        
        self.active = True
        self.finished = False
        frameRate = self._GetFrameRate()
        if frameRate == "25/1":
            # 1000ms / 25fps == 40msec/frame
            self.imgDuration = 1000 * Gst.MSECOND / 25
        elif frameRate == "30000/1001":
            # 1000ms / 29.97fps == 33,367msec/frame
            self.imgDuration = int(round(1000 * Gst.MSECOND / (30000.0/1001.0)))
        self._Log(logging.DEBUG, "set imgDuration=%s", self.imgDuration)
        
        outFile = os.path.join(self.GetOutputPath(), 
                               "output.%s" % self._GetExtension())
        
        self.pipeline = Gst.Pipeline("pipeline")
        
        caps = Gst.Caps("image/jpeg,framerate={0}".format(frameRate))
        videoSrc = Gst.ElementFactory.make("appsrc")
        videoSrc.set_property("block", "true")
        videoSrc.set_property("caps", caps)
        videoSrc.connect("need-data", self._GstNeedData)
        self.pipeline.add(videoSrc)

        queueVideo = Gst.ElementFactory.make("queue")
        self.pipeline.add(queueVideo)

        jpegDecoder = Gst.ElementFactory.make("jpegdec")
        self.pipeline.add(jpegDecoder)

        colorConverter = Gst.ElementFactory.make("videoconvert")
        self.pipeline.add(colorConverter)

        videoEnc = self._GetVideoEncoder()
        self.pipeline.add(videoEnc)
        
        if not (self.__class__.GetProperty("RenderSubtitle").lower() in ["0", _(u"no"), "false"]) and Gst.ElementFactory.find("textoverlay"):
            self.textoverlay = Gst.ElementFactory.make("textoverlay")
            self.textoverlay.set_property("text", "")
            self.pipeline.add(self.textoverlay)

        mux = self._GetMux()
        self.pipeline.add(mux)

        # link elements for video stream
        videoSrc.link(jpegDecoder)
        jpegDecoder.link(colorConverter)
        if self.textoverlay:
            colorConverter.link(self.textoverlay)
            self.textoverlay.link(queueVideo)
        else:
            colorConverter.link(queueVideo)
        queueVideo.link(videoEnc)
        videoEnc.link(mux)
        

        if self.GetAudioFiles():
            self.concat = Gst.ElementFactory.make("concat")
            self.pipeline.add(self.concat)

            self._GstAddAudioFile(self.GetAudioFiles()[self.idxAudioFile])

            queueAudio = Gst.ElementFactory.make("queue")
            self.pipeline.add(queueAudio)
            
            audioConv = Gst.ElementFactory.make("audioconvert")
            self.pipeline.add(audioConv)

            audiorate = Gst.ElementFactory.make("audioresample")
            self.pipeline.add(audiorate)

            audioEnc = self._GetAudioEncoder()
            self.pipeline.add(audioEnc)

            self.concat.link(queueAudio)
            queueAudio.link(audioConv)
            audioConv.link(audiorate)
            audiorate.link(audioEnc)
            audioEnc.link(mux)

            srcpad = mux.get_static_pad('src')
            srcpad.add_probe(Gst.PadProbeType.BUFFER, 
                             self._GstProbeBuffer, 
                             audioConv)


        sink = Gst.ElementFactory.make("filesink")
        sink.set_property("location", outFile)
        self.pipeline.add(sink)

        mux.link(sink)

        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self._GstOnMessage)

        self.pipeline.set_state(Gst.State.PLAYING)
        
        self.gtkMainloop = GObject.MainLoop()
        gtkMainloopThread = threading.Thread(name="gtkMainLoop",
                                             target=self.gtkMainloop.run)
        gtkMainloopThread.start()
        
        self.ready.clear()
        
    def _GstAddAudioFile(self, audioFile):
        audioSrc = Gst.ElementFactory.make("filesrc")
        audioSrc.set_property("location", audioFile)
        self.pipeline.add(audioSrc)

        audioDec = Gst.ElementFactory.make("decodebin")
        audioDec.connect("pad-added", self._GstPadAdded)
        self.pipeline.add(audioDec)

        audioSrc.link(audioDec)

    def Finalize(self):
        if not self.finished:
            self.finished = True

        self.__CleanUp()
        
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

    def _GstOnMessage(self, bus, msg):
        self._Log(logging.DEBUG, '_GstOnMessage: %s', msg.type)

        if msg.type == Gst.MessageType.ERROR:
            err, debug = msg.parse_error()
            self._Log(logging.ERROR, "Error received from element %s: %s", 
                          msg.src.get_name(), err)
            self._Log(logging.DEBUG, "Debugging information: %s", debug)

        elif msg.type == Gst.MessageType.EOS:
            self.pipeline.set_state(Gst.State.NULL)
            self.ready.set()
#         return Gst.BusSyncReply.PASS

    def _GstNeedData(self, src, need_bytes):
        self._Log(logging.DEBUG, '_GstNeedData: %s', self.idxFrame)
        
        pts = self.idxFrame * self.imgDuration

        while self.active:
            result = None
            try:
                result = self.resQueue.get(True, 0.25)
                break
            except Queue.Empty:
                self._Log(logging.DEBUG, '_GstNeedData: Queue.Empty')
                if self.finished:
                    self._Log(logging.DEBUG, '_GstNeedData: finished, emitting end-of-stream (finalTime %s)', pts)
                    self.finalTime = pts
                    src.emit("end-of-stream")
                    return
                else:
                    continue
        else:
            self._Log(logging.DEBUG, '_GstNeedData: not active anymore, emitting end-of-stream (finalTime %s)', pts)
            self.finalTime = pts
            src.emit("end-of-stream")
            return
        
        self._Log(logging.DEBUG, '_GstNeedData: push to buffer (%s)', len(result))
                
        buf = Gst.Buffer.new_wrapped(result)
        buf.pts = pts
        buf.duration = self.imgDuration
        ret = src.emit("push-buffer", buf)
        if ret != Gst.FlowReturn.OK:
            return

        if self.textoverlay:
#             self.textoverlay.set_property("text", "Frame: %s" % self.idxFrame)
            if self.srtParse is None:
                srtPath = os.path.join(self.GetOutputPath(), "output.srt")
                self.srtParse = SrtParser(srtPath, self.GetProfile().GetFramerate())

            subtitle = self.srtParse.Get(self.idxFrame)
            self.textoverlay.set_property("text", subtitle)

        self.idxFrame += 1
        
    def _GstPadAdded(self, decodebin, pad):
        caps = pad.get_current_caps()
        compatible_pad = self.concat.get_compatible_pad(pad, caps)
        pad.link(compatible_pad)

        self.idxAudioFile += 1
        if self.idxAudioFile < len(self.GetAudioFiles()):
            self._GstAddAudioFile(self.GetAudioFiles()[self.idxAudioFile])

    def _GstProbeBuffer(self, srcPad, probeInfo, audioConv):
        buf = probeInfo.get_buffer()
        if self.finalTime is None:
            return True
        elif self.finalTime is NOT_SET:
            self._Log(logging.DEBUG, "_GstProbeBuffer: noop %s - %s", buf.pts, self.finalTime)
            return True
        elif buf.pts >= self.finalTime:
            self._Log(logging.DEBUG, "_GstProbeBuffer: send eos to audio stream %s - %s", buf.pts, self.finalTime)
            audioConv.send_event(Gst.Event.new_eos())
            self.finalTime = NOT_SET
            return True
        else:
            self._Log(logging.DEBUG, "_GstProbeBuffer: finishing audio buffer %s - %s", buf.pts, self.finalTime)
            return True

    def _GetExtension(self):
        raise NotImplementedError()
    def _GetMux(self):
        raise NotImplementedError()
    def _GetAudioEncoder(self):
        raise NotImplementedError()
    def _GetVideoEncoder(self):
        raise NotImplementedError()


class MkvX264MP3(_GStreamerRenderer):

    @staticmethod
    def GetName():
        return "x264/MP3 (MKV)"
    
    @staticmethod
    def CheckDependencies(msgList):
        _GStreamerRenderer.CheckDependencies(msgList)
        if not msgList:
            aEnc = Gst.ElementFactory.find("lamemp3enc")
            if aEnc is None:
                msgList.append(_(u"MP3-Codec (gstreamer1.0-plugins-ugly) required!"))
                
            vEnc = Gst.ElementFactory.find("x264enc")
            if vEnc is None:
                msgList.append(_(u"x264-Codec (gstreamer1.0-plugins-ugly) required!"))
            
            mux = Gst.ElementFactory.find("matroskamux")
            if mux is None:
                msgList.append(_(u"MKV-Muxer (gstreamer1.0-plugins-good) required!"))

    def _GetExtension(self):
        return "mkv"
    
    def _GetMux(self):
        mux = Gst.ElementFactory.make("matroskamux")
        return mux    
        
    def _GetAudioEncoder(self):
        audioEnc = Gst.ElementFactory.make("avenc_ac3")
#         audioEnc = Gst.ElementFactory.make("lame")
#         audioEnc.set_property("target", "bitrate")
        audioEnc.set_property("bitrate", 192000)
        return audioEnc

    def _GetVideoEncoder(self):
        videoEnc = Gst.ElementFactory.make("x264enc")
        videoEnc.set_property("bitrate", self._GetBitrate())
        return videoEnc


class OggTheoraVorbis(_GStreamerRenderer):
    
    @staticmethod
    def GetName():
        return "Theora/Vorbis (OGV)"
    
    @staticmethod
    def CheckDependencies(msgList):
        _GStreamerRenderer.CheckDependencies(msgList)
        if not msgList:
            aEnc = Gst.ElementFactory.find("theoraenc")
            if aEnc is None:
                msgList.append(_(u"Theora-Codec (gstreamer1.0-plugins-base) required!"))
                
            vEnc = Gst.ElementFactory.find("vorbisenc")
            if vEnc is None:
                msgList.append(_(u"Vorbis-Codec (gstreamer1.0-plugins-base) required!"))
            
            mux = Gst.ElementFactory.find("oggmux")
            if mux is None:
                msgList.append(_(u"OGV-Muxer (gstreamer1.0-plugins-base) required!"))
    
    def _GetExtension(self):
        return "ogv"
    
    def _GetMux(self):
        mux = Gst.ElementFactory.make("oggmux")
        return mux    
        
    def _GetAudioEncoder(self):
        audioEnc = Gst.ElementFactory.make("vorbisenc")
        return audioEnc
        
    def _GetVideoEncoder(self):
        videoEnc = Gst.ElementFactory.make("theoraenc")
        videoEnc.set_property("bitrate", self._GetBitrate())
        return videoEnc
        
        
class VCDFormat(_GStreamerRenderer):
    
    @staticmethod
    def GetName():
        return "VCD (MPG)"
    
    @staticmethod
    def CheckDependencies(msgList):
        _GStreamerRenderer.CheckDependencies(msgList)
        if not msgList:
            vEnc = Gst.ElementFactory.find("mpeg2enc")
            if vEnc is None:
                msgList.append(_(u"MPEG-1/2-Codec (gstreamer0.10-plugins-bad) required!"))

            aEnc = Gst.ElementFactory.find("twolamemp2enc")
            if aEnc is None:
                msgList.append(_(u"TwoLAME-Codec (gstreamer1.0-plugins-bad) required!"))

            mux = Gst.ElementFactory.find("mpegtsmux")
            if mux is None:
                msgList.append(_(u"MPEG-Muxer (gstreamer1.0-plugins-bad) required!"))
    
    def _GetExtension(self):
        return "mpg"
    
    def _GetMux(self):
        mux = Gst.ElementFactory.make("mpegtsmux")
        return mux    
        
    def _GetAudioEncoder(self):
        audioEnc = Gst.ElementFactory.make("twolamemp2enc")
        return audioEnc
        
    def _GetVideoEncoder(self):
        videoEnc = Gst.ElementFactory.make("mpeg2enc")
        videoEnc.set_property("format", 1)
        videoEnc.set_property("norm", "p" if self.GetProfile().GetVideoNorm() == OutputProfile.PAL else "n")
        return videoEnc


class SVCDFormat(_GStreamerRenderer):
    
    @staticmethod
    def GetName():
        return "SVCD (MPG)"
    
    @staticmethod
    def CheckDependencies(msgList):
        _GStreamerRenderer.CheckDependencies(msgList)
        if not msgList:
            vEnc = Gst.ElementFactory.find("mpeg2enc")
            if vEnc is None:
                msgList.append(_(u"MPEG-1/2-Codec (gstreamer0.10-plugins-bad) required!"))

            aEnc = Gst.ElementFactory.find("twolamemp2enc")
            if aEnc is None:
                msgList.append(_(u"TwoLAME-Codec (gstreamer1.0-plugins-bad) required!"))

            mux = Gst.ElementFactory.find("mpegtsmux")
            if mux is None:
                msgList.append(_(u"MPEG-Muxer (gstreamer1.0-plugins-bad) required!"))
    
    def _GetExtension(self):
        return "mpg"
    
    def _GetMux(self):
        mux = Gst.ElementFactory.make("mpegtsmux")
        return mux    
        
    def _GetAudioEncoder(self):
        audioEnc = Gst.ElementFactory.make("twolamemp2enc")
        return audioEnc
        
    def _GetVideoEncoder(self):
        videoEnc = Gst.ElementFactory.make("mpeg2enc")
        videoEnc.set_property("format", 4)
        videoEnc.set_property("norm", "p" if self.GetProfile().GetVideoNorm() == OutputProfile.PAL else "n")
        if self._aspect == Aspect.ASPECT_16_9:
            gstAspect = 3
        elif self._aspect == Aspect.ASPECT_4_3:
            gstAspect = 2
        else:
            gstAspect = 0
        videoEnc.set_property("aspect", gstAspect)
        videoEnc.set_property("dummy-svcd-sof", 0)
        videoEnc.set_property("bitrate", self._GetBitrate())
        return videoEnc


class DVDFormat(_GStreamerRenderer):
    
    @staticmethod
    def GetName():
        return "DVD (MPG)"
    
    @staticmethod
    def CheckDependencies(msgList):
        _GStreamerRenderer.CheckDependencies(msgList)
        if not msgList:
            vEnc = Gst.ElementFactory.find("mpeg2enc")
            if vEnc is None:
                msgList.append(_(u"MPEG-1/2-Codec (gstreamer0.10-plugins-bad) required!"))

            aEnc = Gst.ElementFactory.find("twolamemp2enc")
            if aEnc is None:
                msgList.append(_(u"TwoLAME-Codec (gstreamer1.0-plugins-bad) required!"))

            mux = Gst.ElementFactory.find("mpegtsmux")
            if mux is None:
                msgList.append(_(u"MPEG-Muxer (gstreamer1.0-plugins-bad) required!"))
    
    def _GetExtension(self):
        return "mpg"
    
    def _GetMux(self):
        mux = Gst.ElementFactory.make("mpegtsmux")
        return mux    
        
    def _GetAudioEncoder(self):
        audioEnc = Gst.ElementFactory.make("twolamemp2enc")
        return audioEnc
        
    def _GetVideoEncoder(self):
        videoEnc = Gst.ElementFactory.make("mpeg2enc")
        videoEnc.set_property("format", 8)
        videoEnc.set_property("norm", "p" if self.GetProfile().GetVideoNorm() == OutputProfile.PAL else "n")
        if self._aspect == Aspect.ASPECT_16_9:
            gstAspect = 3
        elif self._aspect == Aspect.ASPECT_4_3:
            gstAspect = 2
        else:
            gstAspect = 0
        videoEnc.set_property("aspect", gstAspect)
        videoEnc.set_property("bitrate", self._GetBitrate())
        return videoEnc
