# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Jens Goepfert
#

from .IWorkLoad import IWorkLoad


class WorkLoad(IWorkLoad):

    def __init__(self):
        pass

    def _Execute(self, jobContext):
        """
        internal - called by the framework
        """
        try:
            return self.Run(jobContext)
        finally:
            self._Finish()

    def _Finish(self):
        pass
