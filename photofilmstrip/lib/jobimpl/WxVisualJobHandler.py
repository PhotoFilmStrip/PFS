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
        if win is None:
            win = self
        assert isinstance(win, wx.EvtHandler)
        self.__win = win
        
    def GetId(self):
        pass
        
    def OnHandleJobBegin(self, jobContext):
        pass
    
    def OnHandleJobDone(self, jobContext):
        evt = ResultEvent(self.__win.GetId(), jobContext.GetResultObject())
        wx.PostEvent(self.__win, evt)
    
    def OnHandleJobUpdate(self, jobContext, fields=None):
        evt = UpdateEvent(self.__win.GetId(), fields)
        wx.PostEvent(self.__win, evt)
    

class ResultEvent(wx.PyEvent):

    def __init__(self, ident, resultObj):
        wx.PyEvent.__init__(self, ident, EVT_JOB_RESULT_TYPE)
        assert isinstance(resultObj, ResultObject)
        self.__resultObj = None
        
    def _SetResultObj(self, resultObj):
        self.__resultObj = resultObj

    def GetResult(self, printTraceback=True):
        return self.__resultObj.GetResult(printTraceback)


class UpdateEvent(wx.PyEvent):

    def __init__(self, ident, fields):
        wx.PyEvent.__init__(self, ident, EVT_JOB_UPDATE_TYPE)
        self.__fields = fields

    def GetFields(self):
        return self.__fields

