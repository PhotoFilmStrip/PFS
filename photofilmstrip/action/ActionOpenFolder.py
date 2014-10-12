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


class ActionOpenFolder(IAction):
    
    def __init__(self, outpath):
        self.outpath = outpath
    
    def GetName(self):
        return _(u'Open folder')
    
    def GetBitmap(self):
        import wx
        ms = wx.ArtProvider.GetSizeHint(wx.ART_MENU)
        return wx.ArtProvider.GetBitmap(wx.ART_FOLDER_OPEN,
                                        wx.ART_TOOLBAR,
                                        ms)

    def Execute(self):
        if not os.path.exists(self.outpath):
            return
        
        if os.name == "nt":
            os.startfile(self.outpath) # IGNORE:E1101
        else:
            subprocess.Popen(["xdg-open", self.outpath])
