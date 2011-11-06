
class IJobContext(object):

    def GetId(self):
        raise NotImplementedError()
    
    def GetGroupId(self):
        raise NotImplementedError
    
    def GetTask(self, block, timeout):
        raise NotImplementedError()
    
    def GetResultToFetch(self):
        raise NotImplementedError()
    
    def PushResult(self, result):
        '''
        @param result:
        @return: the resultId
        '''
        raise NotImplementedError()
    
    def FetchResult(self, resultId):
        raise NotImplementedError()
    
    def Finalize(self):
        raise NotImplementedError()

    
class IWorker(object):
    
    def GetContextGroupId(self):
        raise NotImplementedError()
