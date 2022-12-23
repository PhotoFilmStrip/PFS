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
        if name == MediaOrientation.KEY():
            value = MediaOrientation.Create(value)
            if value is None:
                value = MediaOrientation.AUTO_DETECT
        elif name == MediaAudioLevel.KEY():
            value = MediaAudioLevel.Create(value)
            if value is None:
                value = MediaAudioLevel.PERCENT_50
        return value

    def GetAllProperties(self):
        return {
            MediaOrientation.KEY(): self.GetProperty(MediaOrientation.KEY()),
            MediaAudioLevel.KEY(): self.GetProperty(MediaAudioLevel.KEY())
        }

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

    AUTO_DETECT = "auto-detect"
    ROTATE_LEFT = "rotate-left"
    ROTATE_RIGHT = "rotate-right"
    UPSIDE_DOWN = "upside-down"

    def GetLabel(self):
        i18nDict = {
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

    @classmethod
    def KEY(cls):
        return "orientation"


class MediaAudioLevel(enum.Enum):

    PERCENT_00 = "mute"
    PERCENT_25 = "25"
    PERCENT_50 = "50"
    PERCENT_75 = "75"
    PERCENT_100 = "100"

    def GetLabel(self):
        i18nDict = {
            MediaAudioLevel.PERCENT_00: _("Muted"),
            MediaAudioLevel.PERCENT_25: _("Silent"),
            MediaAudioLevel.PERCENT_50: _("Medium"),
            MediaAudioLevel.PERCENT_75: _("Loud"),
            MediaAudioLevel.PERCENT_100: _("Full")
        }
        return i18nDict[self]

    def GetValue(self):
        valueDict = {
            MediaAudioLevel.PERCENT_00: 0.0,
            MediaAudioLevel.PERCENT_25: 0.25,
            MediaAudioLevel.PERCENT_50: 0.5,
            MediaAudioLevel.PERCENT_75: 0.75,
            MediaAudioLevel.PERCENT_100: 1.0
        }
        return valueDict[self]

    @classmethod
    def Create(cls, value):
        for item in cls:
            if item.value == value:
                return item

    @classmethod
    def KEY(cls):
        return "audio-level"
