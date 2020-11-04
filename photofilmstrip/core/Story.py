# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2019 Jens Goepfert
#

import os

from photofilmstrip.lib.common.ObserverPattern import Observable
from photofilmstrip.core.Aspect import Aspect


class Story(Observable):

    def __init__(self, filename=None):
        Observable.__init__(self)
        self.__medias = []
        self.__filename = filename

    def GetName(self):
        if self.__filename is None:
            return ""
        fname = os.path.splitext(self.__filename)[0]
        return os.path.basename(fname)

    def GetFilename(self):
        return self.__filename

    def SetFilename(self, filename):
        self.__filename = filename

    def GetAspect(self):
        return Aspect.ASPECT_16_9

    def GetMedias(self):
        return self.__medias

    def SetMedias(self, medias):
        self.__medias = medias
        self.Notify("medias")
