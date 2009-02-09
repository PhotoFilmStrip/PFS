#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
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

import sys

import wx

from gui.ImageProvider  import ImageProvider
from gui.FrmMain import FrmMain
from gui.DlgBugReport import DlgBugReport


class PhotoFilmStripApp(wx.App):
    
    def OnInit(self):
        wx.InitAllImageHandlers()
#        loc = wx.Locale(wx.LANGUAGE_GERMAN)

        ImageProvider.Init()

        frame = FrmMain()
        frame.Show()
        frame.Maximize()
        self.SetTopWindow(frame)
        
        DlgBugReport.Initialize(frame)
        
        if len(sys.argv) > 1:
            frame.LoadProject(sys.argv[1].decode(sys.getfilesystemencoding()))

        return True


def main():
    app = PhotoFilmStripApp(0)
    app.MainLoop()
