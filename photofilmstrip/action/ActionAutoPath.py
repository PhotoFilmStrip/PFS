# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2011 Jens Goepfert
#

import random

from photofilmstrip.action.IAction import IAction

from photofilmstrip.core.Aspect import Aspect
from photofilmstrip.core import PILBackend


class ActionAutoPath(IAction):

    def __init__(self, picture, aspect):
        self.__picture = picture
        self.__aspect = aspect

    def GetName(self):
        return _(u'Random motion')

    def Execute(self):
        try:
            width, height = PILBackend.GetImageSize(
                self.__picture.GetFilename())
        except:
            return

        if self.__picture.GetWidth() == -1:
            # FIXME: stupid if
            self.__picture.SetWidth(width)
            self.__picture.SetHeight(height)

        ratio = Aspect.ToFloat(self.__aspect)
        if width < height:
            # portrait
            startRect = (0, 0, width, width / ratio)
            targetRect = (0, height - (width / ratio), width, width / ratio)
        else:
            scaledWidth = width * 0.75
            startRect = (0, 0, width, width / ratio)
            d = random.randint(0, 3)
            if d == 0:
                targetRect = (0, 0, scaledWidth, scaledWidth / ratio)
            elif d == 1:
                targetRect = (0, height - (scaledWidth / ratio),
                              scaledWidth, scaledWidth / ratio)
            elif d == 2:
                targetRect = (width - scaledWidth, 0,
                              scaledWidth, scaledWidth / ratio)
            elif d == 3:
                targetRect = (width - scaledWidth,
                              height - (scaledWidth / ratio),
                              scaledWidth, scaledWidth / ratio)

        if random.randint(0, 1):
            targetRect, startRect = startRect, targetRect

        self.__picture.SetStartRect(startRect)
        self.__picture.SetTargetRect(targetRect)
