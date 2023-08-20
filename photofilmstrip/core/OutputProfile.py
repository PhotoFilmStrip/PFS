# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2010 Jens Goepfert
#

from photofilmstrip.core.Aspect import Aspect


class FrameRate:

    def __init__(self, numValue, strValue):
        self.num = numValue
        self.str = strValue

    def __str__(self, *args, **kwargs):
        return "%.2f fps" % self.num

    def AsFloat(self):
        return self.num

    def AsStr(self):
        return self.str


class OutputProfile:

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

    def ToPortraitMode(self):
        portraitProf = OutputProfile("Portrait {}".format(self.__name),
                                     (self.__resolution[1], self.__resolution[0]),
                                     self.__frameRate,
                                     self.__bitrate)
        return portraitProf


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
    svcd_ntsc = OutputProfile("SVCD-NTSC", (480, 480), FPS29997, 2500,
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


def __Create16_10Profiles():
    profs = []

    for fps in [FPS23996, FPS25]:
        prof = OutputProfile("640x400", (640, 400), fps, 1000)
        if fps is FPS25:
            prof.SetFriendlyName("Medium")
        profs.append(prof)
    for fps in [FPS29997, FPS30, FPS50, FPS59994, FPS60]:
        prof = OutputProfile("640x400", (640, 400), fps, 1500)
        profs.append(prof)

    for fps in [FPS24, FPS30]:
        prof = OutputProfile("768x480", (768, 480), fps, 2500)
        profs.append(prof)
    for fps in [FPS50, FPS60]:
        prof = OutputProfile("768x480", (768, 480), fps, 4000)
        profs.append(prof)

    # WXGA
    for fps in [FPS23996, FPS24, FPS25]:
        prof = OutputProfile("1280x800", (1280, 800), fps, 5000)
        profs.append(prof)
    for fps in [FPS29997, FPS30, FPS50, FPS59994, FPS60]:
        prof = OutputProfile("1280x800", (1280, 800), fps, 7500)
        profs.append(prof)

    # WXGA+
    for fps in [FPS23996, FPS24, FPS25]:
        prof = OutputProfile("1440x900", (1440, 900), fps, 6000)
        profs.append(prof)
    for fps in [FPS29997, FPS30, FPS50, FPS59994, FPS60]:
        prof = OutputProfile("1440x900", (1440, 900), fps, 8500)
        profs.append(prof)

    # WSXGA+
    for fps in [FPS23996, FPS24, FPS25]:
        prof = OutputProfile("1680x1050", (1680, 1050), fps, 8000)
        profs.append(prof)
    for fps in [FPS29997, FPS30, FPS50, FPS60]:
        prof = OutputProfile("1680x1050", (1920, 1080), fps, 12000)
        profs.append(prof)

    # WUXGA
    for fps in [FPS23996, FPS24, FPS25]:
        prof = OutputProfile("1920x1200", (1920, 1200), fps, 9000)
        profs.append(prof)
    for fps in [FPS29997, FPS30, FPS50, FPS60]:
        prof = OutputProfile("1920x1200", (1920, 1200), fps, 13000)
        profs.append(prof)

    # WQXGA
    for fps in [FPS23996, FPS24, FPS25]:
        prof = OutputProfile("2560x1600", (2560, 1600), fps, 15000)
        profs.append(prof)
    for fps in [FPS29997, FPS30, FPS50, FPS60]:
        prof = OutputProfile("2560x1600", (2560, 1600), fps, 30000)
        profs.append(prof)

    # WQUXGA
    for fps in [FPS23996, FPS24, FPS25]:
        prof = OutputProfile("3840x2400", (3840, 2400), fps, 30000)
        profs.append(prof)
    for fps in [FPS29997, FPS30, FPS50, FPS60]:
        prof = OutputProfile("3840x2400", (3840, 2400), fps, 60000)
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
    if aspect in (Aspect.ASPECT_4_3, Aspect.ASPECT_3_4):
        result = __Create4_3Profiles()
    elif aspect in (Aspect.ASPECT_3_2, Aspect.ASPECT_2_3):
        result = __Create3_2Profiles()
    elif aspect in (Aspect.ASPECT_16_10, Aspect.ASPECT_10_16):
        result = __Create16_10Profiles()
    else:
        result = __Create16_9Profiles()

    if Aspect.IsPortraitMode(aspect):
        result = [p.ToPortraitMode() for p in result]

    return result


def GetMPEGProfiles():
    return __CreateMPEGProfiles()
