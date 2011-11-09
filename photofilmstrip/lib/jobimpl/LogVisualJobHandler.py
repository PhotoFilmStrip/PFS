# encoding: UTF-8


from .IVisualJobHandler import IVisualJobHandler
from .LogVisualJobManager import LOGGER


class LogVisualJobHandler(IVisualJobHandler):

    def OnHandleJobBegin(self, jobContext):
        LOGGER.debug("OnHandleJobBegin %s", jobContext)
    
    def OnHandleJobDone(self, jobContext):
        LOGGER.debug("OnHandleJobDone %s", jobContext)
    
    def OnHandleJobUpdate(self, jobContext, fields=None):
        LOGGER.debug("OnHandleJobUpdate %s -> %s", jobContext, fields)
