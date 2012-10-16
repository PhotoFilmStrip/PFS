# encoding: UTF-8

import wx

from photofilmstrip.lib.jobimpl.IVisualJobManager import IVisualJobManager
from photofilmstrip.lib.jobimpl.JobManager import JobManager
from photofilmstrip.lib.jobimpl.Job import Job

_EVT_REGISTER_JOB_TYPE = wx.NewEventType()
EVT_REGISTER_JOB = wx.PyEventBinder(_EVT_REGISTER_JOB_TYPE, 1)

_EVT_REMOVE_JOB_TYPE = wx.NewEventType()
EVT_REMOVE_JOB = wx.PyEventBinder(_EVT_REMOVE_JOB_TYPE, 1)


class WxVisualJobManager(IVisualJobManager):
    
    def __init__(self, win=None):
        self.__id = wx.NewId()
        if win is None:
            win = self
        assert isinstance(win, wx.EvtHandler)
        self.__win = win
        JobManager().AddVisual(self)

    def GetId(self):
        return self.__id
        
    def RegisterJob(self, job):
        evt = JobEvent(self.__win.GetId(), job, _EVT_REGISTER_JOB_TYPE)
        wx.PostEvent(self.__win, evt)
    
    def RemoveJob(self, job):
        evt = JobEvent(self.__win.GetId(), job, _EVT_REMOVE_JOB_TYPE)
        wx.PostEvent(self.__win, evt)


class JobEvent(wx.PyEvent):
    
    def __init__(self, ident, job, evtType):
        wx.PyEvent.__init__(self, ident, evtType)
        assert isinstance(job, Job)
        self.__job = job
        
    def GetJob(self):
        return self.__job
