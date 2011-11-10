# encoding: UTF-8

class IVisualJobManager(object):
    
    def RegisterJob(self, job):
        raise NotImplementedError()
    
    def UpdateJob(self, job, fields=None):
        raise NotImplementedError()
    
    def RemoveJob(self, job):
        raise NotImplementedError()
