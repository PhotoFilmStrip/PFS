
class IJobContext(object):

    def GetGroupId(self):
        raise NotImplementedError
    
    def GetWorkLoad(self, block, timeout):
        raise NotImplementedError()
    
    def PushResult(self, resultObject):
        raise NotImplementedError()
    
    def Begin(self):
        raise NotImplementedError()
    
    def Finalize(self):
        raise NotImplementedError()

    
class IWorker(object):
    
    def GetContextGroupId(self):
        raise NotImplementedError()
