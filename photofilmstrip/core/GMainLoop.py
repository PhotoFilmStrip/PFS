# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#

import os
import logging
import threading

from gi.repository import GObject

from photofilmstrip.lib.DestructionManager import Destroyable


class GMainLoop(threading.Thread, Destroyable):

    __instance = None

    def __init__(self):
        threading.Thread.__init__(self, name="GMainLoop")
        Destroyable.__init__(self)

        self.__gMainloop = None

        if os.name == "nt":
            self._Log(logging.DEBUG, "creating GObject MainLoop")
            self.start()

    def run(self):
        self._Log(logging.DEBUG, "GObject MainLoop starting...")

        GObject.threads_init()
        self.__gMainloop = GObject.MainLoop()
        self.__gMainloop.run()

        self._Log(logging.DEBUG, "GObject MainLoop finished")

    def _Log(self, level, msg):
        return logging.getLogger('GMainLoop').log(level, msg)

    def Destroy(self):
        if self.__gMainloop is not None:
            self._Log(logging.DEBUG, "destroying GObject MainLoop thread...")

            self.__gMainloop.quit()
            self.join(1.0)

            self._Log(logging.DEBUG, "GObject MainLoop thread is dead")

            self.__gMainloop = None
        GMainLoop.__instance = None

    @classmethod
    def EnsureRunning(cls):
        if cls.__instance is None:
            cls.__instance = GMainLoop()
