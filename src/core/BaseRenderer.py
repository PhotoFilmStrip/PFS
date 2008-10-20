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

import os, logging

import wx


class BaseRenderer(object):
    
    def __init__(self):
        self._frameRate = 25.0
        self._resolution = (1280, 720)
        self._transDuration = 1.0
        self._outputPath = None
        
        self.__progressHandler = None
        
    def SetProgressHandler(self, progressHandler):
        self.__progressHandler = progressHandler
        
    def GetOutputPath(self):
        return self._outputPath
        
    def GetFrameRate(self):
        return self._frameRate
    def SetFrameRate(self, fr):
        self._frameRate = fr
        
    def GetResolution(self):
        return self._resolution
    def SetResolution(self, res):
        self._resolution = res
        
    def GetTransitionDuration(self):
        return self._transDuration
    def SetTransitionDuration(self, tr):
        self._transDuration = tr
    
    def __ComputePath(self, pic):
        px1, py1 = pic.GetStartRect().GetPosition().Get()
        w1, h1 = pic.GetStartRect().GetSize().Get()
        
        px2, py2 = pic.GetTargetRect().GetPosition().Get()
        w2, h2 = pic.GetTargetRect().GetSize().Get()
        
        cx1 = (w1 / 2.0) + px1
        cy1 = (h1 / 2.0) + py1

        cx2 = (w2 / 2.0) + px2
        cy2 = (h2 / 2.0) + py2
        
        pics = (pic.GetDuration() + self.GetTransitionDuration()) * self.GetFrameRate()
        
        dx = (cx2 - cx1) / pics
        dy = (cy2 - cy1) / pics
        dw = (w2 - w1) / pics
        dh = (h2 - h1) / pics
        
        pathRects = []
        for step in xrange(int(pics) + 1):
            px = cx1 + step * dx
            py = cy1 + step * dy
            width = w1 + step * dw
            height = h1 + step * dh
            
            rect = wx.Rect(px - width / 2.0, 
                           py - height / 2.0, 
                           width, 
                           height)
            
            pathRects.append(rect)
        return pathRects

    def __Start(self, pics, outputPath):
        self._outputPath = outputPath
        self.__progressHandler.SetInfo(_(u"initialize renderer"))
        self.Prepare()
        
        TRANS_COUNT = int(self.GetTransitionDuration() * self.GetFrameRate())

        filesBefore = None
        filesCurrent = None
        
        for pic in pics:
            infoText = _(u"processing image '%s'") % os.path.basename(pic.GetFilename())
            self.__progressHandler.SetInfo(infoText)

            self.__progressHandler.SetInfo(u"%s - %s" % (infoText, _(u"prepare")))
            preparedResult = self.ProcessPrepare(pic.GetFilename(),
                                                 pic.GetRotation(),
                                                 pic.GetEffect())

            filesCurrent = []
            pathRects = self.__ComputePath(pic)
            for idxRect, rect in enumerate(pathRects):
                if self.__progressHandler.IsAborted():
                    self.__progressHandler.Done()
                    return

                self.__progressHandler.Step()
                
                self.__progressHandler.SetInfo(u"%s - %s (%d/%d)" % (infoText, 
                                                                     _(u"crop and resize"),
                                                                     idxRect,
                                                                     len(pathRects)))
                filename = self.ProcessCropAndResize(preparedResult,
                                                     rect, 
                                                     self.GetResolution())
                
                if not isinstance(filename, basestring):
                    raise RuntimeError("ProcessCropAndResize must return a filename")
                
                filesCurrent.append(filename)
                
            if filesBefore is None:
                filesBefore = filesCurrent
            else:
                filesTransFrom = filesBefore[-TRANS_COUNT:]
                del filesBefore[-TRANS_COUNT:]
                filesTransTo = filesCurrent[:TRANS_COUNT]
                del filesCurrent[:TRANS_COUNT]
                
                for filename in filesBefore:
                    self.__progressHandler.SetInfo(u"finalizing '%s'" % (os.path.basename(filename)))
                    self.ProcessFinalize(filename)
                
                self.__progressHandler.SetInfo(_(u"calculating transition"))
                files = self.ProcessTransition(filesTransFrom, filesTransTo)
                
                for filename in files:
                    self.__progressHandler.SetInfo(u"finalizing '%s'" % (os.path.basename(filename)))
                    self.ProcessFinalize(filename)

                filesBefore = filesCurrent
        
        for filename in filesCurrent:
            self.__progressHandler.SetInfo(u"finalizing '%s'" % (os.path.basename(filename)))
            self.ProcessFinalize(filename)
                    
        self.__progressHandler.SetInfo(_(u"creating output..."))
        self.Finalize()
        
    def Start(self, pics, outputPath):
        count = 0
        for pic in pics:
            count += pic.GetDuration() * self.GetFrameRate()
        self.__progressHandler.SetMaxProgress(int(count))
        
        try:
            self.__Start(pics, outputPath)
        except Exception, err:
            logging.error(str(err))
        
        self.__progressHandler.Done()
                    
    def CheckDependencies(self):
        raise NotImplementedError
    
    def Prepare(self):
        raise NotImplementedError()        
    
    def ProcessPrepare(self, filename, rotation, effect):
        raise NotImplementedError()
    
    def ProcessCropAndResize(self, preparedResult, cropRect, size):
        raise NotImplementedError()
        
    def ProcessTransition(self, fileListFrom, fileListTo):
        raise NotImplementedError()
    
    def ProcessFinalize(self, filename):
        raise NotImplementedError()
    
    def Finalize(self):
        raise NotImplementedError()
    
    