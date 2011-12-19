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

from photofilmstrip.core.tasks import TaskCropResize, TaskTrans, TaskSubtitle
from photofilmstrip.lib.jobimpl.JobManager import JobManager
from photofilmstrip.core.RenderJob import RenderJob


class RenderEngine(object):
    
    def __init__(self, name, aRenderer, draftMode):
        self.__name = name
        self.__aRenderer = aRenderer
        self.__profile = aRenderer.GetProfile()
        self.__errorMsg = None
        self.__errorCls = None
        self.__tasks = []
        self.__draftMode = draftMode

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

    def __TransAndFinal(self, infoText, trans, 
                        picFrom, picTo, 
                        pathRectsFrom, pathRectsTo):
        if len(pathRectsFrom) != len(pathRectsTo):
            raise RuntimeError()
        
        count = len(pathRectsFrom)
        for idx in range(count):
            task = TaskTrans(trans, idx / float(count),
                             picFrom.Copy(), pathRectsFrom[idx], 
                             picTo.Copy(), pathRectsTo[idx], 
                             self.__profile.GetResolution())
            task.SetInfo(infoText)
            task.SetDraft(self.__draftMode)
            self.__tasks.append(task)
        
        return True

    def __PrepareTasks(self, pics):
        pathRectsBefore = None
        picBefore = None
        transCountBefore = 0
        
        for idxPic, pic in enumerate(pics):
            picCount = self.__GetPicCount(pic)
            transCount = 0
            if idxPic < (len(pics) - 1):
                # last pic has no transition
                transCount = self.__GetTransCount(pic)

            pathRects = self.__ComputePath(pic, picCount + transCount + transCountBefore)

            if idxPic > 0 and idxPic < len(pics):
                # first and last pic has no transition
                infoText = _(u"processing transition %d/%d") % (idxPic + 1, len(pics))
                
                if transCountBefore > 0:
                    phase2a = pathRectsBefore[-transCountBefore:]
                    phase2b = pathRects[:transCountBefore]
                    if not self.__TransAndFinal(infoText,
                                                pics[idxPic-1].GetTransition(),
                                                picBefore, pic, 
                                                phase2a, phase2b):
                        break
                
            infoText = _(u"processing image %d/%d") % (idxPic + 1, len(pics))

            if transCount > 0:
                # transition needs pictures, subtract them from movement
                _pathRects = pathRects[transCountBefore:-transCount]
            else:
                # transition needs no pictures, use them all for movement
                _pathRects = pathRects[transCountBefore:]
                
            for rect in _pathRects:
                task = TaskCropResize(pic.Copy(), rect, 
                                      self.__profile.GetResolution())
                task.SetInfo(infoText)
                task.SetDraft(self.__draftMode)
                self.__tasks.append(task)
            
            picBefore = pic
            pathRectsBefore = pathRects
            transCountBefore = transCount

    def CreateRenderJob(self, pics, targetLengthSecs=None):
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
        self.__PrepareTasks(pics)
        
        taskSub = TaskSubtitle(self.__aRenderer.GetOutputPath(),
                               self.__picCountFactor,
                               pics)
        self.__tasks.insert(0, taskSub)
                
        rjc = RenderJob(self.__name, self.__aRenderer, self.__tasks)
        return rjc
