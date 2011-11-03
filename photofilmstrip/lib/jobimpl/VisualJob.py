# encoding: UTF-8

from .IVisualJob import IVisualJob
from .IVisualJobHandler import IVisualJobHandler
from .Job import Job
from .LogVisualJobHandler import LogVisualJobHandler


class VisualJob(Job, IVisualJob):
    def __init__(self, evt, target=None, args=None, kwargs=None,
                 visualJobHandler=None):
        Job.__init__(self, evt, target, args, kwargs)
        IVisualJob.__init__(self)
        
        if visualJobHandler is None:
            visualJobHandler = LogVisualJobHandler()
        assert isinstance(visualJobHandler, IVisualJobHandler)
        
        self.visualJobHandler = visualJobHandler
        
        self.__name = u""
        self.__progress = 0
        self.__maxProgress = 100
        self.__info = u""

    def _Finish(self):
        self.visualJobHandler.OnHandleJobDone()
    
    def GetName(self):
        return self.__name
    def SetName(self, name):
        self.__name = name
        self.visualJobHandler.OnHandleJobUpdate(("name",))

    def GetMaxProgress(self):
        return self.__maxProgress
    def SetMaxProgress(self, maxProgress):
        self.__maxProgress = maxProgress
        self.visualJobHandler.OnHandleJobUpdate(("maxProgress",))

    def StepProgress(self, info=None):
        self.__progress += 1
        if info is not None:
            self.__info = info
        self.visualJobHandler.OnHandleJobUpdate(("progress, info",))

    def GetInfo(self):
        return self.__info
    def SetInfo(self, info):
        self.__info = info
        self.visualJobHandler.OnHandleJobUpdate(("info",))

    def GetProgress(self):
        return self.__progress
    def SetProgress(self, progress):
        self.__progress = progress
        self.visualJobHandler.OnHandleJobUpdate(("progress",))
