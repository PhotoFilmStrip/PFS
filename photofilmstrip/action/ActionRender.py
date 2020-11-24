# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2011 Jens Goepfert
#

import logging
import os

from photofilmstrip.action.IAction import IAction

from photofilmstrip.lib.Settings import Settings
from photofilmstrip.lib.util import CheckFile
from photofilmstrip.core.Renderers import RENDERERS
from photofilmstrip.core.RenderEngine import RenderEngineSlideshow, \
    RenderEngineTimelapse
from photofilmstrip.core.RenderJob import RenderJob
from photofilmstrip.core.GPlayer import GPlayer
from photofilmstrip.core.exceptions import RenderException


class ActionRender(IAction):

    def __init__(self, photoFilmStrip,
                 profile,
                 rendererClass, draftMode,
                 outpath=None):
        self.__photoFilmStrip = photoFilmStrip
        self.__profile = profile
        self.__rendererClass = rendererClass
        self.__draftMode = draftMode
        self.__outpath = outpath

        self.__renderJob = None

    def GetName(self):
        return _("Start")

    def _CheckAndGetOutFile(self):
        if self.__outpath == "-":
            return

        projFile = self.__photoFilmStrip.GetFilename()
        baseDir = os.path.dirname(projFile)
        baseDir = os.path.join(baseDir, self.__profile.GetName())
        if not os.path.isdir(baseDir):
            os.makedirs(baseDir)

        outFile = os.path.join(baseDir,
                               os.path.basename(os.path.splitext(projFile)[0]))
        return outFile

    def _SaveSettings(self):
        settings = Settings()
        settings.SetLastProfile(self.__profile.GetName())

        try:
            idxRenderer = RENDERERS.index(self.__rendererClass)
        except ValueError:
            return

        settings.SetUsedRenderer(idxRenderer)

    def Execute(self):
        audioFiles = []
        invalidAudioFiles = []
        audioLength = 0
        for audioFile in self.__photoFilmStrip.GetAudioFiles():
            if CheckFile(audioFile):
                length = GPlayer(audioFile).GetLength()
                if length is None:
                    logging.warning("Invalid audiofile '%s'", audioFile)
                    invalidAudioFiles.append(audioFile)
                else:
                    audioFiles.append(audioFile)
                    logging.debug("Using audiofile '%s' with length: %s", audioFile, length)
                    audioLength += length
            else:
                logging.warning("Missing audiofile '%s'!", audioFile)

        if len(audioFiles) != len(self.__photoFilmStrip.GetAudioFiles()):
            raise RenderException(
                _("The following audio files are invalid or missing:") + "\n\n" + "\n".join(
                    invalidAudioFiles))

        outFile = self._CheckAndGetOutFile()

        self._SaveSettings()

        savedProps = Settings().GetRenderProperties(self.__rendererClass.__name__)
        for prop in self.__rendererClass.GetProperties():
            value = savedProps.get(prop.lower(), self.__rendererClass.GetProperty(prop))
            self.__rendererClass.SetProperty(prop, value)

        totalLength = self.__photoFilmStrip.GetDuration(False)
        if totalLength == -1:
            totalLength = int(round((audioLength + 500) / 1000.0))

        renderer = self.__rendererClass()
        renderer.Init(self.__profile,
                      self.__photoFilmStrip.GetAspect(),
                      outFile)

        renderer.SetAudioFiles(audioFiles)

        if self.__photoFilmStrip.GetTimelapse():
            uxEvent = "RenderTimeLapse"
            renderEngine = RenderEngineTimelapse(self.__profile,
                                                 self.__photoFilmStrip.GetPictures(),
                                                 self.__draftMode)
        else:
            uxEvent = "RenderSlideshow"
            renderEngine = RenderEngineSlideshow(self.__profile,
                                                 self.__photoFilmStrip.GetPictures(),
                                                 self.__draftMode,
                                                 totalLength)

        name = "%s (%s)" % (self.__photoFilmStrip.GetName(),
                            self.__profile.GetName())

        self.__renderJob = RenderJob(name, renderer,
                                     renderEngine.GetTasks())
        self.__renderJob.AddUxEvent(uxEvent)
        self.__renderJob.AddUxEvent(self.__profile.GetName())

    def GetRenderJob(self):
        return self.__renderJob
