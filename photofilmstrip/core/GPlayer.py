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

import datetime
import logging
import re
import sys

try:
    import pygst
    pygst.require("0.10")
    import gst
except ImportError:
    pass

from photofilmstrip.lib.util import Encode


class GPlayer(object):
    
    def __init__(self, filename):
        self.filename = Encode(filename, sys.getfilesystemencoding())
        self.__proc = None
        self.__length = None
        
        self.__Identify()

    def __Identify(self):
        d = gst.parse_launch("filesrc name=source ! decodebin2 ! fakesink")
        source = d.get_by_name("source")
        source.set_property("location", self.filename)
        d.set_state(gst.STATE_PLAYING)
        d.get_state()
        gstFormat = gst.Format(gst.FORMAT_TIME)
        duration = d.query_duration(gstFormat)[0]
        d.set_state(gst.STATE_NULL)
        
        delta = datetime.timedelta(seconds=(duration / gst.SECOND))
        logging.debug("identify audio with gplayer: Duration: %s", delta)
        
        self.__length = duration / gst.SECOND
        
    def IsOk(self):
        return self.__length is not None
    
    def IsPlaying(self):
        return self.__proc is not None
    
    def Play(self):
        if self.__proc is None:
            self.__proc = gst.parse_launch("filesrc name=source ! decodebin2 ! autoaudiosink")
            source = self.__proc.get_by_name("source")
            source.set_property("location", self.filename)
            self.__proc.set_state(gst.STATE_PLAYING)
    
    def Stop(self):
        self.Close()
    
    def Close(self):
        self.__proc.set_state(gst.STATE_NULL)
        self.__proc = None
    
    def GetLength(self):
        return self.__length
