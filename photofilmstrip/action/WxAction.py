# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2011 Jens Goepfert
#

from photofilmstrip.action.WxAbstractAction import WxAbstractAction


class WxAction(WxAbstractAction):

    def __init__(self, name, target, args=None, bmp=None):
        WxAbstractAction.__init__(self)
        self.name = name
        self.target = target
        if args is None:
            args = ()
        self.args = args
        self.bmp = bmp

    def GetName(self):
        return self.name

    def Execute(self):
        return self.target(*self.args)

    def GetBitmap(self, art=None):
        if isinstance(self.bmp, dict):
            return self.bmp.get(art)
        else:
            return self.bmp
