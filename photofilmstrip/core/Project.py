# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#

import os

from photofilmstrip.lib.common.ObserverPattern import Observable
from photofilmstrip.core.Aspect import Aspect


class Project(Observable):

    def __init__(self, filename=None):
        Observable.__init__(self)
        self.__pictures = []
        self.__filename = filename

        self.__audioFiles = []
        self.__aspect = Aspect.ASPECT_16_9
        self.__duration = None
        self.__timelapse = False

    def GetName(self):
        if self.__filename is None:
            return ""
        fname = os.path.splitext(self.__filename)[0]
        return os.path.basename(fname)

    def GetFilename(self):
        return self.__filename

    def SetFilename(self, filename):
        self.__filename = filename

    def GetPictures(self):
        return self.__pictures

    def SetPictures(self, picList):
        oldDuration = self.GetDuration()
        self.__pictures = picList
        self.Notify("pictures")
        if self.GetDuration() != oldDuration:
            self.Notify("duration")

    def SetAudioFiles(self, audioFiles):
        self.__audioFiles = audioFiles
        self.Notify("audiofile")

    def GetAudioFile(self):
        '''
        compatibility
        '''
        if self.__audioFiles:
            return self.__audioFiles[0]
        else:
            return None

    def GetAudioFiles(self):
        return self.__audioFiles

    def SetAspect(self, aspect):
        if aspect == self.__aspect:
            return
        self.__aspect = aspect
        self.Notify("aspect")

    def GetAspect(self):
        return self.__aspect

    def SetDuration(self, duration):
        if duration == self.__duration:
            return
        self.__duration = duration
        self.Notify("duration")

    def GetDuration(self, calc=True):
        if calc:
            totalTime = 0
            for pic in self.__pictures:
                totalTime += pic.GetDuration() + pic.GetTransitionDuration()
        else:
            totalTime = self.__duration
        return totalTime

    def SetTimelapse(self, value):
        if value == self.__timelapse:
            return
        self.__timelapse = value
        self.Notify("timelapse")

    def GetTimelapse(self):
        return self.__timelapse
