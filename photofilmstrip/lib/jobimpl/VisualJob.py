# encoding: UTF-8

from .IVisualJob import IVisualJob
from .IVisualJobHandler import IVisualJobHandler
from .Job import Job
from .LogVisualJobHandler import LogVisualJobHandler


class VisualJob(Job, IVisualJob):
    def __init__(self, name, target=None, args=None, kwargs=None,
                 maxProgress=-1,
                 visualJobHandler=None):
        IVisualJob.__init__(self)
        Job.__init__(self, target, args, kwargs)
        
        self.__defaultVisualJobHdl = LogVisualJobHandler()
        self.__visualJobHandler = []
        if visualJobHandler is not None:
            self.AddVisualJobHandler(visualJobHandler)
        
        self.__name = name
        self.__maxProgress = maxProgress
        self.__progress = 0
        self.__info = u""

        self.__aborted = False
        
    def __NotifyHandler(self, funcName, args=None):
        if args is None:
            args = ()
        for hdl in self.__visualJobHandler:
            func = getattr(hdl, funcName)
            func(self, *args)

    def AddVisualJobHandler(self, visualJobHandler):
        assert isinstance(visualJobHandler, IVisualJobHandler)
        if self.__defaultVisualJobHdl in self.__visualJobHandler:
            self.__visualJobHandler.remove(self.__defaultVisualJobHdl)

        self.__visualJobHandler.append(visualJobHandler)
    
    def RemoveVisualJobHandler(self, visualJobHandler):
        if visualJobHandler in self.__visualJobHandler:
            self.__visualJobHandler.remove(visualJobHandler)
        
        if len(self.__visualJobHandler) == 0:
            self.__visualJobHandler.append(self.__defaultVisualJobHdl)

    def Begin(self):
        self.__NotifyHandler("OnHandleJobBegin")
        
    def Done(self):
        self.__NotifyHandler("OnHandleJobDone")
    
    def GetName(self):
        return self.__name
    def SetName(self, name):
        self.__name = name
        self.__NotifyHandler("OnHandleJobUpdate", (("name",),))

    def GetMaxProgress(self):
        return self.__maxProgress
    def SetMaxProgress(self, maxProgress):
        self.__maxProgress = maxProgress
        self.__NotifyHandler("OnHandleJobUpdate", (("maxProgress",),))

    def StepProgress(self, info=None, progress=1):
        notifyFields = ("progress",)
        self.__progress += progress
        if info is not None:
            self.__info = info
            notifyFields = ("progress", "info")
        self.__NotifyHandler("OnHandleJobUpdate", (notifyFields,))

    def GetInfo(self):
        return self.__info
    def SetInfo(self, info):
        self.__info = info
        self.__NotifyHandler("OnHandleJobUpdate", (("info",),))

    def GetProgress(self):
        return self.__progress
    def SetProgress(self, progress):
        self.__progress = progress
        self.__NotifyHandler("OnHandleJobUpdate", (("progress",),))


    def IsAborted(self):
        return self.__aborted
    def Abort(self):
        self.__aborted = True
    
    def IsIdle(self):
        raise NotImplementedError()
    def SetIdle(self, value):
        raise NotImplementedError()
