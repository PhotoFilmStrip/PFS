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
import os, time, thread, threading
import multiprocessing

import Queue
import cStringIO


import gobject
import pygst
pygst.require("0.10")
import gst

from photofilmstrip.core.OutputProfile import OutputProfile
from photofilmstrip.core.BaseRenderer import BaseRenderer


class GStreamerWorker(threading.Thread):
    
    def __init__(self, resQueue, outFile, audioFile, framerate):
#        multiprocessing.Process.__init__(self)
        threading.Thread.__init__(self)
        self.resQueue = resQueue
        self.outFile = outFile
        self.audioFile = audioFile
        self.framerate = framerate

        self.active = True
        self.finished = False
        self.mainloop = None
        self.pipeline = None

        self.cur_time = 0
        gobject.threads_init()
        
    def run(self):
        self.mainloop = gobject.MainLoop()
        
        gstSrc = ['appsrc name=src block=true caps="image/jpeg,framerate={0}"'.format(self.framerate),
                  'jpegdec',
#                  'timeoverlay halign=left valign=bottom text="Stream time:" shaded-background=true',
                  'x264enc']
        if self.audioFile:
            gstSrc.extend([
                  'queue',
                  'mux. filesrc location="{0}"'.format(self.audioFile),
                  'decodebin2',
                  'audioconvert',
                  'lamemp3enc target=bitrate bitrate=192',
#                  'avenc_ac3 bitrate=192000',
                  ])
        gstSrc.extend([
                  'matroskamux name=mux',
                  'filesink location="{0}"'.format(self.outFile)
                  ])
        
        gstString = " ! ".join(gstSrc)
        logging.debug('gst: %s', gstString)
        self.pipeline = gst.parse_launch(gstString)
        src = self.pipeline.get_by_name("src")
        src.connect("need-data", self.need_data)
        
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message", self.on_message)
    
        self.pipeline.set_state(gst.STATE_PLAYING)
        
        self.mainloop.run()
        logging.debug('gobject mainloop finished')
        
    def on_message(self, bus, msg):
        logging.debug('on_message - %s - %s', bus, msg)
        if msg.type == gst.MESSAGE_EOS:
            self.pipeline.set_state(gst.STATE_NULL)
            self.mainloop.quit()
            
    def need_data(self, src, need_bytes):
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


class GStreamerRenderer(BaseRenderer):
    
    def __init__(self):
        BaseRenderer.__init__(self)
        self.resQueue = Queue.Queue(20)
        
        self.gstreamerWorker = None
        
    @staticmethod
    def GetName():
        return "GStreamer MKV (h264)"
    
    @staticmethod
    def CheckDependencies(msgList):
        try:
            pass
        except ImportError, err:
            logging.debug("checking for open-cv failed: %s", err)
            output = ""
            msgList.append(_(u"Open-CV (python-opencv) required!"))

    @staticmethod
    def GetProperties():
        return []

    @staticmethod
    def GetDefaultProperty(prop):
        return BaseRenderer.GetDefaultProperty(prop)

    def ProcessFinalize(self, pilImg):
        res = cStringIO.StringIO()
        pilImg.save(res, 'JPEG', quality=95)
        self.resQueue.put(res.getvalue())
    
    def __CleanUp(self):
        if self.gstreamerWorker is None:
            return
        
        self.gstreamerWorker.join()
        self.gstreamerWorker = None
        
    def ProcessAbort(self):
        if self.gstreamerWorker:
            self.gstreamerWorker.active = False
        self.__CleanUp()

    def Prepare(self):
        outFile = os.path.join(self.GetOutputPath(), "output.mkv")

        self.gstreamerWorker = GStreamerWorker(self.resQueue, 
                                               outFile, 
                                               self.GetAudioFile(),
                                               self._GetFrameRate())
        self.gstreamerWorker.start()
        
    def Finalize(self):
        if self.gstreamerWorker:
            self.gstreamerWorker.finished = True
        self.__CleanUp()
        
    def _GetFrameRate(self):
        if self.GetProfile().GetVideoNorm() == OutputProfile.PAL:
            framerate = "25/1"
        else:
            framerate = "30000/1001"
        return framerate
