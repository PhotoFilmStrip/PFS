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

from gi.repository import Gst
from gi.repository import GObject

from photofilmstrip.core.Aspect import Aspect
from photofilmstrip.core.OutputProfile import OutputProfile
from photofilmstrip.core.BaseRenderer import BaseRenderer, RendererException
from photofilmstrip.core.Subtitle import SrtParser


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
        self.ptsOffset = 0
        self.ptsLast = None

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
        '''
        ProcessFinalize is called from several worker threads and puts the new
        image data (JPEG) in a queue.
        :param pilImg:
        '''
        res = cStringIO.StringIO()
        pilImg.save(res, 'JPEG', quality=95)
        self.resQueue.put(res.getvalue())

    def __CleanUp(self):
        '''
        Waits until the ready event is set and finished the GTK-Mainloop.
        The ready event is set within _GstOnMessage if the end-of-stream event
        was handled.
        '''
        if self.ready is None:
            return

        self._Log(logging.DEBUG, "waiting for ready event")
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
        self.ptsOffset = 0
        self.ptsLast = None

        if not (self.__class__.GetProperty("RenderSubtitle").lower() in ["0", _(u"no"), "false"]):
            # delete subtitle file, if subtitle is rendered in video
            srtPath = os.path.join(self.GetOutputPath(), "output.srt")
            if os.path.exists(srtPath):
                os.remove(srtPath)

    def ProcessAbort(self):
        '''
        Called if the user aborts the rendering. Sets the active flag to false
        and waits until everything is cleaned up.
        '''
        if self.active:
            self.active = False

        self.__CleanUp()

    def Prepare(self):
        '''
        Build the gstreamer pipeline and all necessary objects and bindings.
        '''
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
            self.imgDuration = int(round(1000 * Gst.MSECOND / (30000.0 / 1001.0)))
        self._Log(logging.DEBUG, "set imgDuration=%s", self.imgDuration)

        outFile = os.path.join(self.GetOutputPath(),
                               "output.%s" % self._GetExtension())

        self.pipeline = Gst.Pipeline()

        caps = Gst.caps_from_string("image/jpeg,framerate={0}".format(frameRate))
        videoSrc = Gst.ElementFactory.make("appsrc")
        videoSrc.set_property("block", True)
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

        # link elements for video stream
        videoSrc.link(jpegDecoder)
        jpegDecoder.link(colorConverter)
        if self.textoverlay:
            colorConverter.link(self.textoverlay)
            self.textoverlay.link(queueVideo)
        else:
            colorConverter.link(queueVideo)
        queueVideo.link(videoEnc)

        audioEnc = None
        if self.GetAudioFiles():
            self.concat = Gst.ElementFactory.make("concat")
            self.pipeline.add(self.concat)

            srcpad = self.concat.get_static_pad("src")
            srcpad.add_probe(Gst.PadProbeType.BUFFER,  # | Gst.PadProbeType.EVENT_DOWNSTREAM,
                             self._GstProbeBuffer)

            self._GstAddAudioFile(self.GetAudioFiles()[self.idxAudioFile])

            audioConv = Gst.ElementFactory.make("audioconvert")
            self.pipeline.add(audioConv)

            audiorate = Gst.ElementFactory.make("audioresample")
            self.pipeline.add(audiorate)

            audioEnc = self._GetAudioEncoder()
            self.pipeline.add(audioEnc)

            self.concat.link(audioConv)
            audioConv.link(audiorate)
            audiorate.link(audioEnc)

        if self.GetProfile().IsMPEGProfile():
            vp = Gst.ElementFactory.make("mpegvideoparse")
            self.pipeline.add(vp)
            videoEnc.link(vp)
            videoEnc = vp

            if audioEnc:
                ap = Gst.ElementFactory.make("mpegaudioparse")
                self.pipeline.add(ap)
                audioEnc.link(ap)
                audioEnc = ap

        mux = self._GetMux()
        self.pipeline.add(mux)
        videoEnc.link(mux)
        if audioEnc:
            audioEnc.link(mux)

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
                                             target=self._GtkMainloop)
        gtkMainloopThread.start()

        self.ready.clear()

    def _GtkMainloop(self):
        self._Log(logging.DEBUG, "GTK mainloop starting...")
        self.gtkMainloop.run()
        self._Log(logging.DEBUG, "GTK mainloop finished")

    def _GstAddAudioFile(self, audioFile):
        '''
        Inserts new elements to refer a new audio file in the gstreamer pipeline.
        :param audioFile: the full path to the audio file
        '''
        audioSrc = Gst.ElementFactory.make("filesrc")
        audioSrc.set_property("location", audioFile)
        self.pipeline.add(audioSrc)

        audioDec = Gst.ElementFactory.make("decodebin")
        audioDec.connect("pad-added", self._GstPadAddedAudio)
        audioDec.connect("no-more-pads", self._GstNoMorePadsAudio)
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
        '''
        Gstreamer message handler for messages in gstreamer event bus.
        :param bus:
        :param msg:
        '''
        self._Log(logging.DEBUG, '_GstOnMessage: %s', msg.type)

        if msg.type == Gst.MessageType.ERROR:
            err, debug = msg.parse_error()
            self._Log(logging.ERROR, "Error received from element %s: %s",
                          msg.src.get_name(), err)
            self._Log(logging.DEBUG, "Debugging information: %s", debug)

        elif msg.type == Gst.MessageType.LATENCY:
            self.pipeline.recalculate_latency()

        elif msg.type == Gst.MessageType.EOS:
            self.pipeline.set_state(Gst.State.NULL)
            self.ready.set()
#         return Gst.BusSyncReply.PASS

    def _GstNeedData(self, src, need_bytes):
        '''
        Gstreamer need-data probe callback to feed the appsrc with image data.
        The image data comes from a queue that is filled from other worker
        threads. If the queue is empty and the finish flag is set send
        end-of-stream to the appsrc so the pipeline can finish its processing.
        If the textoverlay element is available the current text for the
        rendered subtitle will be set.
        :param src: GstElement appsrc
        :param need_bytes: unused size
        '''
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

    def _GstPadAddedAudio(self, decodebin, pad):
        '''
        Gstreamer pad-added probe callback to attach a new audio file to the
        pipeline.
        :param decodebin: GstElement decodebin (decoder for audio data)
        :param pad: GstPad object
        '''
        self._Log(logging.DEBUG, "_GstPadAddedAudio: %s - %s", decodebin, pad)
        caps = pad.get_current_caps()
        compatible_pad = self.concat.get_compatible_pad(pad, caps)
        pad.link(compatible_pad)

    def _GstNoMorePadsAudio(self, decodebin):
        self._Log(logging.DEBUG, "_GstNoMorePadsAudio: %s", decodebin)
        self.idxAudioFile += 1
        if self.idxAudioFile < len(self.GetAudioFiles()):
#             self.pipeline.set_state(Gst.State.PAUSED)
            self._GstAddAudioFile(self.GetAudioFiles()[self.idxAudioFile])
#             self.pipeline.set_state(Gst.State.PLAYING)

    def _GstProbeBuffer(self, srcPad, probeInfo):
        '''
        Gstreamer pad probe callback to check if the current stream time has
        reached the final time (usually the length of the overall audio stream).
        If final time has reached send eos event (end of stream) to finish the
        pipeline
        :param srcPad: src pad of the muxer
        :param probeInfo: GstPadProbeInfo object
        '''
        buf = probeInfo.get_buffer()
        self._Log(logging.DEBUG, "_GstProbeBuffer: buffer %s", (buf, buf.pts / Gst.MSECOND, self.ptsOffset / Gst.MSECOND, self.finalTime))
        if buf.pts < self.ptsLast:
            self.ptsOffset += self.ptsLast
        self.ptsLast = buf.pts

        if self.finalTime is None:
            return Gst.PadProbeReturn.PASS
        elif self.ptsOffset + buf.pts >= self.finalTime:
            return Gst.PadProbeReturn.DROP
        else:
            return Gst.PadProbeReturn.PASS

    def _GetExtension(self):
        raise NotImplementedError()
    def _GetMux(self):
        raise NotImplementedError()
    def _GetAudioEncoder(self):
        raise NotImplementedError()
    def _GetVideoEncoder(self):
        raise NotImplementedError()


class MkvX264AC3(_GStreamerRenderer):

    @staticmethod
    def GetName():
        return "x264/AC3 (MKV)"

    @staticmethod
    def CheckDependencies(msgList):
        _GStreamerRenderer.CheckDependencies(msgList)
        if not msgList:
            aEnc = Gst.ElementFactory.find("avenc_ac3")
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
#         audioEnc = Gst.ElementFactory.make("lamemp3enc")
        audioEnc = Gst.ElementFactory.make("avenc_ac3")
#         audioEnc = Gst.ElementFactory.make("lame")

#         audioEnc.set_property("target", "bitrate")
#         audioEnc.set_property("bitrate", 192)
        return audioEnc

    def _GetVideoEncoder(self):
        videoEnc = Gst.ElementFactory.make("x264enc")
        videoEnc.set_property("bitrate", self._GetBitrate())
        return videoEnc


class Mp4X264AAC(_GStreamerRenderer):

    @staticmethod
    def GetName():
        return "x264/AAC (MP4)"

    @staticmethod
    def CheckDependencies(msgList):
        _GStreamerRenderer.CheckDependencies(msgList)
        if not msgList:
            aEnc = Gst.ElementFactory.find("voaacenc")
            if aEnc is None:
                msgList.append(_(u"MP3-Codec (gstreamer1.0-plugins-bad) required!"))

            vEnc = Gst.ElementFactory.find("x264enc")
            if vEnc is None:
                msgList.append(_(u"x264-Codec (gstreamer1.0-plugins-ugly) required!"))

            mux = Gst.ElementFactory.find("flvmux")
            if mux is None:
                msgList.append(_(u"FLV-Muxer (gstreamer1.0-plugins-good) required!"))

    def _GetExtension(self):
        return "mp4"

    def _GetMux(self):
        mux = Gst.ElementFactory.make("flvmux")
        return mux

    def _GetAudioEncoder(self):
        audioEnc = Gst.ElementFactory.make("voaacenc")
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
