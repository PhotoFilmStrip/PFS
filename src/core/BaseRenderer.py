#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
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

import logging


class MetaBaseRenderer(type):
    def __new__(cls, name, bases, dic):
        newBaseRendererClass = type.__new__(cls, name, bases, dic)
        newBaseRendererClass.PROP_VALUES = {}
        return newBaseRendererClass


class BaseRenderer(object):
    
    __metaclass__  = MetaBaseRenderer
    
    def __init__(self):
        self._outputPath = None
        self._profile = None
        self._audioFile = None

    def Init(self, profile, outputPath):
        self._outputPath = outputPath
        self._profile = profile
        
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
            cls.PROP_VALUES[prop] = value
        else:
            logging.getLogger(cls.GetName()).warning(_(u"Unknown property: %s"), prop)
            
    @classmethod
    def GetProperty(cls, prop):
        return cls.PROP_VALUES.get(prop, cls.GetDefaultProperty(prop))

    @staticmethod
    def GetDefaultProperty(prop):
        return _(u"<default>")
    
    def SetAudioFile(self, audioFile):
        self._audioFile = audioFile
    def GetAudioFile(self):
        return self._audioFile
    PAudioFile = property(GetAudioFile, SetAudioFile)
        
    def GetOutputPath(self):
        return self._outputPath
    POutputPath = property(GetOutputPath)
        
    def GetProfile(self):
        return self._profile
    PProfile = property(GetProfile)

    def Prepare(self):
        raise NotImplementedError()        
    
    def ProcessPrepare(self, filename, rotation, effect):
        raise NotImplementedError()
    
    def ProcessCropAndResize(self, preparedResult, cropRect, size):
        raise NotImplementedError()
        
    def ProcessTransition(self, fileListFrom, fileListTo):
        raise NotImplementedError()
    
    def ProcessFinalize(self, filename):
        raise NotImplementedError()
    
    def Finalize(self):
        raise NotImplementedError()
    
    def ProcessAbort(self):
        raise NotImplementedError()
