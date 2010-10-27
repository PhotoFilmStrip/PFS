# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2010 Jens Goepfert
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

import re
import sys

from subprocess import Popen, PIPE, STDOUT

from lib.util import Encode


class MPlayer(object):
    
    def __init__(self, filename):
        self.filename = Encode(filename, sys.getfilesystemencoding())
        self.__proc = None
        self.__length = None
        
        self.__Identify()

    def __Identify(self):
        cmd = ["mplayer", "-identify", "-frames", "0", "-ao", "null", "-vo", "null", self.filename]
        proc = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=False)
        proc.wait()
        output = proc.stdout.read()
        
        reo = re.compile(".*ID_LENGTH=(\d+)[.](\d+)*", re.DOTALL | re.MULTILINE)
        match = reo.match(output)
            
        try:
            if match is not None:
                self.__length = float(match.group(1))
        except:
            import traceback
            traceback.print_exc()
        
    def __Call(self):
        if self.__proc is None:
            cmd = ["mplayer", self.filename]
            self.__proc = Popen(cmd, stdin=PIPE, stderr=STDOUT, shell=False)
        
    def IsOk(self):
        return self.__length is not None
    
    def IsPlaying(self):
        return self.__proc is not None
    
    def Play(self):
        self.__Call()
    
    def Stop(self):
        self.Close()
    
    def Close(self):
        if self.__proc is not None:
            if sys.platform == "win32":
                cmd = ["taskkill", "/PID", str(self.__proc.pid), "/F"]
                kp = Popen(cmd, shell=False)
                kp.wait()
            else:
                self.__proc.communicate("q")
            self.__proc = None
    
    def GetLength(self):
        return self.__length
