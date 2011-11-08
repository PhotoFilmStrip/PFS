
import sys

import wx
from photofilmstrip.lib.jobimpl.ResultObject import ResultObject

EVT_JOB_RESULT_TYPE = wx.NewEventType()
EVT_JOB_RESULT = wx.PyEventBinder(EVT_JOB_RESULT_TYPE, 1)


class SystemEvent(wx.PyEvent):

    def __init__(self, notifyObject, notifyCallback):
        self.notifyObject = notifyObject
        self.notifyCallback = notifyCallback

        if isinstance(notifyObject, wx.Window):
            wx.PyEvent.__init__(self, notifyObject.GetId(), EVT_JOB_RESULT_TYPE)
            notifyObject.Bind(EVT_JOB_RESULT, notifyCallback)

    def DispatchEvent(self):
        if isinstance(self.notifyObject, wx.Window):
            wx.PostEvent(self.notifyObject, self)
#            self.notifyObject.Unbind(EVT_TASK_RESULT)


class ResultEvent(SystemEvent):

    def __init__(self, notifyObject, notifyCallback):
        SystemEvent.__init__(self, notifyObject, notifyCallback)
        self.__resultObj = None
        
    def _SetResultObj(self, resultObj):
        assert isinstance(resultObj, ResultObject)
        self.__resultObj = resultObj

    def GetResult(self, printTraceback=True):
        return self.__resultObj.GetResult(printTraceback)


#class AutocheckResultEvent(ResultEvent):
#    """
#    Auf Instanzen dieses ResultEvents wird automatisch nach Abschluss der
#    jeweiligen Task die Methode GetResult() aufgerufen, um eine Exception,
#    die u.U. waehrend der Taskausfuehrung aufgetreten ist, erneut zu werfen
#    und damit den Fehler bei der Taskausfuehrung auszugeben.
#    """
#    def __init__(self):
#        AutocheckResultEvent.__init__(None,
#                                      lambda evt: evt.GetResult())

