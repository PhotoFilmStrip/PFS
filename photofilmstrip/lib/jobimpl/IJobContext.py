# encoding: UTF-8

class IJobContext(object):
    '''
    The JobContext interface handles the processing of a long running job.
    A Job can contain of multiple tasks (smaller workloads) that may processed
    on different worker threads. The JobContext belongs to a group that decides
    on which workers the workloads are processed.
    '''

    def GetGroupId(self):
        raise NotImplementedError
    
    def GetWorkLoad(self):
        raise NotImplementedError()
    
    def PushResult(self, resultObject):
        raise NotImplementedError()
    
    def _Begin(self):
        """
        internal - called from the framework
        """
        raise NotImplementedError()
    def Begin(self):
        raise NotImplementedError()
    
    def _Done(self):
        """
        internal - called from the framework
        """
        raise NotImplementedError()
    def Done(self):
        raise NotImplementedError()

    def IsDone(self):
        raise NotImplementedError()
    
    def IsAborted(self):
        raise NotImplementedError()
    def Abort(self, msg=None):
        raise NotImplementedError()
    
    def IsIdle(self):
        raise NotImplementedError()
    


    
class IWorker(object):
    
    def GetContextGroupId(self):
        raise NotImplementedError()
