# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2017 Jens Goepfert
#


class RenderException(Exception):

    def __init__(self, msg):
        Exception.__init__(self)
        self.message = msg
        self.msg = msg

    def GetMessage(self):
        return self.msg


class RendererException(RenderException):
    pass
