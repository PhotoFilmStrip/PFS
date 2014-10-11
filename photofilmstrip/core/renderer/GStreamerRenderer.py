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

try:
    import pygst
    pygst.require("0.10")
    import gst
    import gobject
except ImportError:
    pygst = None
    gst = None

from photofilmstrip.core.OutputProfile import OutputProfile
from photofilmstrip.core.BaseRenderer import BaseRenderer
from photofilmstrip.core.Subtitle import SubtitleParser
from photofilmstrip.core.renderer.RendererException import RendererException


class GStreamerRenderer(BaseRenderer):
    
    def __init__(self):
        BaseRenderer.__init__(self)
        self.resQueue = Queue.Queue(20)
        
        self.active = None
        self.finished = None
        self.ready = None
        self.pipeline = None
        self.curFrame = 0
        
        self.audioConv = None
        self.textoverlay = None
        self.srtParse = None
        
    @staticmethod
    def GetName():
        return "x264/MP3 (MKV)"
    
    @staticmethod
    def CheckDependencies(msgList):
        if pygst is None or gst is None:
            logging.debug("checking for gstreamer failed: %s")
            msgList.append(_(u"GStreamer (python-gst0.10) required!"))

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
        
        self.srtParse = None
        self.ready = None
        self.active = None
        self.finished = None
        self.curFrame = 0
        
        self.pipeline = None
        self.audioConv = None
        self.textoverlay = None
        
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
        self.ready = threading.Event()
        self.active = True
        self.finished = False
        
        outFile = os.path.join(self.GetOutputPath(), "output.mkv")
        
        gobject.threads_init()
        
        self.pipeline = gst.Pipeline("pipeline")
        
        videoSrc = gst.element_factory_make("appsrc", "vsource")
        videoSrc.set_property("block", "true")
        caps = gst.Caps("image/jpeg,framerate={0}".format(self._GetFrameRate()))
        videoSrc.set_property("caps", caps)
        videoSrc.connect("need-data", self._GstNeedData)
        self.pipeline.add(videoSrc)
        
        jpegDecoder = gst.element_factory_make("jpegdec", None)
        self.pipeline.add(jpegDecoder)
        videoSrc.link(jpegDecoder)

        x264Enc = gst.element_factory_make("x264enc", None)
        x264Enc.set_property("bitrate", self._GetBitrate())
        self.pipeline.add(x264Enc)
        
        if not (self.__class__.GetProperty("RenderSubtitle").lower() in ["0", _(u"no"), "false"]):
            self.textoverlay = gst.element_factory_make("textoverlay", None)
            self.textoverlay.set_property("text", "")
            self.pipeline.add(self.textoverlay)
            
            jpegDecoder.link(self.textoverlay)
            self.textoverlay.link(x264Enc)
        else:
            jpegDecoder.link(x264Enc)

        mux = gst.element_factory_make("matroskamux", "mux")
        self.pipeline.add(mux)

        x264Enc.link(mux)
        
        if self.GetAudioFile():
            audioSrc = gst.element_factory_make("filesrc", None)
            audioSrc.set_property("location", self.GetAudioFile())
            self.pipeline.add(audioSrc)
                        
            audioDec = gst.element_factory_make("decodebin2", None)
            self.pipeline.add(audioDec)
            
            audioConv = gst.element_factory_make("audioconvert", None)
            self.pipeline.add(audioConv)
            
            audioEnc = gst.element_factory_make("lamemp3enc", None)
            audioEnc.set_property("target", "bitrate")
            audioEnc.set_property("bitrate", 192)
            self.pipeline.add(audioEnc)

            gst.element_link_many(audioSrc, audioDec)
            gst.element_link_many(audioConv, audioEnc, mux)

            self.audioConv = audioConv
            
        sink = gst.element_factory_make("filesink", None)
        sink.set_property("location", outFile)
        self.pipeline.add(sink)
        
        mux.link(sink)
        
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self._GstOnMessage)
        
        if self.audioConv:
            audioDec.connect("pad-added", self._GstPadAdded)
    
        self.pipeline.set_state(gst.STATE_PLAYING)
        
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
        logging.debug('on_message - %s - %s', bus, msg)
        if msg.type == gst.MESSAGE_EOS:
            self.pipeline.set_state(gst.STATE_NULL)
            self.ready.set()
            
    def _GstNeedData(self, src, need_bytes):
        logging.debug('need_data: %s - %s', need_bytes, self.curFrame)
        
        while self.active:
            result = None
            try:
                result = self.resQueue.get(True, 0.25)
                break
            except Queue.Empty:
                logging.debug('need_data: Queue.Empty')
                if self.finished:
                    logging.debug('need_data: finished, emitting end-of-stream')
                    src.emit("end-of-stream")
                    return
                else:
                    continue
        else:
            logging.debug('need_data: not active anymore, emitting end-of-stream')
            src.emit("end-of-stream")
            return
        
        logging.debug('need_data: push to buffer (%s)', len(result))
                
        buf = gst.Buffer(result)
        src.emit("push-buffer", buf)

        if self.textoverlay:
#             self.textoverlay.set_property("text", "Frame: %s" % self.curFrame)
            if self.srtParse is None:
                srtPath = os.path.join(self.GetOutputPath(), "output.srt")
                self.srtParse = SubtitleParser(srtPath, self.GetProfile().GetFramerate())
                
            subtitle = self.srtParse.Get(self.curFrame)
            self.textoverlay.set_property("text", subtitle)

        self.curFrame += 1
        
    def _GstPadAdded(self, decodebin, pad):
        caps = pad.get_caps()
        compatible_pad = self.audioConv.get_compatible_pad(pad, caps)
        pad.link(compatible_pad)
