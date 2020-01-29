# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2011 Jens Goepfert
#

import logging
import sys

from photofilmstrip.lib.DestructionManager import DestructionManager


class AppMixin:

    def __init__(self):
        self.InitLogging()

    def InitLogging(self):
        if "-d" in sys.argv:
            lvl = logging.DEBUG
        else:
            lvl = logging.WARNING
        logging.basicConfig(level=lvl,
                            format=self._GetLogFormat(),
                            datefmt='%d.%m.%Y %H:%M:%S',
                            filename=self._GetLogFilename())

    def InitI18N(self):
        from photofilmstrip.action.ActionI18N import ActionI18N
        ActionI18N().Execute()

    def InitGLib(self):
        import gi
        gi.require_version('Gst', '1.0')
        gi.require_version('GstController', '1.0')
        gi.require_version('GES', '1.0')
        gi.require_version('Gtk', '3.0')
        gi.require_version('Pango', '1.0')

        from gi.repository import Gst, GES
        Gst.init(None)
        GES.init()

    def Start(self):
        self.InitI18N()
        self.InitGLib()

        DestructionManager()

        from photofilmstrip.lib.jobimpl.JobManager import JobManager
        JobManager().Init(workerCount=2)
        JobManager().Init("render")

        try:
            return self._OnStart()
        finally:
            DestructionManager().Destroy()

    def _GetLogFormat(self):
        return '%(asctime)s (%(levelname)s) %(name)s: %(message)s'

    def _GetLogFilename(self):
        return None

    def _OnStart(self):
        raise NotImplementedError()
