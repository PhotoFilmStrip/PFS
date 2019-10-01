# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Jens Goepfert
#

import logging

from .IVisualJobManager import IVisualJobManager

LOGGER = logging.getLogger("VisualJobManager")


class LogVisualJobManager(IVisualJobManager):

    def RegisterJob(self, job):
        LOGGER.debug("RegisterJob %s", job.GetName())

    def RemoveJob(self, job):
        LOGGER.debug("RemoveJob %s", job.GetName())
