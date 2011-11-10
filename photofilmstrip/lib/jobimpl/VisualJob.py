# encoding: UTF-8

from .IVisualJob import IVisualJob
from .IVisualJobHandler import IVisualJobHandler
from .Job import Job
from .LogVisualJobHandler import LogVisualJobHandler


class VisualJob(Job, IVisualJob):
    def __init__(self, name, target=None, args=None, kwargs=None,
                 maxProgress=-1,
                 visualJobHandler=None,
                 groupId="general"):
        Job.__init__(self, target, args, kwargs, groupId)
        IVisualJob.__init__(self)
        
        self.__defaultVisualJobHdl = LogVisualJobHandler()
        self.__visualJobHandler = []
        if visualJobHandler is not None:
            self.AddVisualJobHandler(visualJobHandler)
        
        self.__name = name
        self.__maxProgress = maxProgress
        self.__progress = 0
        self.__info = u""
        
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

    def _Begin(self):
        self.__NotifyHandler("OnHandleJobBegin")
        Job._Begin(self)
        
    def _Done(self):
        Job._Done(self)
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

#    def IsIdle(self):
#        raise NotImplementedError()
#    def SetIdle(self, value):
#        raise NotImplementedError()
