

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
    
    return [vcd, svcd, dvd, medium, hd, fullhd]


DEFAULT_PROFILES = __CreateDefaultProfiles()    