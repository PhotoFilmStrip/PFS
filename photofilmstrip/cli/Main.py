# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2010 Jens Goepfert
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

import os, sys, time, logging

from optparse import OptionParser

from photofilmstrip import Constants

from photofilmstrip.lib.common.ObserverPattern import Observer

from photofilmstrip.lib.util import Decode

from photofilmstrip.core.OutputProfile import OutputProfile, GetOutputProfiles
from photofilmstrip.core.ProjectFile import ProjectFile
from photofilmstrip.core.Renderer import RENDERERS
from photofilmstrip.core.renderer.StreamRenderer import StreamRenderer
from photofilmstrip.action.ActionRender import ActionRender
from photofilmstrip.lib.jobimpl.JobManager import JobManager
from photofilmstrip.lib.jobimpl.IVisualJobHandler import IVisualJobHandler


class CliGui(IVisualJobHandler):
    
    def __init__(self):
        Observer.__init__(self)
        self._maxProgress = 100
        self._curProgress = 0
        self._info = u""
        
    def __Output(self):
        percent = float(self._curProgress) / self._maxProgress
        width = 37
        chars = u"=" * int(width * percent)
        chars = chars[:width] 
        line = u"|%-3d%%%-37s| %s" % (int(percent * 100), chars, self._info)
        line = line[:80]
        print u"%-80s\r" % (line),
        
    def OnHandleJobBegin(self, jobContext):
        pass
    
    def OnHandleJobDone(self, jobContext):
        self._info = _(u"all done")
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
        print
        print Constants.APP_NAME, Constants.APP_VERSION_EX
        print u"(C) 2010 Jens G\xf6pfert"
        print Constants.APP_URL
        print 
        print u"%-20s: %s" % (_(u"processing project"), project)
        print u"%-20s: %s" % (_(u"using renderer"), rendererClass.GetName())
        print u"%-20s: %s" % (_(u"output format"), profile.GetName(withRes=True))
        print u"%-20s: %1.f (%s):" % (_(u"framerate"), profile.GetFramerate(), "PAL" if profile.GetVideoNorm() == OutputProfile.PAL else "NTSC") 
        print
        
    def Write(self, text):
        print text


class DummyGui(IVisualJobHandler):

    def OnHandleJobBegin(self, jobContext):
        pass
    def OnHandleJobDone(self, jobContext):
        pass
    def OnHandleJobUpdate(self, jobContext, fields=None):
        pass


def main():
    parser = OptionParser(prog="%s-cli" % Constants.APP_NAME.lower(), 
                          version="%%prog %s" % Constants.APP_VERSION_EX)

    profiles = GetOutputProfiles()
    profStr = ", ".join(["%d=%s" % (idx, prof.GetName()) for idx, prof in enumerate(profiles)])
    
    formatStr = ", ".join(["%d=%s" % (idx, rdr.GetName()) for idx, rdr in enumerate(RENDERERS)])

    parser.add_option("-p", "--project", help=_(u"specifies the project file"))
    parser.add_option("-o", "--outputpath", help=_(u"The path where to save the output files. Use - for stdout."), metavar="PATH")
    parser.add_option("-t", "--profile", help=profStr + " [default: %default]", default=3, type="int")
    parser.add_option("-n", "--videonorm", help="n=NTSC, p=PAL [default: %default]", default="p")
    parser.add_option("-f", "--format", help=formatStr + " [default: %default]", default=1, type="int")
    parser.add_option("-a", "--draft", action="store_true", default=False, help=u"%s - %s" % (_(u"enable draft mode"), _(u"Activate this option to generate a preview of your PhotoFilmStrip. The rendering process will speed up dramatically, but results in lower quality.")))
    parser.add_option("-d", "--debug", action="store_true", default=False, help=u"enable debug logging")
    
    options = parser.parse_args()[0]

    if options.project:
        options.project = Decode(options.project, sys.getfilesystemencoding())
        options.project = os.path.abspath(options.project)
        if not os.path.isfile(options.project):
            logging.error(_(u"project file does not exist: %s"), options.project)
            return 1
    else:
        parser.print_help()
        logging.error(_(u"no project file specified!"))
        return 2


    if options.profile >= len(profiles):
        parser.print_help()
        logging.error(_(u"invalid profile specified: %s"), options.profile)
        return 3
    profile = profiles[options.profile]


    if options.videonorm == "p":
        videoNorm = OutputProfile.PAL
    elif options.videonorm == "n":
        videoNorm = OutputProfile.NTSC
    else:
        parser.print_help()
        logging.error(_(u"invalid videonorm specified: %s"), options.videonorm)
        return 4
        

    if options.format not in range(len(RENDERERS)):
        parser.print_help()
        logging.error(_(u"invalid format specified: %s"), options.format)
        return 5
    rendererClass = RENDERERS[options.format]

    
    prjFile = ProjectFile(filename=options.project)
    if not prjFile.Load():
        logging.error(_(u"cannot load photofilmstrip"))
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
                except StandardError, err:
                    logging.error(_(u"cannot create output path: %s"), err)
                    return 7
    else:
        outpath = None
            

    project = prjFile.GetProject()
    ar = ActionRender(project, profile, videoNorm, rendererClass, False, outpath)
    
    audioFile = project.GetAudioFile()
    if not ar.CheckFile(audioFile):
        logging.error(_(u"Audio file '%s' does not exist!"), audioFile)
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
        cliGui.Write("\n" + _(u"...aborted!"))
        return 10
        
    resultObj = renderJob.GetResultObject()
    result = resultObj.GetResult()
    if result:
        cliGui.Write(_(u"all done"))
#    else:
#        logging.error(_(u"Error: %s"), renderEngine.GetErrorMessage())
