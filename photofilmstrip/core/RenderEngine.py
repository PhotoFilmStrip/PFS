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

import os
import re
import sys

from photofilmstrip.core.tasks import TaskCropResize, TaskTrans, TaskSubtitle
from photofilmstrip.core.RenderJob import RenderJob
from photofilmstrip.core.Picture import Picture


class RenderEngine(object):
    
    def __init__(self, name, aRenderer, draftMode):
        self._name = name
        self._aRenderer = aRenderer
        self._profile = aRenderer.GetProfile()
        self._tasks = []
        self._draftMode = draftMode

    def _PrepareTasks(self, pics):
        raise NotImplementedError()
        
    def CreateRenderJob(self, pics):
        # determine step count for progressbar
        self._tasks = []
        self._PrepareTasks(pics)
        
        rjc = RenderJob(self._name, self._aRenderer, self._tasks)
        return rjc


class RenderEngineSlideshow(RenderEngine):

    def __init__(self, name, aRenderer, draftMode, totalLength):
        RenderEngine.__init__(self, name, aRenderer, draftMode)
        self.__targetLengthSecs = totalLength
        self.__picCountFactor = None
        
    def __GetPicCountFactor(self, pics):
        if self.__targetLengthSecs is None:
            result = 1.0
        else:
            # targetLength should be at least 1sec for each pic
            targetLengthSecs = max(self.__targetLengthSecs, len(pics))
            totalSecs = 0
            for idxPic, pic in enumerate(pics):
                totalSecs += pic.GetDuration()
                if idxPic < (len(pics) - 1):
                    totalSecs += pic.GetTransitionDuration()
            result = targetLengthSecs / totalSecs
            
        return result

    def __GetPicCount(self, pic):
        """
        returns the number of pictures
        """
        if sys.platform == "win32":
            # FIXME: Hack for mencoder which is only used under win32
            fr = 25.0
        else:
            fr = self._profile.GetFramerate()
        return int(round(pic.GetDuration() * \
                         fr * \
                         self.__picCountFactor))
    
    def __GetTransCount(self, pic):
        """
        returns the number of pictures needed for the transition
        """
        if sys.platform == "win32":
            # FIXME: Hack for mencoder which is only used under win32
            fr = 25.0
        else:
            fr = self._profile.GetFramerate()
        return int(round(pic.GetTransitionDuration() * \
                         fr * \
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
                             self._profile.GetResolution())
            task.SetInfo(infoText)
            task.SetDraft(self._draftMode)
            self._tasks.append(task)
        
        return True

    def _PrepareTasks(self, pics):
        self.__picCountFactor = self.__GetPicCountFactor(pics)

        taskSub = TaskSubtitle(self._aRenderer.GetOutputPath(),
                               self.__picCountFactor,
                               pics)
        self._tasks.append(taskSub)

        pathRectsBefore = None
        picBefore = None
        transCountBefore = 0
        
        for idxPic, pic in enumerate(pics):
            picCount = self.__GetPicCount(pic)
            transCount = 0
            if idxPic < (len(pics) - 1):
                # last pic has no transition
                transCount = self.__GetTransCount(pic)

            cp = ComputePath(pic, picCount + transCount + transCountBefore)
            pathRects = cp.GetPathRects()

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
                                      self._profile.GetResolution())
                task.SetInfo(infoText)
                task.SetDraft(self._draftMode)
                self._tasks.append(task)
            
            picBefore = pic
            pathRectsBefore = pathRects
            transCountBefore = transCount


class RenderEngineTimelapse(RenderEngine):

    def _PrepareTasks(self, pics):
        picBefore = None
        getnum = re.compile(r"(.*?)(\d+)([.].*)")

        picNum = None
        numDigits = None

        for idxPic, pic in enumerate(pics):
            match = getnum.match(os.path.basename(pic.GetFilename()))
            picPrefix = match.groups()[0]
            picNum = int(match.groups()[1])
            picPostfix = match.groups()[2]
            numDigits = len(match.groups()[1])
            
            picDur = int(pic.GetDuration())
            transDur = int(pic.GetTransitionDuration())
            if idxPic < (len(pics) - 1):
                # get number from next pic
                match = getnum.match(os.path.basename(pics[idxPic + 1].GetFilename()))
                nextPicNum = int(match.groups()[1])

                picCount = nextPicNum - picNum + 1
            else:
                # last pic needs only one rect to add the final image
                picCount = 1

            cp = ComputePath(pic, (picDur * picCount) + (transDur * (picCount - 1)))
            pathRects = cp.GetPathRects()

            picDir = os.path.dirname(pic.GetFilename())
            idxRect = 0
            while idxRect < len(pathRects):
                picCopy = pic.Copy()
                picCopy._filename = os.path.join(picDir,
                                                 "{0}{1}{2}".format(picPrefix,
                                                                    ("%%0%dd" % numDigits) % picNum,
                                                                    picPostfix))

                if transDur > 0 and picBefore:
                    for idxTrans in range(transDur):
                        task = TaskTrans(pic.GetTransition(), (idxTrans+1) / float(transDur + 1),
                                         picBefore.Copy(), pathRects[idxRect],
                                         picCopy.Copy(), pathRects[idxRect],
                                         self._profile.GetResolution())
                        task.SetInfo(_(u"processing transition %d/%d") % (picNum, idxTrans+1))
                        task.SetDraft(self._draftMode)
                        self._tasks.append(task)
                        idxRect += 1

                for __ in range(picDur):
                    task = TaskCropResize(picCopy.Copy(), pathRects[idxRect],
                                          self._profile.GetResolution())
                    task.SetInfo(_(u"processing image %d/%d") % (picNum, __ + 1))
                    task.SetDraft(self._draftMode)
                    self._tasks.append(task)
                    idxRect += 1

                picNum += 1
                picBefore = picCopy

            picBefore = None


class ComputePath(object):

    def __init__(self, pic, picCount):
        px1, py1 = pic.GetStartRect()[:2]
        w1, h1 = pic.GetStartRect()[2:]

        px2, py2 = pic.GetTargetRect()[:2]
        w2, h2 = pic.GetTargetRect()[2:]

        cx1 = (w1 / 2.0) + px1
        cy1 = (h1 / 2.0) + py1

        cx2 = (w2 / 2.0) + px2
        cy2 = (h2 / 2.0) + py2
        
        if pic.GetMovement() == Picture.MOVE_LINEAR:
            clazz = LinearMovement
        elif pic.GetMovement() == Picture.MOVE_DELAYED:
            clazz = DelayedMovement
        else:
            clazz = AccelMovement
        mX = clazz(cx2 - cx1, picCount, cx1)
        mY = clazz(cy2 - cy1, picCount, cy1)
        mW = clazz(w2 - w1, picCount, w1)
        mH = clazz(h2 - h1, picCount, h1)

        pathRects = []
        for step in xrange(picCount):
            px = mX.Get(step)
            py = mY.Get(step)
            width = mW.Get(step)
            height = mH.Get(step)

            rect = (px - width / 2.0,
                    py - height / 2.0,
                    width,
                    height)

            pathRects.append(rect)
        self.pathRects = pathRects

    def GetPathRects(self):
        return self.pathRects


class LinearMovement(object):
    
    def __init__(self, s, t, s0):
        self._s = float(s)
        self._t = float(t)
        self._s0 = float(s0)
        
        if t > 1:
            self._v  = self._s / (self._t - 1)
        else:
            self._v = 0
        
    def Get(self, t):
        # s = v *t + s0
        t = float(t)
        return self._v * t + self._s0
        
        
class AccelMovement(object):
    
    def __init__(self, s, t, s0):
        self._s = float(s)
        self._t = float(t)
        self._s0 = float(s0)
        
        # gesucht: Polynom 3ten Grades
        # s = a*t^3 + b*t^2 + c*t + d
        # RB 1: f'(t) = 0
        # RB 2: f'(0) = 0 --> c = 0
        # RB 3: f''(t/2) = 0 --> b = -3 * a * t
        # RB 4: f(t) = s --> a = (s - b*t^2) / t^3
        
        self._a = -2.0 * self._s / (self._t**3)
        self._b = -3 * self._a * (self._t / 2.0) 
        self._c = 0
        self._d = float(s0)
        
    def Get(self, t):
        return self._a*t**3 + self._b*t**2 + self._c*t + self._d


class DelayedMovement(AccelMovement):

    def __init__(self, s, t, s0):
        AccelMovement.__init__(self, s, t / 2, s0)
        self._t4th = t / 4
        self._sAccel = None
        
    def Get(self, t):
        if t < self._t4th:
            self._sAccel = self._s0
        elif t < (self._t * 2) - self._t4th:
            self._sAccel = AccelMovement.Get(self, t - self._t4th)
        return self._sAccel
        
    