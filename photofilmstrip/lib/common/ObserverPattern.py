# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#


class Observable:

    def __init__(self):
        self.__observers = []

    def AddObserver(self, observer):
        if isinstance(observer, Observer):
            if observer not in self.__observers:
                self.__observers.append(observer)
        else:
            raise RuntimeError()

    def RemoveObserver(self, observer):
        self.__observers.remove(observer)

    def Notify(self, arg=None):
        for observer in self.__observers:
            observer.ObservableUpdate(self, arg)


class Observer:

    def ObservableUpdate(self, obj, arg):
        raise NotImplementedError()
