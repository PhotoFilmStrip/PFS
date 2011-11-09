
class IJobContext(object):

    def GetGroupId(self):
        raise NotImplementedError
    
    def GetWorkLoad(self, block, timeout):
        raise NotImplementedError()
    
    def PushResult(self, resultObject):
        raise NotImplementedError()
    
    def Begin(self):
        raise NotImplementedError()
    
    def Done(self):
        raise NotImplementedError()
    
    def IsAborted(self):
        raise NotImplementedError()
    def Abort(self):
        raise NotImplementedError()
    
    def IsIdle(self):
        raise NotImplementedError()
    def SetPaused(self, value):
        raise NotImplementedError()
    


    
class IWorker(object):
    
    def GetContextGroupId(self):
        raise NotImplementedError()
