#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#

import os
import tempfile
import sys

from photofilmstrip.AppMixin import AppMixin
from photofilmstrip.ux.Ux import UxService, UxPreventStartupSignal
from photofilmstrip import Constants


class GuiApp(AppMixin):

    def _OnStart(self):
        import wx
        assert wx.VERSION[0] == 4

        from photofilmstrip.ux.Ux import UxService
        UxService.GetInstance().Initialize()

        from photofilmstrip.gui.PhotoFilmStripApp import PhotoFilmStripApp
        app = PhotoFilmStripApp(0)
        app.MainLoop()

    def _GetLogFilename(self):
        if getattr(sys, 'frozen', None) == "windows_exe":
            sys.stderr = sys.stdout
            return os.path.join(tempfile.gettempdir(), Constants.APP_NAME + ".log")
        else:
            return None


def main():
    guiApp = GuiApp()
    try:
        UxService.GetInstance().Start()
    except UxPreventStartupSignal:
        return

    guiApp.Start()


if __name__ == "__main__":
    main()
