# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#

import os
import sys

import wx

from photofilmstrip.lib.Settings import Settings

from photofilmstrip.gui.Art import Art
from photofilmstrip.gui.FrmMain import FrmMain
from photofilmstrip.gui.DlgBugReport import DlgBugReport


class PhotoFilmStripApp(wx.App):

    def OnInit(self):
        lang = Settings().GetLanguage()
        wxLangInfo = wx.Locale.FindLanguageInfo(lang)
        if wxLangInfo is None:
            wxLang = wx.Locale.GetSystemLanguage()
        else:
            wxLang = wxLangInfo.Language
            if not wx.Locale.IsAvailable(wxLang):
                wxLang = wx.Locale.GetSystemLanguage()
        self.locale = wx.Locale(wxLang)  # pylint: disable=attribute-defined-outside-init

        Art.Init()

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
