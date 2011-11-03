# encoding: UTF-8


from .IVisualJobHandler import IVisualJobHandler
from .LogVisualJobManager import LOGGER


class LogVisualJobHandler(IVisualJobHandler):

    def OnHandleJobDone(self):
        LOGGER.debug("OnHandleJobDone {0}", self)
    
    def OnHandleJobUpdate(self, fields=None):
        LOGGER.debug("OnHandleJobUpdate {0}", self)
