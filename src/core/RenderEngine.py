# encoding: UTF-8
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

import traceback, StringIO

import Image

from core.Subtitle import SubtitleSrt
from core.Picture import Picture


class RenderEngine(object):
    
    def __init__(self, aRenderer, progressHandler):
        self.__aRenderer = aRenderer
        self.__profile = aRenderer.GetProfile()
        self.__progressHandler = progressHandler
        self.__errorMsg = None

        self.__picCountFactor = 1.0
        
    def __ComputePath(self, pic, picCount):
        px1, py1 = pic.GetStartRect()[:2]
        w1, h1 = pic.GetStartRect()[2:]
        
        px2, py2 = pic.GetTargetRect()[:2]
        w2, h2 = pic.GetTargetRect()[2:]
        
        cx1 = (w1 / 2.0) + px1
        cy1 = (h1 / 2.0) + py1

        cx2 = (w2 / 2.0) + px2
        cy2 = (h2 / 2.0) + py2
        
        dx = (cx2 - cx1) / float(picCount - 1)
        dy = (cy2 - cy1) / float(picCount - 1)
        dw = (w2 - w1) / float(picCount - 1)
        dh = (h2 - h1) / float(picCount - 1)
        
        pathRects = []
        for step in xrange(picCount):
            px = cx1 + step * dx
            py = cy1 + step * dy
            width = w1 + step * dw
            height = h1 + step * dh
            
            rect = (px - width / 2.0, 
                    py - height / 2.0, 
                    width, 
                    height)
            
            pathRects.append(rect)
        return pathRects
    
    def __GetPicCount(self, pic):
        """
        returns the number of pictures
        """
#                         self.__profile.GetFramerate() * \
        return int(round(pic.GetDuration() * \
                         25.0 * \
                         self.__picCountFactor))
    
    def __GetTransCount(self, pic):
        """
        returns the number of pictures needed for the transition
        """
#                         self.__profile.GetFramerate() * \
        return int(round(pic.GetTransitionDuration() * \
                         25.0 * \
                         self.__picCountFactor))

    def __CheckAbort(self):
        if self.__progressHandler.IsAborted():
            self.__aRenderer.ProcessAbort()
            return True
        return False
    
    def __ProcAndFinal(self, image, pathRects):
        for rect in pathRects:
            if self.__CheckAbort():
                return False
            
            self.__progressHandler.Step()
            img = self.__aRenderer.ProcessCropAndResize(image,
                                                        rect, 
                                                        self.__profile.GetResolution())
            self.__aRenderer.ProcessFinalize(img)
        return True

    def __TransAndFinal(self, trans, imgFrom, imgTo, pathRectsFrom, pathRectsTo):
        if len(pathRectsFrom) != len(pathRectsTo):
            raise RuntimeError
        
        COUNT = len(pathRectsFrom)
        
        for idx in range(COUNT):
            if self.__CheckAbort():
                return False
        
            self.__progressHandler.Step()
            image1 = self.__aRenderer.ProcessCropAndResize(imgFrom,
                                                           pathRectsFrom[idx], 
                                                           self.__profile.GetResolution())

            image2 = self.__aRenderer.ProcessCropAndResize(imgTo,
                                                           pathRectsTo[idx], 
                                                           self.__profile.GetResolution())

            if trans == Picture.TRANS_FADE:
                img = Image.blend(image1, image2, idx / float(COUNT))
            elif trans == Picture.TRANS_ROLL:
                img = self.roll(image1, image2, idx / float(COUNT))
            
            self.__aRenderer.ProcessFinalize(img)
        
        return True

    def roll(self, img1, img2, proc):
        xsize, ysize = img1.size
        delta = int(xsize * proc)
        part1 = img2.crop((0, 0, delta, ysize))
        part2 = img1.crop((delta, 0, xsize, ysize))
        image = img2.copy()
        image.paste(part2, (0, 0, xsize-delta, ysize))
        image.paste(part1, (xsize-delta, 0, xsize, ysize))
        return image
    
    def __Start(self, pics):
        self.__progressHandler.SetInfo(_(u"initialize renderer"))
        self.__aRenderer.Prepare()
        
        pathRects = None
        img = None
        transCount = None
        
        pathRectsBefore = None
        imgBefore = None
        transCountBefore = 0
        
        for idxPic, pic in enumerate(pics):
            picCount = self.__GetPicCount(pic)
            transCount = 0
            if idxPic < (len(pics) - 1):
                transCount = self.__GetTransCount(pic)

            img = pic.GetImage()
            pathRects = self.__ComputePath(pic, picCount + transCount + transCountBefore)

            if idxPic > 0 and idxPic < len(pics):
                infoText = _(u"processing transition %d/%d") % (idxPic + 1, len(pics))
                self.__progressHandler.SetInfo(infoText)
                
                if transCountBefore > 0:
                    phase2a = pathRectsBefore[-transCountBefore:]
                    phase2b = pathRects[:transCountBefore]
                    if not self.__TransAndFinal(pics[idxPic-1].GetTransition(),
                                                imgBefore, img, 
                                                phase2a, phase2b):
                        return
                
            infoText = _(u"processing image %d/%d") % (idxPic + 1, len(pics))
            self.__progressHandler.SetInfo(infoText)

            if transCount > 0:
                if not self.__ProcAndFinal(img, pathRects[transCountBefore:-transCount]):
                    return
            else:
                if not self.__ProcAndFinal(img, pathRects[transCountBefore:]):
                    return
            
            imgBefore = img
            pathRectsBefore = pathRects
            transCountBefore = transCount

        self.__progressHandler.SetInfo(_(u"creating output..."))
        self.__aRenderer.Finalize()
        
    def Start(self, pics, targetLengthSecs=None):
        if targetLengthSecs is not None:
            # targetLength should be at least 1sec for each pic
            targetLengthSecs = max(targetLengthSecs, len(pics))
            totalSecs = 0
            for idxPic, pic in enumerate(pics):
                totalSecs += pic.GetDuration()
                if idxPic < (len(pics) - 1):
                    totalSecs += pic.GetTransitionDuration()
            self.__picCountFactor = targetLengthSecs / totalSecs
            
        # determine step count for progressbar
        count = 0
        generateSubtitle = False
        for idxPic, pic in enumerate(pics):
            count += round(self.__GetPicCount(pic))
            if idxPic < (len(pics) - 1):
                count += round(self.__GetTransCount(pic))
            
            if pic.GetComment() and not generateSubtitle:
                generateSubtitle = True
                count += 1

        self.__progressHandler.SetMaxProgress(int(count))
        
        try:
            if generateSubtitle:
                self.__progressHandler.SetInfo(_(u"generating subtitle"))
                st = SubtitleSrt(self.__aRenderer.POutputPath, self.__picCountFactor)
                st.Start(pics)
                self.__progressHandler.Step()
            
            self.__Start(pics)
            return True
        except StandardError, err:
            tb = StringIO.StringIO()
            traceback.print_exc(file=tb)
            self.__errorMsg = u"%s: %s\n%s" % (err.__class__.__name__, 
                                               unicode(err), 
                                               tb.getvalue())
            return False
        finally:
            self.__progressHandler.Done()

    def GetErrorMessage(self):
        return self.__errorMsg
