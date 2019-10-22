# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#

import logging
import threading

from gi.repository import GObject, Gtk

from photofilmstrip.lib.DestructionManager import Destroyable


class GtkMainLoop(threading.Thread, Destroyable):

    __instance = None

    def __init__(self):
        threading.Thread.__init__(self, name="GtkMainLoop")
        Destroyable.__init__(self)

        self.__gtkMainloop = None

        if Gtk.main_level() == 0:
            self._Log(logging.DEBUG, "creating gtk mainloop")
            self.start()
        else:
            self._Log(logging.DEBUG, "gtk mainloop is already present")

    def run(self):
        self._Log(logging.DEBUG, "GTK mainloop starting...")

        GObject.threads_init()
        self.__gtkMainloop = GObject.MainLoop()
        self.__gtkMainloop.run()

        self._Log(logging.DEBUG, "GTK mainloop finished")

    def _Log(self, level, msg):
        return logging.getLogger('GtkMainLoop').log(level, msg)

    def Destroy(self):
        if self.__gtkMainloop is not None:
            self._Log(logging.DEBUG, "destroying GTK mainloop thread...")

            self.__gtkMainloop.quit()
            self.join(1.0)

            self._Log(logging.DEBUG, "GTK mainloop thread is dead")

            self.__gtkMainloop = None
        GtkMainLoop.__instance = None

    @classmethod
    def EnsureRunning(cls):
        if cls.__instance is None:
            cls.__instance = GtkMainLoop()
