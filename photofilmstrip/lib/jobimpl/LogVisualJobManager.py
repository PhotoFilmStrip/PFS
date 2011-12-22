# encoding: UTF-8

import logging

from .IVisualJobManager import IVisualJobManager

LOGGER = logging.getLogger("VisualJobManager")

class LogVisualJobManager(IVisualJobManager):
    
    def RegisterJob(self, job):
        LOGGER.debug("RegisterJob %s", job.GetName())
    
    def UpdateJob(self, job, fields=None):
        LOGGER.debug("UpdateJob %s [%s]", job.GetName(), fields)
    
    def RemoveJob(self, job):
        LOGGER.debug("RemoveJob %s", job.GetName())
