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

import traceback, StringIO
import logging
import multiprocessing
from multiprocessing.queues import Queue, Full, Empty

from photofilmstrip.core.renderer.RendererException import RendererException
from photofilmstrip.core.Subtitle import SubtitleSrt

from photofilmstrip.core.backend.PILBackend import PILBackend
#from photofilmstrip.core.backend.CairoBackend import CairoBackend

BACKEND = PILBackend()
#BACKEND = CairoBackend()


class RenderEngine(object):
    
    def __init__(self, aRenderer, progressHandler, draftMode):
        self.__aRenderer = aRenderer
        self.__profile = aRenderer.GetProfile()
        self.__progressHandler = progressHandler
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

    def __CheckAbort(self):
        if self.__progressHandler.IsAborted():
            self.__aRenderer.ProcessAbort()
            return True
        return False
    
    def __TransAndFinal(self, infoText, trans, 
                        picFrom, picTo, 
                        pathRectsFrom, pathRectsTo):
        if len(pathRectsFrom) != len(pathRectsTo):
            raise RuntimeError()
        
        count = len(pathRectsFrom)
        for idx in range(count):
            task = TaskTrans(BACKEND, 
                             trans, idx / float(count),
                             picFrom.Copy(), pathRectsFrom[idx], 
                             picTo.Copy(), pathRectsTo[idx], 
                             self.__profile.GetResolution())
            task.SetInfo(infoText)
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

#            img = self.__aRenderer.CreateCtx(pic) # TODO:
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
                task = TaskCropResize(BACKEND,
                                      pic.Copy(), rect, 
                                      self.__profile.GetResolution())
                task.SetInfo(infoText)
                self.__tasks.append(task)
            
            picBefore = pic
            pathRectsBefore = pathRects
            transCountBefore = transCount

    def __HasComments(self, pics):
        for pic in pics:
            if pic.GetComment():
                return True
        return False
    
    def __Process(self):
        self.__progressHandler.SetInfo(_(u"initialize renderer"))
        self.__aRenderer.Prepare()
        BACKEND.EnableDraftMode(self.__draftMode)

        self.__progressHandler.SetInfo(_(u"creating output..."))
        
        taskQueue = Queue()
        cpuCount = multiprocessing.cpu_count()
        doneQueue = Queue(cpuCount * 3)

        # prepare task queue
        idx = 0
        for idx, task in enumerate(self.__tasks):
            task.SetIdx(idx)
            taskQueue.put(task, False)
            
        # prepare workers
        workers = []
        for num in range(cpuCount):
            tw = TaskWorker("TaskWorker_%d" % num,
                            taskQueue,
                            doneQueue)
            workers.append(tw)
            tw.start()
            
        resultBuffer = {}
        curResult = 0
        while not self.__progressHandler.IsAborted() and curResult <= idx:
            result = None
            try:
#                if not self.__aRenderer.EnsureFramerate():
#                    taskQueue.get(True, 1.0)
                
                result = doneQueue.get(True, 1.0)
            except Empty:
                print "doneQueue empty"
                
            if result is not None:
                resIdx, resCtx = result
                resultBuffer[resIdx] = resCtx
            
            while resultBuffer.has_key(curResult):
                resCtx = resultBuffer[curResult]
                resCtx.Unserialize(None)
                self.__aRenderer.ProcessFinalize(resCtx)
                
                del resultBuffer[curResult]
                curResult += 1
                self.__progressHandler.Step()
                
        # empty all queues, so that workers will finish their main loop
        while 1:
            logging.debug("emptying task queue")
            try:
                taskQueue.get(True, 0.05)
            except Empty:
                logging.debug("task queue empty")
                break
        while 1:
            logging.debug("emptying result queue")
            try:
                doneQueue.get(True, 0.05)
            except Empty:
                logging.debug("result queue empty")
                break
            
        # wait for workers to terminate
        for tw in workers:
            logging.debug("joining worker: %s", tw)
            tw.join(3.0)
            if tw.is_alive():
                logging.debug("killing worker: %s", tw)
                tw.terminate()
            
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
        self.__PrepareTasks(pics)
        count = len(self.__tasks)
        generateSubtitle = self.__HasComments(pics)
        if generateSubtitle:
            count += 1

        self.__progressHandler.SetMaxProgress(int(count))
        
        try:
            if generateSubtitle:
                self.__progressHandler.SetInfo(_(u"generating subtitle"))
                st = SubtitleSrt(self.__aRenderer.POutputPath, self.__picCountFactor)
                st.Start(pics)
                self.__progressHandler.Step()
            
            self.__Process()
            return True
        except RendererException, err:
            self.__errorCls = err.__class__
            self.__errorMsg = err.GetMessage()
        except StandardError, err:
            self.__errorCls = err.__class__
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

    def GetErrorClass(self):
        return self.__errorCls


class TaskWorker(multiprocessing.Process):
#class TaskWorker(threading.Thread):
    
    def __init__(self, name, taskQueue, doneQueue):
        multiprocessing.Process.__init__(self, name=name)#, verbose=1)
#        threading.Thread.__init__(self, name=name)#, verbose=1)
        self.taskQueue = taskQueue
        self.doneQueue = doneQueue
        self.imgCache = {}
        self.imgKeyStack = []
        
    def FetchImage(self, pic):
        if not self.imgCache.has_key(pic.GetFilename()):
            logging.debug("%s: GetImage(%s)", self.name, pic.GetFilename())
            if len(self.imgKeyStack) > 1:
                key = self.imgKeyStack.pop(0)
                logging.debug("%s: Pop cache (%s)", self.name, key)
                self.imgCache[key] = None
                                
            # TODO: gleiches bild mit unterschiedlicher rotation
            self.imgCache[pic.GetFilename()] = BACKEND.CreateCtx(pic)
            self.imgKeyStack.append(pic.GetFilename())
        return self.imgCache[pic.GetFilename()]
        
    def run(self):
        logging.debug("%s: worker started", self.name)
        
#        import hotshot, hotshot.stats
#        prof = hotshot.Profile("pfs_%s.prof" % self.name)
#        prof.runcall(self._run)
#        prof.close()
#        
#    def _run(self):
        while 1:
            logging.debug("%s: task queue size %s", self.name, self.taskQueue.qsize())
            
            task = None
            try:
                task = self.taskQueue.get(True, 0.1)
            except Empty:
                logging.debug("%s: task queue empty", self.name)
                break
            
            logging.debug("%s: %s - start", self.name, task.GetIdx())
            result = task.Run(self)
            logging.debug("%s: %s - done", self.name, task.GetIdx())
            
            result.Serialize()
            
            while 1:
                logging.debug("%s: queuing result: %s", self.name, task.GetIdx())
                try:
                    self.doneQueue.put((task.GetIdx(), result), True, 1.0)
                    break
                except Full:
                    logging.debug("%s: result queue full", self.name)
            logging.debug("%s: result queued: %s", self.name, task.GetIdx())
        
        logging.debug("%s: joining done queue", self.name)
        self.doneQueue.close()
        self.doneQueue.join_thread()
        
        logging.debug("%s: worker finished", self.name)


class Task(object):
    def __init__(self, backend, resolution):
        self.backend = backend
        self.resolution = resolution
        self.idx = None
        self.info = ""
        
    def GetInfo(self):
        return self.info
    def SetInfo(self, info):
        self.info = info
        
    def GetIdx(self):
        return self.idx
    def SetIdx(self, idx):
        self.idx = idx
        
    def Run(self, procCtx):
        try:
            img = self._Run(procCtx)
        except Exception:
            img = None
            traceback.print_exc()
        return img
            
    def _Run(self, procCtx):
        raise NotImplementedError()


class TaskCropResize(Task):
    def __init__(self, backend, picture, rect, resolution):
        Task.__init__(self, backend, resolution)
        self.picture = picture
        self.rect = rect
        
    def _Run(self, procCtx):
        image = procCtx.FetchImage(self.picture)
        img = self.backend.CropAndResize(image,
                                         self.rect,
                                         self.resolution)
        return img
    

class TaskTrans(Task):
    def __init__(self, backend, kind, percentage,
                 pic1, rect1, pic2, rect2, resolution):
        Task.__init__(self, backend, resolution)
        self.kind = kind
        self.percentage = percentage
        self.taskPic1 = TaskCropResize(backend, pic1, rect1, resolution)
        self.taskPic2 = TaskCropResize(backend, pic2, rect2, resolution)
        
    def _Run(self, procCtx):
        image1 = self.taskPic1.Run(procCtx)
        image2 = self.taskPic2.Run(procCtx)
        
        img = self.backend.Transition(self.kind, 
                                      image1, image2, 
                                      self.percentage)
        
        return img
