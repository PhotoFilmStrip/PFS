# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2011 Jens Goepfert
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
import subprocess
import sys

from photofilmstrip import Constants
from photofilmstrip.lib.DestructionManager import DestructionManager


if sys.platform == "win32":
    _path = os.getenv("PATH", "").split(";")
    _path.append(os.path.join(Constants.APP_DIR, "lib", "mplayer"))
    os.putenv("PATH", ";".join(_path)) 

    import _subprocess # IGNORE:F0401
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= _subprocess.STARTF_USESHOWWINDOW
    subprocess.STARTUPINFO = lambda: startupinfo


class AppMixin(object):
    
    def __init__(self):
        pass
    
    def InitLogging(self):
        if "-d" in sys.argv:
            lvl = logging.DEBUG
        else:
            lvl = logging.WARNING
        logging.basicConfig(level=lvl,
                            format=self._GetLogFormat(),
                            datefmt='%d.%m.%Y %H:%M:%S')

    def InitI18N(self):
        from photofilmstrip.action.ActionI18N import ActionI18N
        ActionI18N().Execute()
        
    def Start(self):
        self.InitLogging()
        self.InitI18N()
        
        DestructionManager()
        
        from photofilmstrip.lib.jobimpl.JobManager import JobManager
        JobManager().Init(workerCount=2)
        JobManager().Init("render")
        
        try:
            return self._OnStart()
        finally:
            DestructionManager().Destroy()
            
    def _GetLogFormat(self):
        return '%(asctime)s (%(levelname)s) %(name)s: %(message)s'

    def _OnStart(self):
        raise NotImplementedError()
