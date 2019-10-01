# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#


class SingletonType(type):

    def __init__(self, name, bases, dict):
        type.__init__(self, name, bases, dict)
        self.instance = None

    def __call__(self):
        if self.instance is None:
            self.instance = type.__call__(self)
        return self.instance


class Singleton(metaclass=SingletonType):
    pass
