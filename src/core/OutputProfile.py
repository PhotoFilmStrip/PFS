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


class OutputProfile(object):
    
    PAL  = 1
    NTSC = 2
    
    def __init__(self):
        self.PName = ""
        self.PResPal = 0
        self.PResNtsc = 0
        self.PBitrate = 0
        self.__videoNorm = OutputProfile.PAL 
        
    def __Readonly(self, val):
        raise RuntimeError("readonly property")
    
    def __GetResolution(self):
        if self.__videoNorm == OutputProfile.PAL:
            return self.PResPal
        return self.PResNtsc
    PResolution = property(__GetResolution, __Readonly)
    
    def __GetFramerate(self):
        if self.__videoNorm == OutputProfile.PAL:
            return 25.0
        return 30000.0 / 1001.0
    PFramerate = property(__GetFramerate, __Readonly)
        
    
    def SetVideoNorm(self, norm):
        if norm not in [OutputProfile.PAL, OutputProfile.NTSC]:
            raise RuntimeError("videonorm must be one of PAL or NTSC")
        self.__videoNorm = norm
    def GetVideoNorm(self):
        return self.__videoNorm
    PVideoNorm = property(GetVideoNorm, SetVideoNorm)
        


def __CreateDefaultProfiles():
    vcd = OutputProfile()
    vcd.PName = "VCD"
    vcd.PResPal = (352, 288)
    vcd.PResNtsc = (352, 240)
    vcd.PBitrate = 1150
    
    svcd = OutputProfile()
    svcd.PName = "SVCD"
    svcd.PResPal = (480, 576)
    svcd.PResNtsc = (480, 480)
    svcd.PBitrate = 2500

    dvd = OutputProfile()
    dvd.PName = "DVD"
    dvd.PResPal = (720, 576)
    dvd.PResNtsc = (720, 480)
    dvd.PBitrate = 8000
    
    return [vcd, svcd, dvd]

    
def __Create16_9Profiles():
    medium = OutputProfile()
    medium.PName = "Medium 640x360"
    medium.PResPal = (640, 360)
    medium.PResNtsc = (640, 360) 
    medium.PBitrate = 8000

    hd = OutputProfile()
    hd.PName = "HD 1280x720"
    hd.PResPal = (1280, 720)
    hd.PResNtsc = (1280, 720) 
    hd.PBitrate = 10000

    fullhd = OutputProfile()
    fullhd.PName = "FULL-HD 1920x1080"
    fullhd.PResPal = (1920, 1080)
    fullhd.PResNtsc = (1920, 1080) 
    fullhd.PBitrate = 12000
    
    return [medium, hd, fullhd]

def __Create4_3Profiles():
    medium = OutputProfile()
    medium.PName = "Medium 640x480"
    medium.PResPal = (640, 480)
    medium.PResNtsc = (640, 480) 
    medium.PBitrate = 8000

    hd = OutputProfile()
    hd.PName = "HD 960x720"
    hd.PResPal = (960, 720)
    hd.PResNtsc = (960, 720) 
    hd.PBitrate = 10000

    fullhd = OutputProfile()
    fullhd.PName = "FULL-HD 1440x1080"
    fullhd.PResPal = (1440, 1080)
    fullhd.PResNtsc = (1440, 1080) 
    fullhd.PBitrate = 12000
    
    return [medium, hd, fullhd]

def __Create3_2Profiles():
    medium = OutputProfile()
    medium.PName = "Medium 720x480"
    medium.PResPal = (720, 480)
    medium.PResNtsc = (720, 480) 
    medium.PBitrate = 8000

    hd = OutputProfile()
    hd.PName = "HD 1080x720"
    hd.PResPal = (1080, 720)
    hd.PResNtsc = (1080, 720) 
    hd.PBitrate = 10000

    fullhd = OutputProfile()
    fullhd.PName = "FULL-HD 1620x1080"
    fullhd.PResPal = (1620, 1080)
    fullhd.PResNtsc = (1620, 1080) 
    fullhd.PBitrate = 12000
    
    return [medium, hd, fullhd]


def GetOutputProfiles(aspect):
    if "%.3f" % aspect == "%.3f" % (4.0 / 3.0):
        return __CreateDefaultProfiles() + __Create4_3Profiles()
    elif "%.3f" % aspect == "%.3f" % (3.0 / 2.0):
        return __Create3_2Profiles()
    else:
        return __CreateDefaultProfiles() + __Create16_9Profiles()
