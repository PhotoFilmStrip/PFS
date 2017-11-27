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

from photofilmstrip.core.Aspect import Aspect


class FrameRate(object):

    def __init__(self, numValue, strValue):
        self.num = numValue
        self.str = strValue

    def __str__(self, *args, **kwargs):
        return u"%.2f fps" % self.num

    def AsFloat(self):
        return self.num

    def AsStr(self):
        return self.str


class OutputProfile(object):

    PAL = 1
    NTSC = 2

    def __init__(self, name, resolution, frameRate, bitrate, videoNorm=None):
        self.__name = name
        self.__resolution = resolution
        self.__frameRate = frameRate
        self.__bitrate = bitrate
        self.__videoNorm = videoNorm
        self.__friendlyName = None

    def GetName(self, withRes=False):
        if self.__videoNorm:
            simple = self.__name
        else:
            simple = "{0}@{1}".format(self.__name, self.__frameRate)
        if withRes:
            return "%s (%dx%d)" % (simple, self.GetResolution()[0], self.GetResolution()[1])
        else:
            return simple

    def GetBitrate(self):
        return self.__bitrate

    def GetResolution(self):
        return self.__resolution

    def GetFrameRate(self):
        return self.__frameRate

    def GetVideoNorm(self):
        return self.__videoNorm

    def IsMPEGProfile(self):
        for mpegProf in ("VCD", "SVCD", "DVD"):
            if self.__name.startswith(mpegProf):
                return True
        return False

    def SetFriendlyName(self, value):
        self.__friendlyName = value

    def GetFriendlyName(self):
        return self.__friendlyName


FPS15 = FrameRate(15.0, "15/1")
FPS23996 = FrameRate(24000.0 / 1001.0, "24000/1001")
FPS24 = FrameRate(24.0, "24/1")
FPS25 = FrameRate(25.0, "25/1")
FPS29997 = FrameRate(30000.0 / 1001.0, "30000/1001")
FPS30 = FrameRate(30.0, "30/1")
FPS50 = FrameRate(50.0, "50/1")
FPS59994 = FrameRate(60000.0 / 1001.0, "60000/1001")
FPS60 = FrameRate(60.0, "60/1")


def __CreateMPEGProfiles():
    vcd_pal = OutputProfile("VCD-PAL", (352, 288), FPS25, 1150,
                            OutputProfile.PAL)
    vcd_ntsc = OutputProfile("VCD-NTSC", (352, 240), FPS29997, 1150,
                             OutputProfile.NTSC)

    svcd_pal = OutputProfile("SVCD-PAL", (480, 576), FPS25, 2500,
                             OutputProfile.PAL)
    svcd_ntsc = OutputProfile("SVCD-NTSC", (480, 576), FPS29997, 2500,
                              OutputProfile.NTSC)

    dvd_pal = OutputProfile("DVD-PAL", (720, 576), FPS25, 8000,
                            OutputProfile.PAL)
    dvd_ntsc = OutputProfile("DVD-NTSC", (720, 480), FPS29997, 8000,
                             OutputProfile.NTSC)
    result = [vcd_pal, vcd_ntsc, svcd_pal, svcd_ntsc, dvd_pal, dvd_ntsc]
    for prof in result:
        prof.SetFriendlyName(prof.GetName())
    return result


def __Create16_9Profiles():
    profs = []

    # 360p
    for fps in [FPS23996, FPS25]:
        prof = OutputProfile("360p", (640, 360), fps, 1000)
        if fps is FPS25:
            prof.SetFriendlyName("Medium")
        profs.append(prof)
    for fps in [FPS29997, FPS30, FPS50, FPS59994, FPS60]:
        prof = OutputProfile("360p", (640, 360), fps, 1500)
        profs.append(prof)

    # 480p
    for fps in [FPS24, FPS30]:
        prof = OutputProfile("480p", (854, 480), fps, 2500)
        profs.append(prof)
    for fps in [FPS50, FPS60]:
        prof = OutputProfile("480p", (854, 480), fps, 4000)
        profs.append(prof)

    # 720p
    for fps in [FPS23996, FPS24, FPS25]:
        prof = OutputProfile("HD 720p", (1280, 720), fps, 5000)
        if fps is FPS25:
            prof.SetFriendlyName("HD")
        profs.append(prof)
    for fps in [FPS29997, FPS30, FPS50, FPS59994, FPS60]:
        prof = OutputProfile("HD 720p", (1280, 720), fps, 7500)
        profs.append(prof)

    # 1080p
    for fps in [FPS23996, FPS24, FPS25]:
        prof = OutputProfile("HD 1080p", (1920, 1080), fps, 8000)
        if fps is FPS25:
            prof.SetFriendlyName("FULL-HD")
        profs.append(prof)
    for fps in [FPS29997, FPS30, FPS50, FPS60]:
        prof = OutputProfile("HD 1080p", (1920, 1080), fps, 12000)
        profs.append(prof)

    # 2160p
    for fps in [FPS23996, FPS24, FPS25]:
        prof = OutputProfile("UHD-1 2160p", (3840, 2160), fps, 25000)
        if fps is FPS25:
            prof.SetFriendlyName("UHD")
        profs.append(prof)
    for fps in [FPS29997, FPS30, FPS50, FPS60]:
        prof = OutputProfile("UHD-1 2160p", (3840, 2160), fps, 50000)
        profs.append(prof)

    # 4320p
    for fps in [FPS25, FPS30, FPS50, FPS60]:
        prof = OutputProfile("UHD-2 4320p", (7680, 4320), fps, 60000)
        profs.append(prof)

    return profs


def __Create4_3Profiles():
    profs = []

    # 360p
    for fps in [FPS23996, FPS25]:
        prof = OutputProfile("360p", (480, 360), fps, 1000)
        if fps is FPS25:
            prof.SetFriendlyName("Medium")
        profs.append(prof)
    for fps in [FPS29997, FPS30, FPS50, FPS59994, FPS60]:
        prof = OutputProfile("360p", (480, 360), fps, 1500)
        profs.append(prof)

    # 480p
    for fps in [FPS24, FPS30]:
        prof = OutputProfile("480p", (640, 480), fps, 2500)
        profs.append(prof)
    for fps in [FPS50, FPS60]:
        prof = OutputProfile("480p", (640, 480), fps, 4000)
        profs.append(prof)

    # 720p
    for fps in [FPS23996, FPS24, FPS25]:
        prof = OutputProfile("HD 720p", (960, 720), fps, 5000)
        if fps is FPS25:
            prof.SetFriendlyName("HD")
        profs.append(prof)
    for fps in [FPS29997, FPS30, FPS50, FPS59994, FPS60]:
        prof = OutputProfile("HD 720p", (960, 720), fps, 7500)
        profs.append(prof)

    # 1080p
    for fps in [FPS23996, FPS24, FPS25]:
        prof = OutputProfile("HD 1080p", (1440, 1080), fps, 8000)
        if fps is FPS25:
            prof.SetFriendlyName("FULL-HD")
        profs.append(prof)
    for fps in [FPS29997, FPS30, FPS50, FPS60]:
        prof = OutputProfile("HD 1080p", (1440, 1080), fps, 12000)
        profs.append(prof)

    # 2160p
    for fps in [FPS23996, FPS24, FPS25]:
        prof = OutputProfile("UHD-1 2160p", (2880, 2160), fps, 25000)
        if fps is FPS25:
            prof.SetFriendlyName("UHD")
        profs.append(prof)
    for fps in [FPS29997, FPS30, FPS50, FPS60]:
        prof = OutputProfile("UHD-1 2160p", (2880, 2160), fps, 50000)
        profs.append(prof)

    # 4320p
    for fps in [FPS25, FPS30, FPS50, FPS60]:
        prof = OutputProfile("UHD-2 4320p", (5760, 4320), fps, 60000)
        profs.append(prof)
    return profs


def __Create3_2Profiles():
    profs = []

    # 360p
    for fps in [FPS23996, FPS25]:
        prof = OutputProfile("360p", (540, 360), fps, 1000)
        if fps is FPS25:
            prof.SetFriendlyName("Medium")
        profs.append(prof)
    for fps in [FPS29997, FPS30, FPS50, FPS59994, FPS60]:
        prof = OutputProfile("360p", (540, 360), fps, 1500)
        profs.append(prof)

    # 480p
    for fps in [FPS24, FPS30]:
        prof = OutputProfile("480p", (720, 480), fps, 2500)
        profs.append(prof)
    for fps in [FPS50, FPS60]:
        prof = OutputProfile("480p", (720, 480), fps, 4000)
        profs.append(prof)

    # 720p
    for fps in [FPS23996, FPS24, FPS25]:
        prof = OutputProfile("HD 720p", (1080, 720), fps, 5000)
        if fps is FPS25:
            prof.SetFriendlyName("HD")
        profs.append(prof)
    for fps in [FPS29997, FPS30, FPS50, FPS59994, FPS60]:
        prof = OutputProfile("HD 720p", (1080, 720), fps, 7500)
        profs.append(prof)

    # 1080p
    for fps in [FPS23996, FPS24, FPS25]:
        prof = OutputProfile("HD 1080p", (1620, 1080), fps, 8000)
        if fps is FPS25:
            prof.SetFriendlyName("FULL-HD")
        profs.append(prof)
    for fps in [FPS29997, FPS30, FPS50, FPS60]:
        prof = OutputProfile("HD 1080p", (1620, 1080), fps, 12000)
        profs.append(prof)

    # 2160p
    for fps in [FPS23996, FPS24, FPS25]:
        prof = OutputProfile("UHD-1 2160p", (3240, 2160), fps, 25000)
        if fps is FPS25:
            prof.SetFriendlyName("UHD")
        profs.append(prof)
    for fps in [FPS29997, FPS30, FPS50, FPS60]:
        prof = OutputProfile("UHD-1 2160p", (3240, 2160), fps, 50000)
        profs.append(prof)

    # 4320p
    for fps in [FPS25, FPS30, FPS50, FPS60]:
        prof = OutputProfile("UHD-2 4320p", (6480, 4320), fps, 60000)
        profs.append(prof)

    return profs


def GetOutputProfiles(aspect=Aspect.ASPECT_16_9):
    if aspect == Aspect.ASPECT_4_3:
        return __Create4_3Profiles()
    elif aspect == Aspect.ASPECT_3_2:
        return __Create3_2Profiles()
    else:
        return __Create16_9Profiles()


def GetMPEGProfiles():
    return __CreateMPEGProfiles()
