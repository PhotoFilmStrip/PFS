# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Jens Goepfert
#


class IVisualJobHandler:

    def OnHandleJobBegin(self, jobContext):
        raise NotImplementedError()

    def OnHandleJobDone(self, jobContext):
        raise NotImplementedError()

    def OnHandleJobUpdate(self, jobContext, fields=None):
        raise NotImplementedError()
