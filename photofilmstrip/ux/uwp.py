# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2018 Jens Goepfert
#

import logging
import optparse
import os
import subprocess
import sys

from photofilmstrip.lib.jobimpl.IVisualJobManager import IVisualJobManager
from photofilmstrip.lib.jobimpl.JobManager import JobManager
from photofilmstrip.ux.Ux import UxAdapter, Ux, UxPreventStartupSignal


class UwpAdapter(UxAdapter, IVisualJobManager):

    def __init__(self, svcClientPath):
        self.svcClientPath = svcClientPath
        self.svcClient = None

    def OnInit(self):
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        self.svcClient = subprocess.Popen(
            [self.svcClientPath], stdin=subprocess.PIPE,
            startupinfo=startupinfo)

        JobManager().AddVisual(self)

    def __SendLines(self, lines):
        if self.svcClient is None:
            return

        logging.getLogger('UwpService').debug("Current Exit-Code %s", self.svcClient.poll())

        for line in lines:
            self.svcClient.stdin.write(line.encode("utf-8"))
            self.svcClient.stdin.write("\r\n".encode("utf-8"))
        self.svcClient.stdin.flush()

    def OnDestroy(self):
        lines = ["exit"]
        self.__SendLines(lines)

    def ShowToast(self, title, msg, image, launch):
        lines = ["notify", title, msg, image, "--uwp-open \"" + launch + "\"", "process"]
        self.__SendLines(lines)

    def LogEvent(self, eventName):
        lines = ['event', eventName, "process"]
        self.__SendLines(lines)

    def RegisterJob(self, job):
        if isinstance(job, Ux):
            for uxEvent in job.GetUxEvents():
                self.LogEvent(uxEvent)

    def RemoveJob(self, job):
        if job.GetGroupId() != "render":
            return
        if not job.IsAborted():
            self.ShowToast(_("Slideshow created!"), job.GetName(),
                           job.GetOutputFile(),
                           job.GetOutputFile())

    def OnStart(self):
        parser = optparse.OptionParser(usage=optparse.SUPPRESS_USAGE)
        parser.error = lambda msg: None
        parser.add_option("-u", "--uwp-open", help="opens a folder from uwp-bridge")
        options = parser.parse_args()[0]

        if options.uwp_open:
            from photofilmstrip.action.ActionOpenFolder import ActionOpenFolder
            ActionOpenFolder(options.uwp_open).Execute()

            raise UxPreventStartupSignal()


def ux_init():
    pfsPath = os.path.dirname(sys.argv[0])
    svcClientPath = os.path.join(pfsPath, "..", "Tools", "UwpBridge.exe")
    logging.getLogger('UwpAdapter').debug(
        "trying UwpBridge.exe in '%s'", svcClientPath)

    if os.path.isfile(svcClientPath):
        return UwpAdapter(svcClientPath)
