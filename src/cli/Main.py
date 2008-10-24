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

import os, sys

from optparse import OptionParser

from lib.common.ObserverPattern import Observer

from lib.Settings import Settings

from core.renderer.SingleFileRenderer import SingleFileRenderer
from core.renderer.ShellScriptRenderer import ShellScriptRenderer
from core.renderer.MovieRenderer import MovieRenderer
from core.ProgressHandler import ProgressHandler
from core.PhotoFilmStrip import PhotoFilmStrip


class CliGui(Observer):
    
    def __init__(self):
        Observer.__init__(self)
        self._maxProgress = 100
        self._curProgress = 0
        self._info = ""
        
    def __Output(self):
        percent = float(self._curProgress) / self._maxProgress
        width = 40
        chars = "=" * int(width * percent)
        chars = chars[:width] 
        info = self._info[:38]
        line = "|%-2d%%%-37s| %s" % (int(percent*100), chars, info)
        line = line[:80]
        print "%-80s\r" % (line),
        
    def ObservableUpdate(self, obj, arg):
        if isinstance(obj, ProgressHandler):
            if arg == 'maxProgress':
                self._maxProgress = obj.GetMaxProgress()
            elif arg == 'currentProgress':
                self._curProgress = obj.GetCurrentProgress()
            elif arg == 'info':
                self._info = obj.GetInfo()
            elif arg == 'done':
                self._info = "done"
            elif arg == 'aborting':
                self._info = "aborting..."
            else:
                return
            self.__Output()

def main():
    parser = OptionParser(version="%s %s" % (Settings.APP_NAME, Settings.APP_VERSION))

    parser.add_option("-p", "--project", help=_(u"specifies the project file"), metavar="PROJECT")
    parser.add_option("-o", "--outputpath", help=_(u"the path where to save the output files"), metavar="PATH")
    parser.add_option("-f", "--format", help=_(u"one of: VCD, SVCD, DVD, Medium, HD, FULL-HD") + " [default: %default]", metavar="FORMAT", default="HD")
    parser.add_option("-n", "--videonorm", help="n=NTSC, p=PAL [default: %default]", metavar="VIDEONORM", default="p")
    parser.add_option("-r", "--renderer", help=_(u"0=Single pictures, 1=Shellscript, 2=MPEG-Video (fast), 3=MPEG-Video (HQ)") + " [default: %default]", metavar="RENDERER", default=2, type="int")
    
    options, args = parser.parse_args()
    
    if options.project:
        options.project = os.path.abspath(options.project)
        if not os.path.isfile(options.project):
            parser.error(_(u"projectfile does not exist: %s") % options.project)
    else:
        parser.error(_(u"no projectfile specified!"))
        sys.exit(1)
            
    if options.outputpath:
        options.outputpath = os.path.abspath(options.outputpath)
        if not os.path.exists(options.outputpath):
            try:
                os.makedirs(options.outputpath)
            except Exception, err:
                parser.error(_(u"cannot create outputpath: %s") % err)
    else:
        parser.error(_(u"no outputpath specified!"))
        sys.exit(2)
    

    formatDict = {"vcd": [(352, 288), (352, 240), 1150],
                  "svcd": [(576, 480), (480, 480), 2500],
                  "dvd": [(720, 576), (720, 480), 8000],
                  "medium": [(640, 360), (640, 360), 8000],
                  "hd": [(1280, 720), (1280, 720), 8000],
                  "full-hd": [(1920, 1080), (1920, 1080), 8000]}
    

    if options.videonorm == "p":
        frameRate = 25.0
    elif options.videonorm == "n":
        frameRate = 30.0
    else:
        parser.error(_(u"invalid videonorm specified: %s") % options.videonorm)
        sys.exit(3)

    
    if not formatDict.has_key(options.format.lower()):
        parser.error(_(u"invalid format specified: %s") % options.format)
        sys.exit(4)

    resolution = formatDict[options.format.lower()][0 if options.videonorm == "p" else 1]
    bitrate = formatDict[options.format.lower()][2]

    rendererName = ""
    if options.renderer == 0:
        renderer = SingleFileRenderer()
        rendererName = _(u"Single pictures")
    elif options.renderer == 1:
        renderer = ShellScriptRenderer()
        rendererName = _(u"Single pictures (shellscript)")
    elif options.renderer == 2:
        renderer = MovieRenderer()
        renderer.SetBitrate(bitrate)
        renderer.SetUseResample(False)
        rendererName = _(u"MPEG-Video (fast)")
    elif options.renderer == 3:
        renderer = MovieRenderer()
        renderer.SetBitrate(bitrate)
        renderer.SetUseResample(True)
    
        renderer.SetFrameRate(frameRate)
        renderer.SetResolution(resolution)
        rendererName = _(u"MPEG-Video (HQ; slow)")
    else:
        parser.error(_(u"invalid renderer specified: %s") % options.renderer)
        
    cliGui = CliGui()
    progressHandler = ProgressHandler()
    progressHandler.AddObserver(cliGui)
    
    renderer.SetProgressHandler(progressHandler)
    photoFilmStrip = PhotoFilmStrip()
    photoFilmStrip.Load(options.project) 

    print Settings.APP_NAME, Settings.APP_VERSION
    print u"(C) 2008 Jens G\xf6pfert"
    print "http://photostoryx.sourceforge.net"
    print 
    print "%-20s: %s" % (_(u"processing project"), options.project)
    print "%-20s: %s" % (_(u"using renderer"), rendererName)
    print "%-20s: %s (%dx%d)" % (_(u"output format"), options.format, resolution[0], resolution[1])
    print "%-20s: %1.f (%s):" % (_(u"framerate"), frameRate, "PAL" if options.videonorm == "p" else "NTSC") 
    print
    
    try:
        photoFilmStrip.Render(renderer, options.outputpath)
    except KeyboardInterrupt:
        progressHandler.Abort()
        print
        print
        print _(u"...aborted!")
        sys.exit(5)
        
    print
    print
    print _(u"all done")
