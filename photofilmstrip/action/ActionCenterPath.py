# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2013 Jens Goepfert
#

from photofilmstrip.action.IAction import IAction

from photofilmstrip.core.Aspect import Aspect
from photofilmstrip.core import PILBackend


class ActionCenterPath(IAction):

    def __init__(self, picture, aspect):
        self.__picture = picture
        self.__aspect = aspect

    def GetName(self):
        return _(u'Centralize motion')

    def Execute(self):
        try:
            width, height = PILBackend.GetImageSize(
                self.__picture.GetFilename())
        except:
            return

        ratio = Aspect.ToFloat(self.__aspect)
        picRatio = width / height
        if picRatio > ratio:
            scaledWidth = height * ratio
            scaledHeight = height
        else:
            scaledWidth = width
            scaledHeight = width / ratio

        centerRect = (int(round((width - scaledWidth) / 2.0)),
                      int(round((height - scaledHeight) / 2.0)),
                      int(round(scaledWidth)), int(round(scaledHeight)))
        self.__picture.SetStartRect(centerRect)
        self.__picture.SetTargetRect(centerRect)
