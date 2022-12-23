# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2010 Jens Goepfert
#

import os, time, logging

from optparse import OptionParser

from photofilmstrip import Constants

from photofilmstrip.lib.util import CheckFile

from photofilmstrip.core.Aspect import Aspect
from photofilmstrip.core.OutputProfile import (
    GetOutputProfiles, GetMPEGProfiles)
from photofilmstrip.core.ProjectFile import ProjectFile
from photofilmstrip.core.Renderers import RENDERERS
from photofilmstrip.core.renderer.StreamRenderer import StreamRenderer
from photofilmstrip.action.ActionRender import ActionRender
from photofilmstrip.lib.jobimpl.JobManager import JobManager
from photofilmstrip.lib.jobimpl.IVisualJobHandler import IVisualJobHandler


class CliGui(IVisualJobHandler):

    def __init__(self):
        self._maxProgress = 100
        self._curProgress = 0
        self._info = ""

    def __Output(self):
        percent = float(self._curProgress) / self._maxProgress
        width = 37
        chars = "=" * int(width * percent)
        chars = chars[:width]
        line = "|%-3d%%%-37s| %s" % (int(percent * 100), chars, self._info)
        line = line[:80]
        print("%-80s\r" % (line), end=' ')

    def OnHandleJobBegin(self, jobContext):
        pass

    def OnHandleJobDone(self, jobContext):
        self._info = _("all done")
        self.__Output()

    def OnHandleJobUpdate(self, jobContext, fields=None):
        if 'maxProgress' in fields:
            self._maxProgress = jobContext.GetMaxProgress()
        if 'progress' in fields:
            self._curProgress = jobContext.GetProgress()
        if 'info' in fields:
            self._info = jobContext.GetInfo()
        self.__Output()

    def Info(self, project, rendererClass, profile):
        print()
        print(Constants.APP_NAME, Constants.APP_VERSION_FULL)
        print("(C) 2019 Jens Göpfert")
        print(Constants.APP_URL)
        print()
        print("%-20s: %s" % (_("processing project"), project))
        print("%-20s: %s" % (_("using renderer"), rendererClass.GetName()))
        print("%-20s: %s" % (_("output format"), profile.GetName(
            withRes=True)))
        print("%-20s: %1.f" % (_("framerate"),
                               profile.GetFrameRate().AsFloat()))
        print()

    def Write(self, text):
        print(text)


class DummyGui(IVisualJobHandler):

    def Info(self, project, rendererClass, profile):
        pass

    def OnHandleJobBegin(self, jobContext):
        pass

    def OnHandleJobDone(self, jobContext):
        pass

    def OnHandleJobUpdate(self, jobContext, fields=None):
        pass


def main(showHelp=False):
    parser = OptionParser(prog="%s-cli" % Constants.APP_NAME.lower(),
                          version="%%prog %s" % Constants.APP_VERSION_SUFFIX)

    profiles = GetOutputProfiles() + GetMPEGProfiles()
    profStr = ", ".join(["%d=%s" % (
        idx,
        prof.GetName()) for idx, prof in enumerate(profiles)])

    formatStr = ", ".join(["%d=%s" % (idx, rdr.GetName()) for idx, rdr in enumerate(RENDERERS)])

    parser.add_option("-p", "--project", help=_("specifies the project file"))
    parser.add_option("-o", "--outputpath", help=_("The path where to save the output files. Use - for stdout."), metavar="PATH")
    parser.add_option("-t", "--profile", help=profStr + " [default: %default]", default=0, type="int")
    parser.add_option("-n", "--videonorm", help=_("Option videonorm is deprecated, use an appropriate profile!"))
    parser.add_option("-f", "--format", help=formatStr + " [default: %default]", default=4, type="int")
    parser.add_option("-a", "--draft", action="store_true", default=False, help="%s - %s" % (_("enable draft mode"), _("Activate this option to generate a preview of your PhotoFilmStrip. The rendering process will speed up dramatically, but results in lower quality.")))
    parser.add_option("-d", "--debug", action="store_true", default=False, help="enable debug logging")

    if showHelp:
        parser.print_help()
        return 0

    options = parser.parse_args()[0]

    if options.project:
        options.project = os.path.abspath(options.project)
        if not os.path.isfile(options.project):
            logging.error(_("project file does not exist: %s"), options.project)
            return 1
    else:
        parser.print_help()
        logging.error(_("no project file specified!"))
        return 2

    if options.videonorm:
        parser.print_help()
        logging.error(_("Option videonorm is deprecated, use an appropriate profile!"))
        return 4

    if options.format not in range(len(RENDERERS)):
        parser.print_help()
        logging.error(_("invalid format specified: %s"), options.format)
        return 5
    rendererClass = RENDERERS[options.format]

    if options.profile >= len(profiles):
        parser.print_help()
        logging.error(_("invalid profile specified: %s"), options.profile)
        return 3
    profile = profiles[options.profile]

    prjFile = ProjectFile(filename=options.project)
    if not prjFile.Load():
        logging.error(_("cannot load project"))
        return 6

    if options.outputpath:
        if options.outputpath == "-":
            outpath = "-"
            rendererClass = StreamRenderer
        else:
            outpath = os.path.abspath(options.outputpath)
            if not os.path.exists(outpath):
                try:
                    os.makedirs(outpath)
                except Exception as err:
                    logging.error(_("cannot create output path: %s"), err)
                    return 7
    else:
        outpath = None

    project = prjFile.GetProject()
    if Aspect.IsPortraitMode(project.GetAspect()):
        profile = profile.ToPortraitMode()

    ar = ActionRender(project, profile, rendererClass, False, outpath)

    audioFile = project.GetAudioFile()
    if not CheckFile(audioFile):
        logging.error(_("Audio file '%s' does not exist!"), audioFile)
        return 8

    if rendererClass is StreamRenderer:
        cliGui = DummyGui()
    else:
        cliGui = CliGui()

    cliGui.Info(options.project, rendererClass, profile)

    ar.Execute()
    renderJob = ar.GetRenderJob()
    renderJob.AddVisualJobHandler(cliGui)

    JobManager().EnqueueContext(renderJob)

    try:
        while not renderJob.IsDone():
            time.sleep(0.1)
    except KeyboardInterrupt:
        renderJob.Abort()
        cliGui.Write("\n" + _("...aborted!"))
        return 10

    resultObj = renderJob.GetResultObject()
    result = resultObj.GetResult()
    if result:
        cliGui.Write(_("all done"))
#    else:
#        logging.error(_("Error: %s"), renderEngine.GetErrorMessage())
