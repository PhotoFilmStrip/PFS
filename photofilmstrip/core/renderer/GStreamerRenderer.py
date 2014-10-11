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
from photofilmstrip.core.renderer.RendererException import RendererException


class GStreamerRenderer(BaseRenderer):
    
    def __init__(self):
        BaseRenderer.__init__(self)
        self.resQueue = Queue.Queue(20)
        
        self.active = None
        self.finished = None
        self.ready = None
        self.pipeline = None
        self.cur_time = 0
        
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
        return ["Bitrate"]

    @staticmethod
    def GetDefaultProperty(prop):
        return BaseRenderer.GetDefaultProperty(prop)

    def ProcessFinalize(self, pilImg):
        res = cStringIO.StringIO()
        pilImg.save(res, 'JPEG', quality=95)
        self.resQueue.put(res.getvalue())
    
    def __CleanUp(self):
        if self.ready is None:
            return
        
        self.ready.wait()
        self.ready = None
        self.active = None
        self.finished = None
        self.pipeline = None
        
    def ProcessAbort(self):
        if self.active:
            self.active = False
        
        self.__CleanUp()

    def Prepare(self):
        self.ready = threading.Event()
        self.active = True
        self.finished = False
        
        gobject.threads_init()
        outFile = os.path.join(self.GetOutputPath(), "output.mkv")

        gstSrc = ['appsrc name=src block=true caps="image/jpeg,framerate={0}"'.format(self._GetFrameRate()),
                  'jpegdec',
#                  'timeoverlay halign=left valign=bottom text="Stream time:" shaded-background=true',
                  'x264enc bitrate=%s' % self._GetBitrate()]
        if self.GetAudioFile():
            gstSrc.extend([
                  'queue',
                  'mux. filesrc location="{0}"'.format(self.GetAudioFile()),
                  'decodebin2',
                  'audioconvert',
                  'lamemp3enc target=bitrate bitrate=192',
#                  'avenc_ac3 bitrate=192000',
                  ])
        gstSrc.extend([
                  'matroskamux name=mux',
                  'filesink location="{0}"'.format(outFile)
                  ])
        
        gstString = " ! ".join(gstSrc)
        logging.debug('gst: %s', gstString)
        self.pipeline = gst.parse_launch(gstString)
        src = self.pipeline.get_by_name("src")
        src.connect("need-data", self._GstNeedData)
        
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self._GstOnMessage)
    
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
        logging.debug('need_data: %s - %s', need_bytes, self.cur_time)
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
#        buf.timestamp = self.cur_time * gst.MSECOND
#        buf.duration = self.duration * gst.MSECOND
        src.emit("push-buffer", buf)
        
#        self.cur_time += self.duration
        self.cur_time += 1

