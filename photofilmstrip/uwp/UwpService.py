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
from photofilmstrip.lib.DestructionManager import Destroyable
from photofilmstrip.core.ux import Ux


class UwpService(Destroyable, IVisualJobManager):

    __instance = None

    def __init__(self):
        Destroyable.__init__(self)
        pfsPath = os.path.dirname(sys.argv[0])
        svcClientPath = os.path.join(pfsPath, "..", "Tools", "UwpBridge.exe")
        logging.getLogger('UwpService').debug("trying UwpBridge.exe in '%s'", svcClientPath)

        self.svcClient = None
        if os.path.isfile(svcClientPath):
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            self.svcClient = subprocess.Popen([svcClientPath], stdin=subprocess.PIPE, startupinfo=startupinfo)

            JobManager().AddVisual(self)

    def __SendLines(self, lines):
        if self.svcClient is None:
            return

        logging.getLogger('UwpService').debug("Current Exit-Code %s", self.svcClient.poll())

        for line in lines:
            self.svcClient.stdin.write(line.encode("utf-8"))
            self.svcClient.stdin.write("\r\n".encode("utf-8"))
        self.svcClient.stdin.flush()

    @classmethod
    def GetInstance(cls):
        if cls.__instance is None:
            cls.__instance = UwpService()
        return cls.__instance

    def Destroy(self):
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


def ProcessCommandArgs():
    parser = optparse.OptionParser(usage=optparse.SUPPRESS_USAGE)
    parser.error = lambda msg: None
    parser.add_option("-u", "--uwp-open", help="opens a folder from uwp-bridge")
    options = parser.parse_args()[0]

    if options.uwp_open:
        from photofilmstrip.action.ActionOpenFolder import ActionOpenFolder
        ActionOpenFolder(options.uwp_open).Execute()
        return True

    return False
