# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2014 Jens Goepfert
#

import logging
import os
import threading

import queue

from gi.repository import Gst
from gi.repository import GObject

from photofilmstrip.core.Aspect import Aspect
from photofilmstrip.core.OutputProfile import OutputProfile
from photofilmstrip.core.BaseRenderer import BaseRenderer
from photofilmstrip.core.Subtitle import SrtParser
from photofilmstrip.core.exceptions import RendererException


class _GStreamerRenderer(BaseRenderer):

    def __init__(self):
        BaseRenderer.__init__(self)
        self._Log = _GStreamerRenderer.Log
        self.resQueue = queue.Queue(20)

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
        self.concat = None
        self.ptsOffset = 0
        self.ptsLast = -1

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
        return ["Bitrate", "RenderSubtitle", "SubtitleSettings"]

    @staticmethod
    def GetDefaultProperty(prop):
        if prop == "RenderSubtitle":
            return "false"
        if prop == "SubtitleSettings":
            return ""
        return BaseRenderer.GetDefaultProperty(prop)

    def ToSink(self, data):
        self.resQueue.put(data)

    def GetOutputFile(self):
        outFile = '{0}.{1}'.format(self._outFile, self._GetExtension())
        return outFile

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
        self.concat = None
        self.ptsOffset = 0
        self.ptsLast = -1

        if self.GetTypedProperty("RenderSubtitle", bool):
            # delete subtitle file, if subtitle is rendered in video
            srtPath = self._outFile + ".srt"
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
        frameRate = self.GetProfile().GetFrameRate()
        # 1000ms / fps == x msec/frame
        self.imgDuration = int(round(1000 * Gst.MSECOND / frameRate.AsFloat()))
        self._Log(logging.DEBUG, "set imgDuration=%s", self.imgDuration)

        self.pipeline = Gst.Pipeline()

        caps = Gst.caps_from_string(
            "image/jpeg,framerate={0}".format(frameRate.AsStr()))
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

        if self.GetTypedProperty("RenderSubtitle", bool) and Gst.ElementFactory.find("textoverlay"):
            self.textoverlay = Gst.ElementFactory.make("textoverlay")
            self.textoverlay.set_property("text", "")
            self._SetupTextOverlay()
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

            audioQueue = Gst.ElementFactory.make("queue")
            self.pipeline.add(audioQueue)

            audioEnc = self._GetAudioEncoder()
            self.pipeline.add(audioEnc)

            self.concat.link(audioConv)
            audioConv.link(audiorate)
            audiorate.link(audioQueue)
            audioQueue.link(audioEnc)

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
        elif isinstance(self, MkvX265AC3):
            vp = Gst.ElementFactory.make("h265parse")
            self.pipeline.add(vp)
            videoEnc.link(vp)
            videoEnc = vp

        mux = self._GetMux()
        self.pipeline.add(mux)

        videoQueue2 = Gst.ElementFactory.make("queue")
        self.pipeline.add(videoQueue2)

        videoEncCaps = self._GetVideoEncoderCaps()
        if videoEncCaps:
            videoEnc.link_filtered(videoQueue2, videoEncCaps)
        else:
            videoEnc.link(videoQueue2)
        videoQueue2.link(mux)

        if audioEnc:
            audioQueue2 = Gst.ElementFactory.make("queue")
            self.pipeline.add(audioQueue2)
            audioEnc.link(audioQueue2)
            audioQueue2.link(mux)

        sink = Gst.ElementFactory.make("filesink")
        sink.set_property("location", self.GetOutputFile())
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

    def _GetBitrate(self):
        bitrate = self.GetTypedProperty("Bitrate", int,
                                        self.GetProfile().GetBitrate())
        if bitrate is None:
            raise RendererException(_(u"Bitrate must be a number!"))
        return bitrate

    def _GstOnMessage(self, bus, msg):  # pylint: disable=unused-argument
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

    def _GstNeedData(self, src, need_bytes):  # pylint: disable=unused-argument
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
            except queue.Empty:
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
                srtPath = self._outFile + ".srt"
                self.srtParse = SrtParser(
                    srtPath, self.GetProfile().GetFrameRate().AsFloat())

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

    def _GstProbeBuffer(self, srcPad, probeInfo):  # pylint: disable=unused-argument
        '''
        Gstreamer pad probe callback to check if the current stream time has
        reached the final time (usually the length of the overall audio stream).
        If final time has reached send eos event (end of stream) to finish the
        pipeline
        :param srcPad: src pad of the muxer
        :param probeInfo: GstPadProbeInfo object
        '''
        buf = probeInfo.get_buffer()
        self._Log(logging.DEBUG, "_GstProbeBuffer: buffer %s", (buf, buf.pts // Gst.MSECOND, self.ptsOffset // Gst.MSECOND, self.finalTime))
        if buf.pts < self.ptsLast:
            self.ptsOffset += self.ptsLast
        self.ptsLast = buf.pts

        if self.finalTime is None:
            return Gst.PadProbeReturn.PASS
        elif self.ptsOffset + buf.pts >= self.finalTime:
            return Gst.PadProbeReturn.DROP
        else:
            return Gst.PadProbeReturn.PASS

    def _SetupTextOverlay(self):
        settings = self.GetProperty("SubtitleSettings")
        for singleSetting in settings.split(";"):
            settingAndProp = singleSetting.split("=")
            if len(settingAndProp) == 2:
                prop, value = settingAndProp
                try:
                    # try number as int
                    value = int(value)
                except:  # pylint: disable-msg=bare-except
                    try:
                        # try numbers as hex
                        value = int(value, 16)
                    except:  # pylint: disable-msg=bare-except
                        pass
                self.textoverlay.set_property(prop, value)

    def _GetExtension(self):
        raise NotImplementedError()

    def _GetMux(self):
        raise NotImplementedError()

    def _GetAudioEncoder(self):
        raise NotImplementedError()

    def _GetVideoEncoder(self):
        raise NotImplementedError()

    def _GetVideoEncoderCaps(self):
        return None


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
                msgList.append(_(u"libav (gstreamer1.0-libav) required!"))

            vEnc = Gst.ElementFactory.find("x264enc")
            if vEnc is None:
                msgList.append(_(u"x264-Codec (gstreamer1.0-plugins-ugly) required!"))

            mux = Gst.ElementFactory.find("matroskamux")
            if mux is None:
                msgList.append(_(u"MKV-Muxer (gstreamer1.0-plugins-good) required!"))

    @staticmethod
    def GetDefaultProperty(prop):
        if prop == "Profile":
            return "high"
        elif prop == "HardwareEncoding":
            return "false"
        else:
            return _GStreamerRenderer.GetDefaultProperty(prop)

    @staticmethod
    def GetProperties():
        return _GStreamerRenderer.GetProperties() + [
            "SpeedPreset", "Profile", "HardwareEncoding"]

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
        if self.GetTypedProperty("HardwareEncoding", bool) and Gst.ElementFactory.find("vaapih264enc"):
            videoEnc = Gst.ElementFactory.make("vaapih264enc")
        else:
            videoEnc = Gst.ElementFactory.make("x264enc")
        videoEnc.set_property("bitrate", self._GetBitrate())

        speedPreset = self.GetTypedProperty("SpeedPreset", int)
        if speedPreset is not None:
            videoEnc.set_property("speed-preset", speedPreset)
        return videoEnc

    def _GetVideoEncoderCaps(self):
        profile = self.GetTypedProperty("Profile", str)
        if profile in ("main", "high", "baseline", "constrained-baseline"):
            caps = Gst.caps_from_string("video/x-h264,profile={}".format(profile))
            return caps
        elif profile:
            self._Log(logging.WARN,
                      "value '%s' for profile not supported!",
                      profile)
        return None


class Mp4X264AAC(_GStreamerRenderer):

    @staticmethod
    def GetName():
        return "x264/AAC (MP4)"

    @staticmethod
    def CheckDependencies(msgList):
        _GStreamerRenderer.CheckDependencies(msgList)
        if not msgList:
            aEnc = Gst.ElementFactory.find("avenc_aac")
            if aEnc is None:
                msgList.append(_(u"libav (gstreamer1.0-libav) required!"))

            vEnc = Gst.ElementFactory.find("x264enc")
            if vEnc is None:
                msgList.append(_(u"x264-Codec (gstreamer1.0-plugins-ugly) required!"))

            mux = Gst.ElementFactory.find("flvmux")
            if mux is None:
                msgList.append(_(u"FLV-Muxer (gstreamer1.0-plugins-good) required!"))

    @staticmethod
    def GetDefaultProperty(prop):
        if prop == "Profile":
            return "high"
        elif prop == "HardwareEncoding":
            return "false"
        else:
            return _GStreamerRenderer.GetDefaultProperty(prop)

    @staticmethod
    def GetProperties():
        return _GStreamerRenderer.GetProperties() + [
            "SpeedPreset", "Profile", "HardwareEncoding"]

    def _GetExtension(self):
        return "mp4"

    def _GetMux(self):
        mux = Gst.ElementFactory.make("flvmux")
        return mux

    def _GetAudioEncoder(self):
        audioEnc = Gst.ElementFactory.make("avenc_aac")
        return audioEnc

    def _GetVideoEncoder(self):
        if self.GetTypedProperty("HardwareEncoding", bool) and Gst.ElementFactory.find("vaapih264enc"):
            videoEnc = Gst.ElementFactory.make("vaapih264enc")
        else:
            videoEnc = Gst.ElementFactory.make("x264enc")
        videoEnc.set_property("bitrate", self._GetBitrate())
        speedPreset = self.GetTypedProperty("SpeedPreset", int)
        if speedPreset is not None:
            videoEnc.set_property("speed-preset", speedPreset)
        return videoEnc

    def _GetVideoEncoderCaps(self):
        profile = self.GetTypedProperty("Profile", str)
        if profile in ("main", "high", "baseline", "constrained-baseline"):
            caps = Gst.caps_from_string("video/x-h264,profile={}".format(profile))
            return caps
        elif profile:
            self._Log(logging.WARN,
                      "value '%s' for profile not supported!",
                      profile)
        return None


class MkvX265AC3(_GStreamerRenderer):

    @staticmethod
    def GetName():
        return "x265/AC3 (MKV)"

    @staticmethod
    def CheckDependencies(msgList):
        _GStreamerRenderer.CheckDependencies(msgList)
        if not msgList:
            aEnc = Gst.ElementFactory.find("avenc_ac3")
            if aEnc is None:
                msgList.append(_(u"libav (gstreamer1.0-libav) required!"))

            vEnc = Gst.ElementFactory.find("x265enc")
            if vEnc is None:
                msgList.append(_(u"x264-Codec (gstreamer1.0-plugins-ugly) required!"))

            mux = Gst.ElementFactory.find("matroskamux")
            if mux is None:
                msgList.append(_(u"MKV-Muxer (gstreamer1.0-plugins-good) required!"))

    @staticmethod
    def GetProperties():
        return _GStreamerRenderer.GetProperties() + ["SpeedPreset"]

    def _GetExtension(self):
        return "mkv"

    def _GetMux(self):
        mux = Gst.ElementFactory.make("matroskamux")
        return mux

    def _GetAudioEncoder(self):
        audioEnc = Gst.ElementFactory.make("avenc_ac3")
        return audioEnc

    def _GetVideoEncoder(self):
        videoEnc = Gst.ElementFactory.make("x265enc")
        videoEnc.set_property("bitrate", self._GetBitrate())
        speedPreset = self.GetTypedProperty("SpeedPreset", int)
        if speedPreset is not None:
            videoEnc.set_property("speed-preset", speedPreset)
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
                msgList.append(_(u"MPEG-1/2-Codec (gstreamer1.0-plugins-bad) required!"))

            aEnc = Gst.ElementFactory.find("avenc_mp2")
            if aEnc is None:
                msgList.append(_(u"libav (gstreamer1.0-libav) required!"))

            mux = Gst.ElementFactory.find("mpegtsmux")
            if mux is None:
                msgList.append(_(u"MPEG-Muxer (gstreamer1.0-plugins-bad) required!"))

    def _GetExtension(self):
        return "mpg"

    def _GetMux(self):
        mux = Gst.ElementFactory.make("mpegtsmux")
        return mux

    def _GetAudioEncoder(self):
        audioEnc = Gst.ElementFactory.make("avenc_mp2")
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
                msgList.append(_(u"MPEG-1/2-Codec (gstreamer1.0-plugins-bad) required!"))

            aEnc = Gst.ElementFactory.find("avenc_mp2")
            if aEnc is None:
                msgList.append(_(u"libav (gstreamer1.0-libav) required!"))

            mux = Gst.ElementFactory.find("mpegtsmux")
            if mux is None:
                msgList.append(_(u"MPEG-Muxer (gstreamer1.0-plugins-bad) required!"))

    def _GetExtension(self):
        return "mpg"

    def _GetMux(self):
        mux = Gst.ElementFactory.make("mpegtsmux")
        return mux

    def _GetAudioEncoder(self):
        audioEnc = Gst.ElementFactory.make("avenc_mp2")
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
                msgList.append(_(u"MPEG-1/2-Codec (gstreamer1.0-plugins-bad) required!"))

            aEnc = Gst.ElementFactory.find("avenc_mp2")
            if aEnc is None:
                msgList.append(_(u"libav (gstreamer1.0-libav) required!"))

            mux = Gst.ElementFactory.find("mpegtsmux")
            if mux is None:
                msgList.append(_(u"MPEG-Muxer (gstreamer1.0-plugins-bad) required!"))

    def _GetExtension(self):
        return "mpg"

    def _GetMux(self):
        mux = Gst.ElementFactory.make("mpegtsmux")
        return mux

    def _GetAudioEncoder(self):
        audioEnc = Gst.ElementFactory.make("avenc_mp2")
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
