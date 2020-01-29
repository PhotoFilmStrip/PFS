# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2014 Jens Goepfert
#

import logging
import time

from gi.repository import Gst

from photofilmstrip.core.GtkMainLoop import GtkMainLoop


class GPlayer:

    def __init__(self, filename):
        self.__filename = filename
        self.__pipeline = None
        self.__length = None
        self.__position = None

        self.__Identify()

    def __Identify(self):
        pipeline = Gst.Pipeline()

        fileSrc = Gst.ElementFactory.make("filesrc")
        fileSrc.set_property("location", self.__filename)
        audioDec = Gst.ElementFactory.make("decodebin")
        audioConv = Gst.ElementFactory.make("audioconvert")
        audioSink = Gst.ElementFactory.make("fakesink")

        pipeline.add(fileSrc)
        pipeline.add(audioDec)
        pipeline.add(audioConv)
        pipeline.add(audioSink)

        fileSrc.link(audioDec)
        audioConv.link(audioSink)

        audioDec.connect("pad-added", self._GstPadAdded, audioConv)

        pipeline.set_state(Gst.State.PLAYING)

        bus = pipeline.get_bus()
        hasResult = False
        while not hasResult:
            msg = bus.pop()
            if msg is None:
                time.sleep(0.001)
                continue
            hasResult, duration = pipeline.query_duration(Gst.Format.TIME)

        pipeline.set_state(Gst.State.NULL)

        self.__length = duration // Gst.MSECOND

    def GetFilename(self):
        return self.__filename

    def IsOk(self):
        return self.__length is not None

    def IsPlaying(self):
        return self.__pipeline is not None

    def Play(self):
        if self.__pipeline is None:
            pipeline = Gst.Pipeline()

            fileSrc = Gst.ElementFactory.make("filesrc")
            fileSrc.set_property("location", self.__filename)

            audioDec = Gst.ElementFactory.make("decodebin")
            audioConv = Gst.ElementFactory.make("audioconvert")
            audioResample = Gst.ElementFactory.make("audioresample")
            audioSink = Gst.ElementFactory.make("autoaudiosink")

            pipeline.add(fileSrc)
            pipeline.add(audioDec)
            pipeline.add(audioConv)
            pipeline.add(audioResample)
            pipeline.add(audioSink)

            fileSrc.link(audioDec)
            audioConv.link(audioResample)
            audioResample.link(audioSink)

            audioDec.connect("pad-added", self._GstPadAdded, audioConv)

            self.__pipeline = pipeline
            self.__pipeline.set_state(Gst.State.PLAYING)

            bus = self.__pipeline.get_bus()
            bus.add_signal_watch()
            bus.connect("message", self._GstOnMessage)

        GtkMainLoop.EnsureRunning()

    def Stop(self):
        self.Close()

    def Close(self):
        self.__pipeline.send_event(Gst.Event.new_eos())

    def GetLength(self):
        return self.__length

    def GetPosition(self):
        if self.__pipeline:
            hasResult, position = self.__pipeline.query_position(Gst.Format.TIME)
            if hasResult:
                return position // Gst.MSECOND

    def SetPosition(self, start):
        if self.__pipeline:
            nanoSecs = start * Gst.MSECOND
            self.__pipeline.seek(1.0, Gst.Format.TIME,
                          Gst.SeekFlags.FLUSH, Gst.SeekType.SET,
                          nanoSecs,
                          Gst.SeekType.NONE, 0)

    def _GstOnMessage(self, bus, msg):  # pylint: disable=unused-argument
        logging.debug('_GstOnMessage: %s', msg.type)

        if msg.type == Gst.MessageType.ERROR:
            err, debug = msg.parse_error()
            logging.error("Error received from element %s: %s",
                          msg.src.get_name(), err)
            logging.debug("Debugging information: %s", debug)

        elif msg.type == Gst.MessageType.EOS:
            self.__pipeline.set_state(Gst.State.NULL)
            self.__pipeline = None

    def _GstPadAdded(self, decodebin, pad, audioConv):  # pylint: disable=unused-argument
        caps = pad.get_current_caps()
        compatible_pad = audioConv.get_compatible_pad(pad, caps)
        pad.link(compatible_pad)
