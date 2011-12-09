# encoding: UTF-8

import threading

import wx

from .IVisualJobHandler import IVisualJobHandler
from .ResultObject import ResultObject

_EVT_JOB_RESULT_TYPE = wx.NewEventType()
EVT_JOB_RESULT = wx.PyEventBinder(_EVT_JOB_RESULT_TYPE, 1)

_EVT_JOB_UPDATE_TYPE = wx.NewEventType()
EVT_JOB_UPDATE = wx.PyEventBinder(_EVT_JOB_UPDATE_TYPE, 1)

_EVT_JOB_UIINTERACT_TYPE = wx.NewEventType()
EVT_JOB_UIINTERACT = wx.PyEventBinder(_EVT_JOB_UIINTERACT_TYPE, 1)


class WxVisualJobHandler(IVisualJobHandler):
    
    def __init__(self, win=None):
        self.__id = wx.NewId()
        if win is None:
            win = self
        assert isinstance(win, wx.EvtHandler)
        self.__win = win
        
        self.__win.Bind(EVT_JOB_UIINTERACT, self.__OnInteract)
        
    def GetId(self):
        return self.__id
        
    def OnHandleJobBegin(self, jobContext):
        evt = UpdateEvent(self.__win.GetId(), None, UpdateEvent.KIND_BEGIN)
        wx.PostEvent(self.__win, evt)
    
    def OnHandleJobDone(self, jobContext):
        evt = ResultEvent(self.__win.GetId(), jobContext.GetResultObject())
        wx.PostEvent(self.__win, evt)

        evt = UpdateEvent(self.__win.GetId(), None, UpdateEvent.KIND_DONE)
        wx.PostEvent(self.__win, evt)
    
    def OnHandleJobUpdate(self, jobContext, fields=None):
        evt = UpdateEvent(self.__win.GetId(), fields, UpdateEvent.KIND_UPDATE)
        wx.PostEvent(self.__win, evt)
        
    def OnHandleJobInteraction(self, jobContext, evt):
        assert isinstance(evt, WxInteractionEvent)
        evt._threadEvt = threading.Event()
        evt._job = jobContext
        wx.PostEvent(self.__win, evt)
        evt._threadEvt.wait()
        return evt.GetSkipped()
    
    def __OnInteract(self, event):
        assert wx.Thread_IsMain()
        try:
            event.OnProcess(self.__win)
        finally:
            event._threadEvt.set()



class ResultEvent(wx.PyEvent):

    def __init__(self, ident, resultObj):
        wx.PyEvent.__init__(self, ident, _EVT_JOB_RESULT_TYPE)
        assert isinstance(resultObj, ResultObject)
        self.__resultObj = resultObj
        
    def _SetResultObj(self, resultObj):
        self.__resultObj = resultObj

    def GetResult(self, printTraceback=True):
        return self.__resultObj.GetResult(printTraceback)

    def GetSource(self):
        return self.__resultObj.GetSource()


class UpdateEvent(wx.PyEvent):
    
    KIND_UPDATE = 1
    KIND_BEGIN  = 2
    KIND_DONE    = 4

    def __init__(self, ident, fields, kind):
        wx.PyEvent.__init__(self, ident, _EVT_JOB_UPDATE_TYPE)
        if fields is None:
            fields = []
        self.__fields = fields
        self.__kind = kind

    def GetFields(self):
        return self.__fields

    def IsBegin(self):
        return self.__kind == UpdateEvent.KIND_BEGIN

    def IsDone(self):
        return self.__kind == UpdateEvent.KIND_DONE

    def IsUpdate(self):
        return self.__kind == UpdateEvent.KIND_UPDATE


class WxInteractionEvent(wx.PyEvent):

    def __init__(self):
        wx.PyEvent.__init__(self, eventType=_EVT_JOB_UIINTERACT_TYPE)
        self._threadEvt = None
        self._job = None
        
    def GetJob(self):
        return self._job
    
    def OnProcess(self, wxParent):
        raise NotImplementedError()
