# encoding: UTF-8
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

import os

from photofilmstrip.core.Aspect import Aspect


class Project(object):
    
    def __init__(self, filename=None):
        self.__pictures = []
        self.__filename = filename
        
        self.__audioFile = None
        self.__aspect = Aspect.ASPECT_16_9
        self.__duration = None
        
    def GetName(self):
        if self.__filename is None:
            return u""
        fname = os.path.splitext(self.__filename)[0]
        return os.path.basename(fname)
    
    def GetFilename(self):
        return self.__filename
    def SetFilename(self, filename):
        self.__filename = filename
    
    def GetPictures(self):
        return self.__pictures
    
    def SetPictures(self, picList):
        self.__pictures = picList
        
    def SetAudioFile(self, audioFile):
        self.__audioFile = audioFile
    def GetAudioFile(self):
        return self.__audioFile
    
    def SetAspect(self, aspect):
        self.__aspect = aspect
    def GetAspect(self):
        return self.__aspect
    
    def SetDuration(self, duration):
        self.__duration = duration
    def GetDuration(self, calc=True):
        if self.__duration is None:
            if not calc:
                return None
            totalTime = 0
            for pic in self.__pictures:
                totalTime += pic.GetDuration() + pic.GetTransitionDuration()
        else:
            totalTime = self.__duration
        return totalTime
