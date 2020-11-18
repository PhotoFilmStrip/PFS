# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2011 Jens Goepfert
#

import os
import subprocess

from photofilmstrip.action.IAction import IAction


class ActionOpenFolder(IAction):

    def __init__(self, outFile):
        self.outFile = outFile

    def GetName(self):
        return _("Open folder")

    def Execute(self):
        outDir = os.path.dirname(self.outFile)
        if not os.path.isdir(outDir):
            return

        if os.name == "nt":
            os.startfile(outDir)  # pylint: disable=no-member
        else:
            subprocess.Popen(["xdg-open", outDir])
