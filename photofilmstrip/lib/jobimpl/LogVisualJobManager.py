# encoding: UTF-8

import logging

from .IVisualJobManager import IVisualJobManager

LOGGER = logging.getLogger("VisualJobManager")

class LogVisualJobManager(IVisualJobManager):
    
    def RegisterJob(self, job):
        LOGGER.debug("RegisterJob {0}", job.GetName())
    
    def UpdateJob(self, job, fields=None):
        LOGGER.debug("UpdateJob {0} [{1}]", job.GetName(), fields)
    
    def RemoveJob(self, job):
        LOGGER.debug("RemoveJob {0}", job.GetName())
