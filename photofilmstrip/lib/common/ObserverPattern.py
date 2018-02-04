# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
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
