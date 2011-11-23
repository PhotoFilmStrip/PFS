# encoding: UTF-8

import logging
import threading

from photofilmstrip.lib.jobimpl.VisualJob import VisualJob
from photofilmstrip.lib.jobimpl.Worker import JobAbortedException


class RenderJob(VisualJob):
    def __init__(self, name, renderer, tasks):
        VisualJob.__init__(self, name, groupId="render")
        self.renderer = renderer
        self.tasks = tasks

        self.SetMaxProgress(len(tasks))
        
        self.imgCache = {}
        self.imgKeyStack = []

        self.resultToFetchLock = threading.Lock()
        self.resultToFetch = 0
        self.sink = None
        
        self.results = {}

        self.__logger = logging.getLogger("RenderJob")
        
    def GetOutputPath(self):
        return self.renderer.GetOutputPath()

    def FetchImage(self, pic):
        if not self.imgCache.has_key(pic.GetKey()):
            self.__logger.debug("%s: GetImage(%s)", self.GetName(), pic.GetFilename())
            if len(self.imgKeyStack) > 3:
                key = self.imgKeyStack.pop(0)
                self.__logger.debug("%s: Pop cache (%s)", self.GetName(), key)
                self.imgCache[key] = None
                                
            self.imgCache[pic.GetKey()] = pic.GetImage()
            self.imgKeyStack.append(pic.GetKey())
        return self.imgCache[pic.GetKey()]
        

    def Done(self):
        if self.IsAborted():
            self.renderer.ProcessAbort()
            self.SetInfo(_(u"...aborted!"))
        else:
            self.SetInfo(_(u"all done"))
        self.renderer.Finalize()

    def Begin(self):
        # prepare task queue
        self.__logger.debug("%s: prepare task queue", self.GetName())
        for idx, task in enumerate(self.tasks):
            task.SetIdx(idx)
            self.AddWorkLoad(task)

        # prepare the renderer, creates the sink pipe 
        self.renderer.Prepare()
#        self.sink = self.renderer.GetSink()

    def Abort(self):
        if VisualJob.Abort(self):
            self.SetInfo(_(u"aborting..."))

    def ToSink(self, pilImg):
        self.renderer.ProcessFinalize(pilImg)


    def GetWorkLoad(self, block, timeout):
        task = VisualJob.GetWorkLoad(self, block, timeout)
        self.SetInfo(task.GetInfo())

        self.__logger.debug("%s: %s - start", self.GetName(), task)
        
        return task
        
    def PushResult(self, resultObject):
        task = resultObject.GetSource()
        self.__logger.debug("%s: %s - done", self.GetName(), task)
        try:
            self.results[task.idx] = resultObject.GetResult()
        except JobAbortedException:
            pass
        self.StepProgress()

        with self.resultToFetchLock:
            while self.results.has_key(self.resultToFetch):
                idx = self.resultToFetch
                
                self.__logger.debug("%s: resultToFetch: %s",
                                    self.GetName(), idx)
                
                pilCtx = self.results[idx]
                if pilCtx:
                    self.ToSink(pilCtx)
                del self.results[idx]
                self.resultToFetch += 1
