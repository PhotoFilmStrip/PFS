# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2011 Jens Goepfert
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import io
import logging


class MetaBaseRenderer(type):

    def __new__(cls, name, bases, dic):
        newBaseRendererClass = type.__new__(cls, name, bases, dic)
        newBaseRendererClass.PROP_VALUES = {}
        return newBaseRendererClass


class BaseRenderer(metaclass=MetaBaseRenderer):

    def __init__(self):
        self._outputPath = None
        self._profile = None
        self._audioFiles = []
        self._aspect = None

    def Init(self, profile, aspect, outputPath):
        self._outputPath = outputPath
        self._profile = profile
        self._aspect = aspect

    @staticmethod
    def CheckDependencies(msgList):
        pass

    @staticmethod
    def GetName():
        raise NotImplementedError()

    @staticmethod
    def GetProperties():
        return []

    @classmethod
    def SetProperty(cls, prop, value):
        if prop in cls.GetProperties():
            cls.PROP_VALUES[prop] = value  # pylint: disable=no-member
        else:
            logging.getLogger(cls.GetName()).warning(_(u"Unknown property: %s"), prop)

    @classmethod
    def GetProperty(cls, prop):
        return cls.PROP_VALUES.get(prop, cls.GetDefaultProperty(prop))  # pylint: disable=no-member

    @staticmethod
    def GetDefaultProperty(prop):  # pylint: disable=unused-argument
        return _(u"<default>")

    @classmethod
    def Log(cls, level, *args, **kwargs):
        logging.getLogger(cls.__name__).log(level, *args, **kwargs)

    def GetTypedProperty(self, prop, pyType, default=None):
        value = self.__class__.GetProperty(prop)
        warn = True
        if value == self.__class__.GetDefaultProperty(prop):
            if default is not None:
                value = default
            warn = False

        if pyType is bool:
            if value.lower() in ["0", _(u"no"), "false"]:
                value = False
            else:
                value = True
        else:
            try:
                value = pyType(value)
            except:
                if warn:
                    self.__class__.Log(
                           logging.WARN,
                           "{0} must be of type {1}".format(prop, pyType))
                value = None
        return value

    def SetAudioFiles(self, audioFiles):
        self._audioFiles = audioFiles

    def GetAudioFile(self):
        '''
        compatibility
        '''
        if self._audioFiles:
            return self._audioFiles[0]
        else:
            return None

    def GetAudioFiles(self):
        return self._audioFiles

    def GetOutputPath(self):
        return self._outputPath

    def GetProfile(self):
        return self._profile

    def GetFinalizeHandler(self):
        '''
        :rtype: ImageDataFinalizeHandler
        '''
        return ImageDataFinalizeHandler('JPEG', 95)

    def Finalize(self):
        raise NotImplementedError()

    def ToSink(self, data):
        raise NotImplementedError()

    def ProcessAbort(self):
        raise NotImplementedError()


class FinalizeHandler(object):

    def ProcessFinalize(self, pilImg):
        raise NotImplementedError()

    def UseSmartFinalize(self):
        raise NotImplementedError()


class ImageDataFinalizeHandler(FinalizeHandler):

    def __init__(self, formt, quality):
        self._format = formt
        self._quality = quality

    def UseSmartFinalize(self):
        return True

    def ProcessFinalize(self, pilImg):
        res = io.StringIO()
        pilImg.save(res, self._format, quality=self._quality)
        return res.getvalue()
