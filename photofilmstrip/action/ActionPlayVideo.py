# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2011 Jens Goepfert
#

import os

from photofilmstrip.action.IAction import IAction
from photofilmstrip.lib.util import StartFile


class ActionPlayVideo(IAction):

    def __init__(self, outFile):
        self.outFile = outFile

    def GetName(self):
        return _(u'Play video')

    def Execute(self):
        if os.path.isfile(self.outFile):
            StartFile(self.outFile)
