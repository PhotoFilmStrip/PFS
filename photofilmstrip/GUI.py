#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#

import logging
import os
import tempfile
import sys

if __package__ in (None, ""):
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from photofilmstrip.AppMixin import AppMixin
from photofilmstrip.lib.util import StreamToLogger
from photofilmstrip.ux.Ux import UxService, UxPreventStartupSignal
from photofilmstrip import Constants


class GuiApp(AppMixin):

    def _OnStart(self):
        import wx
        assert wx.VERSION[0] == 4

        UxService.GetInstance().Initialize()

        from photofilmstrip.gui.PhotoFilmStripApp import PhotoFilmStripApp
        app = PhotoFilmStripApp(0)
        app.MainLoop()

    def _GetLogFilename(self):
        if getattr(sys, 'frozen', None):
            stdOutLogger = StreamToLogger("OUT", logging.INFO)
            stdErrLogger = StreamToLogger("ERR", logging.ERROR)
            sys.stdout = stdOutLogger
            sys.stderr = stdErrLogger

            return os.path.join(tempfile.gettempdir(), Constants.APP_NAME + ".log")
        else:
            return None


def _InstallUserIcons():
    # when running from source neither the hicolor theme icons nor the
    # desktop entry are installed; link/copy them into the user's dirs so the
    # window manager resolves app-id "photofilmstrip" -> photofilmstrip.desktop
    # -> photofilmstrip icon (instead of the generic interpreter icon)
    try:
        import shutil
        import subprocess
        from photofilmstrip.lib.util import GetDataDir
        dataDir = GetDataDir("")
        if not dataDir:
            return
        home = os.path.expanduser("~")

        srcDir = os.path.join(dataDir, "icons")
        dstBase = os.path.join(home, ".local", "share", "icons", "hicolor")
        for entry in os.listdir(srcDir):
            src = os.path.join(srcDir, entry, "apps")
            if not os.path.isdir(src):
                continue
            for fname in os.listdir(src):
                if not fname.startswith("photofilmstrip."):
                    continue
                dst = os.path.join(dstBase, entry, "apps")
                dstFile = os.path.join(dst, fname)
                if not os.path.exists(dstFile):
                    os.makedirs(dst, exist_ok=True)
                    try:
                        os.link(os.path.join(src, fname), dstFile)
                    except OSError:
                        shutil.copy2(os.path.join(src, fname), dstFile)

        deskSrc = os.path.join(dataDir, "photofilmstrip.desktop")
        deskDstDir = os.path.join(home, ".local", "share", "applications")
        if os.path.isfile(deskSrc):
            os.makedirs(deskDstDir, exist_ok=True)
            # point Exec at the source launcher so the entry actually works
            with open(deskSrc, "r", encoding="utf-8") as fd:
                content = fd.read()
            launcher = os.path.join(os.path.dirname(dataDir), "pfs")
            content = content.replace("Exec=photofilmstrip",
                                      "Exec=%s %%F" % launcher)
            with open(os.path.join(deskDstDir, "photofilmstrip.desktop"),
                      "w", encoding="utf-8") as fd:
                fd.write(content)

        try:
            subprocess.Popen(["gtk-update-icon-cache", dstBase],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            pass
    except Exception:
        pass


def main():
    if os.name == "nt" and not getattr(sys, 'frozen', None):
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    else:
        # set the program name before GTK initializes, so the window manager
        # matches the installed photofilmstrip.desktop entry and shows the
        # PhotoFilmStrip icon (alt-tab, taskbar, dock) instead of python's
        try:
            from gi.repository import GLib
            GLib.set_prgname("photofilmstrip")
            GLib.set_application_name(Constants.APP_NAME)
        except Exception:
            pass
        if not getattr(sys, 'frozen', None):
            _InstallUserIcons()

    guiApp = GuiApp()
    try:
        UxService.GetInstance().Start()
    except UxPreventStartupSignal:
        return

    guiApp.Start()


if __name__ == "__main__":
    main()
