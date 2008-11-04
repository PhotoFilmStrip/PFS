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

import os

from core.BaseRenderer import BaseRenderer
from core.Picture import Picture


class ShellScriptRenderer(BaseRenderer):
    
    def __init__(self):
        BaseRenderer.__init__(self)
        self._counter = 0
        self._commands = []
    
    @staticmethod
    def CheckDependencies():
        pass
    
    @staticmethod
    def GetName():
        return _(u"Single pictures (shellscript)")
    
    @staticmethod
    def GetProperties():
        return ["ResampleFilter"]

    @staticmethod
    def GetDefaultProperty(prop):
        if prop == "ResampleFilter":
            return "Sinc"
        return BaseRenderer.GetDefaultProperty(prop)

    def Prepare(self):
        pass
    
    def ProcessPrepare(self, filename, rotation, effect):
        arg = "\"%s\" -depth 8 -rotate %d" % (filename, rotation * 90)
        if effect == Picture.EFFECT_BLACK_WHITE:
            arg += ""
        if effect == Picture.EFFECT_SEPIA:
            arg += " -sepia-tone 80% "
        return arg
    
    def ProcessCropAndResize(self, preparedResult, cropRect, size):
        self._counter += 1
        
        newFilename = os.path.join(self.GetOutputPath(), '%09d.pnm' % (self._counter))
        cmd = "convert %s -crop %dx%d+%d+%d " \
              "-filter %s -resize %dx%d! " \
              "\"%s\"" % (preparedResult,
                          cropRect[2], cropRect[3], cropRect[0], cropRect[1],
                          ShellScriptRenderer.GetProperty("ResampleFilter"),
                          size[0], size[1], newFilename)

        self._commands.append(cmd)
        
        return newFilename

    def ProcessTransition(self, fileListFrom, fileListTo):
        files = []
        count = len(fileListFrom)
        for idx in range(count):
            f1 = fileListFrom[idx]
            f2 = fileListTo[idx]
            
            cmd = "composite \"%s\" \"%s\" -depth 8 -quality 100 -dissolve %d \"%s\"" % (f2, f1, (100 / count) * idx, f1)
            self._commands.append(cmd)
            self._commands.append("rm \"%s\"" % f2)

            files.append(f1)
        return files
    
    def ProcessFinalize(self, filename):
        pass
    
    def Finalize(self):
        filename = "%s%sphotostrip.sh" % (self.GetOutputPath(), os.sep)
        fd = open(filename, 'w')
        fd.write("#!/bin/sh")
        fd.write("\n\n")
        for line in self._commands:
            fd.write(line)
            fd.write("\n")
        fd.close()

    def ProcessAbort(self):
        pass
