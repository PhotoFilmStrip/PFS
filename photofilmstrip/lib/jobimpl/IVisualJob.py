# encoding: UTF-8


class IVisualJob(object):
    
    def GetName(self):
        raise NotImplementedError()
    def SetName(self, value):
        raise NotImplementedError()
    
    def GetInfo(self):
        raise NotImplementedError()
    def SetInfo(self, info):
        raise NotImplementedError()
    
    def GetMaxProgress(self):
        raise NotImplementedError()
    def SetMaxProgress(self, value):
        raise NotImplementedError()
        
    def GetProgress(self):
        raise NotImplementedError()
    def SetProgress(self, value):
        raise NotImplementedError()
    def StepProgress(self, info=None, progress=1):
        raise NotImplementedError()

    def IsAborted(self):
        raise NotImplementedError()
    def Abort(self):
        raise NotImplementedError()
    
    def IsIdle(self):
        raise NotImplementedError()
    def SetIdle(self, value):
        raise NotImplementedError()
