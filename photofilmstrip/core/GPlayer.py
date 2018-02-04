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
import threading
import time

from gi.repository import Gst
from gi.repository import GObject


class GPlayer:

    def __init__(self, filename):
        self.__filename = filename
        self.__pipeline = None
        self.__length = None
        self.__gtkMainloop = None

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

        hasResult = False
        while not hasResult:
            msg = pipeline.get_bus().pop()
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
            audioSink = Gst.ElementFactory.make("autoaudiosink")

            pipeline.add(fileSrc)
            pipeline.add(audioDec)
            pipeline.add(audioConv)
            pipeline.add(audioSink)

            fileSrc.link(audioDec)
            audioConv.link(audioSink)

            audioDec.connect("pad-added", self._GstPadAdded, audioConv)

            self.__pipeline = pipeline
            self.__pipeline.set_state(Gst.State.PLAYING)

            bus = self.__pipeline.get_bus()
            bus.add_signal_watch()
            bus.connect("message", self._GstOnMessage)

        gtkMainloopThread = threading.Thread(name="gtkMainLoop",
                                             target=self._GtkMainloop)
        gtkMainloopThread.start()

    def Stop(self):
        self.Close()

    def Close(self):
        self.__pipeline.send_event(Gst.Event.new_eos())

    def GetLength(self):
        return self.__length

    def _GstOnMessage(self, bus, msg):  # pylint: disable=unused-argument
        logging.debug('_GstOnMessage: %s', msg.type)

        if msg.type == Gst.MessageType.ERROR:
            err, debug = msg.parse_error()
            logging.error("Error received from element %s: %s",
                          msg.src.get_name(), err)
            logging.debug("Debugging information: %s", debug)

        elif msg.type == Gst.MessageType.EOS:
            self.__pipeline.set_state(Gst.State.NULL)
            self.__gtkMainloop.quit()
            self.__pipeline = None
            self.__gtkMainloop = None

    def _GstPadAdded(self, decodebin, pad, audioConv):  # pylint: disable=unused-argument
        caps = pad.get_current_caps()
        compatible_pad = audioConv.get_compatible_pad(pad, caps)
        pad.link(compatible_pad)

    def _GtkMainloop(self):
        GObject.threads_init()
        self.__gtkMainloop = GObject.MainLoop()
        self.__gtkMainloop.run()
