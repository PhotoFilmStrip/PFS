# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2011 Jens Goepfert
#


class IAction:

    def GetName(self):
        raise NotImplementedError()

    def Execute(self):
        raise NotImplementedError()
