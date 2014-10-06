# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2011 Jens Goepfert
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

import logging
import os

try:
    import numpy
    import cv2
except ImportError:
    numpy = None
    cv2 = None

from photofilmstrip.core.OutputProfile import OutputProfile
from photofilmstrip.core.BaseRenderer import BaseRenderer


class OpenCvRenderer(BaseRenderer):
    
    def __init__(self):
        BaseRenderer.__init__(self)
        
        self._encOut = None
        self._encErr = None
        
        self._videoWriter = None
        
    @staticmethod
    def GetName():
        return "AVI (XVid)"
    
    @staticmethod
    def CheckDependencies(msgList):
        try:
            import numpy
            import cv2
        except ImportError, err:
            logging.debug("checking for open-cv failed: %s", err)
            output = ""
            msgList.append(_(u"Open-CV (python-opencv) required!"))

    @staticmethod
    def GetProperties():
        return []

    @staticmethod
    def GetDefaultProperty(prop):
        return BaseRenderer.GetDefaultProperty(prop)

    def ProcessFinalize(self, pilImg):
        open_cv_image = numpy.array(pilImg)
        # Convert RGB to BGR
        open_cv_image = open_cv_image[:, :, ::-1].copy() 

        self._videoWriter.write(open_cv_image)
    
    def __CleanUp(self):
        if self._videoWriter is None:
            return
        
        self._videoWriter.release()
        self._videoWriter = None
        
    def ProcessAbort(self):
        self.__CleanUp()

    def Prepare(self):
        profile = self.GetProfile()
        fourcc = cv2.cv.FOURCC(*"XVID")
        
        self._videoWriter = cv2.VideoWriter(os.path.join(self.GetOutputPath(), "output.avi"), 
                                            fourcc, 
                                            self._GetFrameRate(), 
                                            profile.GetResolution())

    def GetSink(self):
        return self._videoWriter
    
    def Finalize(self):
        self.__CleanUp()
        
    def _GetFrameRate(self):
        if self.GetProfile().GetVideoNorm() == OutputProfile.PAL:
            framerate = 25.0
        else:
            framerate = 30.0
        return framerate
