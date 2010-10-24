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

import os, sys, logging

from optparse import OptionParser

from lib.common.ObserverPattern import Observer

from lib.Settings import Settings
from lib.util import Decode, Encode

from core.OutputProfile import OutputProfile, GetOutputProfiles
from core.PhotoFilmStrip import PhotoFilmStrip
from core.ProgressHandler import ProgressHandler
from core.RenderEngine import RenderEngine
from core.renderer import RENDERERS
from core.renderer.StreamRenderer import StreamRenderer


class CliGui(Observer):
    
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
        
    def ObservableUpdate(self, obj, arg):
        if isinstance(obj, ProgressHandler):
            if arg == 'maxProgress':
                self._maxProgress = obj.GetMaxProgress()
            elif arg == 'currentProgress':
                self._curProgress = obj.GetCurrentProgress()
            elif arg == 'info':
                self._info = obj.GetInfo()
            elif arg == 'done':
                self._info = _(u"all done")
            elif arg == 'aborting':
                self._info = obj.GetInfo()
            else:
                return
            self.__Output()
            
    def Info(self, options, rendererClass, profile):
        print
        print Settings.APP_NAME, Settings.APP_VERSION
        print u"(C) 2010 Jens G\xf6pfert"
        print Settings.APP_URL
        print 
        print u"%-20s: %s" % (_(u"processing project"), options.project)
        print u"%-20s: %s" % (_(u"using renderer"), rendererClass.GetName())
        print u"%-20s: %s" % (_(u"output format"), profile.GetName(withRes=True))
        print u"%-20s: %1.f (%s):" % (_(u"framerate"), profile.GetFramerate(), "PAL" if profile.GetVideoNorm() == OutputProfile.PAL else "NTSC") 
        print
        
    def Write(self, text):
        print text


class DummyGui(Observer):

    def __init__(self):
        Observer.__init__(self)
    def ObservableUpdate(self, obj, arg):
        pass
    def Info(self, options, rendererClass, profile):
        pass
    def Write(self, text):
        pass


def main():
    parser = OptionParser(prog="%s-cli" % Settings.APP_NAME.lower(), 
                          version="%%prog %s" % Settings.APP_VERSION)

    profiles = GetOutputProfiles()
    profStr = ", ".join(["%d=%s" % (idx, prof.GetName()) for idx, prof in enumerate(profiles)])
    
    formatStr = ", ".join(["%d=%s" % (idx, rdr.GetName()) for idx, rdr in enumerate(RENDERERS)])

    parser.add_option("-p", "--project", help=_(u"specifies the project file"))
    parser.add_option("-o", "--outputpath", help=_(u"The path where to save the output files. Use - for stdout."), metavar="PATH")
    parser.add_option("-t", "--profile", help=profStr + " [default: %default]", default=3, type="int")
    parser.add_option("-n", "--videonorm", help="n=NTSC, p=PAL [default: %default]", default="p")
    parser.add_option("-f", "--format", help=formatStr + " [default: %default]", default=1, type="int")
    parser.add_option("-d", "--draft", action="store_true", default=False, help=u"%s - %s" % (_(u"enable draft mode"), _(u"Activate this option to generate a preview of your PhotoFilmStrip. The rendering process will speed up dramatically, but results in lower quality.")))
    
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
        profile.SetVideoNorm(OutputProfile.PAL)
    elif options.videonorm == "n":
        profile.SetVideoNorm(OutputProfile.NTSC)
    else:
        parser.print_help()
        logging.error(_(u"invalid videonorm specified: %s"), options.videonorm)
        return 4
        

    if options.format not in range(len(RENDERERS)):
        parser.print_help()
        logging.error(_(u"invalid format specified: %s"), options.format)
        return 5
    rendererClass = RENDERERS[options.format]

    
    photoFilmStrip = PhotoFilmStrip()
    if not photoFilmStrip.Load(options.project):
        logging.error(_(u"cannot load photofilmstrip"))
        return 6
            

    outpath = os.path.dirname(photoFilmStrip.GetFilename())
    outpath = os.path.join(outpath, profile.GetName())
    outpath = Encode(outpath, sys.getfilesystemencoding())

    if options.outputpath:
        if options.outputpath == "-":
            outpath = "-"
            rendererClass = StreamRenderer
        else:  
            outpath = os.path.abspath(options.outputpath)

    if outpath != "-" and not os.path.exists(outpath):
        try:
            os.makedirs(outpath)
        except StandardError, err:
            logging.error(_(u"cannot create output path: %s"), err)
            return 7
        

#    settings = Settings()
#    savedProps = settings.GetRenderProperties(rendererClass.__name__)
#    for prop in rendererClass.GetProperties():
#        value = savedProps.get(prop.lower(), rendererClass.GetProperty(prop))
#        rendererClass.SetProperty(prop, value)
    
    renderer = rendererClass()
    renderer.Init(profile,
                  photoFilmStrip.GetAspect(), 
                  outpath, options.draft)

    audioFile = photoFilmStrip.GetAudioFile()
    if audioFile:
        audioFile = Encode(audioFile, sys.getfilesystemencoding())
        if not os.path.isfile(audioFile):
            logging.error(_(u"Audio file '%s' does not exist!"), audioFile)
            return 8

        renderer.SetAudioFile(audioFile)

    totalLength = photoFilmStrip.GetDuration(False)
    
    if rendererClass is StreamRenderer:
        cliGui = DummyGui()
    else:
        cliGui = CliGui()

    cliGui.Info(options, rendererClass, profile)

    progressHandler = ProgressHandler()
    progressHandler.AddObserver(cliGui)
    
    renderEngine = RenderEngine(renderer, progressHandler)

    try:
        result = renderEngine.Start(photoFilmStrip.GetPictures(), totalLength)
    except KeyboardInterrupt:
        progressHandler.Abort()
        cliGui.Write("\n" + _(u"...aborted!"))
        return 10
        
    if result:
        cliGui.Write(_(u"all done"))
    else:
        logging.error(_(u"Error: %s"), renderEngine.GetErrorMessage())
