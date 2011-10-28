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

import os
import subprocess

from photofilmstrip.action.IAction import IAction
#from photofilmstrip.core.MPlayer import MPlayer


class ActionPlayVideo(IAction):
    
    def __init__(self, outpath):
        self.outpath = outpath
    
    def GetName(self):
        return _(u'Play video')
    
    def Execute(self):
        videoFile = os.path.join(self.outpath, "output.avi")
        if not os.path.exists(videoFile):
            videoFile = os.path.join(self.outpath, "output.flv")
            if not os.path.exists(videoFile):
                return

        if os.name == "nt":
            try:
                os.startfile(videoFile)
            except:
                pass
        else:
            subprocess.Popen(["xdg-open", videoFile])
#                mplayer = MPlayer(videoFile)
#                mplayer.Play()
    