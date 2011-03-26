# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2010 Jens Goepfert
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

from core.Aspect import Aspect


class OutputProfile(object):
    
    PAL  = 1
    NTSC = 2
    
    def __init__(self, name, bitrate, resPal, resNtsc=None):
        self.__name = name
        self.__resPal = resPal
        if resNtsc is None:
            self.__resNtsc = resPal
        else:
            self.__resNtsc = resNtsc
        self.__bitrate = bitrate
        
        self.__videoNorm = OutputProfile.PAL
        
    def GetName(self, withRes=False):
        if withRes:
            return "%s (%dx%d)" % (self.__name, self.GetResolution()[0], self.GetResolution()[1])
        else:
            return self.__name
        
    def GetBitrate(self):
        return self.__bitrate
    
    def GetResolution(self):
        if self.__videoNorm == OutputProfile.PAL:
            return self.__resPal
        else:
            return self.__resNtsc
    
    def GetFramerate(self):
        if self.__videoNorm == OutputProfile.PAL:
            return 25.0
        else:
            return 30000.0 / 1001.0
        
    
    def SetVideoNorm(self, norm):
        if norm not in [OutputProfile.PAL, OutputProfile.NTSC]:
            raise RuntimeError("videonorm must be one of PAL or NTSC")
        self.__videoNorm = norm
    def GetVideoNorm(self):
        return self.__videoNorm
    
            
        


def __CreateDefaultProfiles():
    vcd  = OutputProfile("VCD",  1150, (352, 288), (352, 240))
    svcd = OutputProfile("SVCD", 2500, (480, 576), (480, 480))
    dvd  = OutputProfile("DVD",  8000, (720, 576), (720, 480))
    
    return [vcd, svcd, dvd]

    
def __Create16_9Profiles():
    medium = OutputProfile("Medium", 8000, (640, 360))
    hd = OutputProfile("HD", 10000, (1280, 720))
    fullhd = OutputProfile("FULL-HD", 12000, (1920, 1080))
    
    return [medium, hd, fullhd]

def __Create4_3Profiles():
    medium = OutputProfile("Medium", 8000, (640, 480))
    hd = OutputProfile("HD", 10000, (960, 720))
    fullhd = OutputProfile("FULL-HD", 12000, (1440, 1080))
    
    return [medium, hd, fullhd]

def __Create3_2Profiles():
    medium = OutputProfile("Medium", 8000, (720, 480))
    hd = OutputProfile("HD", 10000, (1080, 720))
    fullhd = OutputProfile("FULL-HD", 12000, (1620, 1080))
    
    return [medium, hd, fullhd]


def GetOutputProfiles(aspect=Aspect.ASPECT_16_9):
    if aspect == Aspect.ASPECT_4_3:
        return __CreateDefaultProfiles() + __Create4_3Profiles()
    elif aspect == Aspect.ASPECT_3_2:
        return __Create3_2Profiles()
    else:
        return __CreateDefaultProfiles() + __Create16_9Profiles()
