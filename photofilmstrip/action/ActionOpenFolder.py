# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2011 Jens Goepfert
#

import os

from photofilmstrip.action.IAction import IAction
from photofilmstrip.lib.util import StartFile


class ActionOpenFolder(IAction):

    def __init__(self, outFile):
        self.outFile = outFile

    def GetName(self):
        return _("Open folder")

    def Execute(self):
        outDir = os.path.dirname(self.outFile)
        if not os.path.isdir(outDir):
            return

        StartFile(outDir)
