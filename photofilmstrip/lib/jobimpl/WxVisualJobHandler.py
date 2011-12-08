# encoding: UTF-8

import wx

from .IVisualJobHandler import IVisualJobHandler
from .ResultObject import ResultObject

EVT_JOB_RESULT_TYPE = wx.NewEventType()
EVT_JOB_RESULT = wx.PyEventBinder(EVT_JOB_RESULT_TYPE, 1)

EVT_JOB_UPDATE_TYPE = wx.NewEventType()
EVT_JOB_UPDATE = wx.PyEventBinder(EVT_JOB_UPDATE_TYPE, 1)


class WxVisualJobHandler(IVisualJobHandler):
    
    def __init__(self, win=None):
        self.__id = wx.NewId()
        if win is None:
            win = self
        assert isinstance(win, wx.EvtHandler)
        self.__win = win
        
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
    

class ResultEvent(wx.PyEvent):

    def __init__(self, ident, resultObj):
        wx.PyEvent.__init__(self, ident, EVT_JOB_RESULT_TYPE)
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
        wx.PyEvent.__init__(self, ident, EVT_JOB_UPDATE_TYPE)
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
