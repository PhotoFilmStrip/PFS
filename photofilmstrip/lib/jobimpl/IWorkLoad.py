# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Jens Goepfert
#


class IWorkLoad:

    def _Execute(self, jobContext):
        raise NotImplementedError()

    def _Finish(self):
        raise NotImplementedError()

    def Run(self, jobContext):
        raise NotImplementedError()
