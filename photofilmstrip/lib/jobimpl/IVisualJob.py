# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Jens Goepfert
#


class IVisualJob:

    def GetName(self):
        raise NotImplementedError()

    def SetName(self, value):
        raise NotImplementedError()

    def GetInfo(self):
        raise NotImplementedError()

    def SetInfo(self, info):
        raise NotImplementedError()

    def GetMaxProgress(self):
        raise NotImplementedError()

    def SetMaxProgress(self, value):
        raise NotImplementedError()

    def GetProgress(self):
        raise NotImplementedError()

    def SetProgress(self, value):
        raise NotImplementedError()

    def StepProgress(self, info=None, progress=1):
        raise NotImplementedError()
