#!/usr/bin/python
# encoding: UTF-8
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

import os
import tempfile
import sys

from photofilmstrip.AppMixin import AppMixin
from photofilmstrip import Constants


class GuiApp(AppMixin):

    def _OnStart(self):
        if not getattr(sys, 'frozen', False):
            import wxversion
            wxversion.select("3.0")

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
    guiApp.Start()


if __name__ == "__main__":
    main()
