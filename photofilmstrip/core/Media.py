# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#

import enum
import os

from photofilmstrip.lib.common.ObserverPattern import Observable
from photofilmstrip.lib.util import CheckFile, FILE_EXTENSIONS_AUDIO, \
    FILE_EXTENSIONS_VIDEO


class Media(Observable):

    def __init__(self, filename):
        Observable.__init__(self)
        self._filename = filename
        self._parent = None
        self._type = self._DetectType()
        self._children = []
        self._properties = {}

    def _DetectType(self):
        # TODO: maybe we let gstreamer detect this later
        fileExt = os.path.splitext(self._filename)[1].lower()
        if fileExt in FILE_EXTENSIONS_AUDIO:
            return MediaType.AUDIO
        elif fileExt in FILE_EXTENSIONS_VIDEO:
            return MediaType.VIDEO
        else:
            return None

    def GetFilename(self):
        return self._filename

    def GetParent(self):
        return self._parent

    def SetProperty(self, name, value):
        assert isinstance(value, str)
        self._properties[name] = value
        self.Notify("property_{}".format(name))

    def GetProperty(self, name):
        value = self._properties.get(name)
        if name == "orientation":
            value = MediaOrientation.Create(value)
            if value is None:
                value = MediaOrientation.AS_IS
        return value

    def GetProperties(self):
        return self._properties

    def GetChildren(self):
        return self._children

    def GetChild(self, idx):
        return self._children[idx]

    def GetIndex(self):
        if self._parent:
            try:
                return self._parent.GetChildren().index(self)
            except ValueError:
                pass
        return None

    def AddChild(self, child, idx=None):
        child._parent = self  # pylint: disable=protected-access
        if idx is None:
            self._children.append(child)
        else:
            self._children.insert(idx, child)
        self.Notify("children")

    def RemoveChild(self, child):
        self._children.remove(child)
        self.Notify("children")

    def IsAudio(self):
        return self._type == MediaType.AUDIO

    def IsVideo(self):
        return self._type == MediaType.VIDEO

    def IsOk(self):
        return CheckFile(self._filename) and self._type is not None


class MediaType(enum.Enum):

    VIDEO = 1
    AUDIO = 2


class MediaOrientation(enum.Enum):

    AS_IS = "as-is"
    AUTO_DETECT = "auto-detect"
    ROTATE_LEFT = "rotate-left"
    ROTATE_RIGHT = "rotate-right"
    UPSIDE_DOWN = "upside-down"

    def GetLabel(self):
        i18nDict = {
            MediaOrientation.AS_IS: _("As is"),
            MediaOrientation.AUTO_DETECT: _("Auto detect"),
            MediaOrientation.ROTATE_LEFT: _("Rotate left"),
            MediaOrientation.ROTATE_RIGHT: _("Rotate right"),
            MediaOrientation.UPSIDE_DOWN: _("Upside down")
        }
        return i18nDict[self]

    @classmethod
    def Create(cls, value):
        for item in cls:
            if item.value == value:
                return item
