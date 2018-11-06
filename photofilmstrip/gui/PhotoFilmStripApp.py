# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#

import os
import sys

import wx

from photofilmstrip.gui.ArtProvider  import ArtProvider
from photofilmstrip.gui.FrmMain import FrmMain
from photofilmstrip.gui.DlgBugReport import DlgBugReport


class PhotoFilmStripApp(wx.App):

    def OnInit(self):
#        self.SetAssertMode(wx.PYAPP_ASSERT_SUPPRESS)
#        loc = wx.Locale(wx.LANGUAGE_GERMAN)

        ArtProvider.Init()

        frame = FrmMain()
        frame.Show()
        frame.Maximize()
        self.SetTopWindow(frame)

        DlgBugReport.Initialize(frame)

        if len(sys.argv) > 1:
            for arg in sys.argv[1:]:
                if os.path.isfile(arg):
                    frame.LoadProject(arg)

        return True
