# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Jens Goepfert
#


class IVisualJobManager:

    def RegisterJob(self, job):
        raise NotImplementedError()

    def RemoveJob(self, job):
        raise NotImplementedError()
