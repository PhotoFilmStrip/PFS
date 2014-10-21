# encoding: UTF-8

import logging
import threading

from photofilmstrip.lib.jobimpl.VisualJob import VisualJob
from photofilmstrip.lib.jobimpl.Worker import JobAbortedException
from photofilmstrip.core import PILBackend


class RenderJob(VisualJob):
    def __init__(self, name, renderer, tasks):
        VisualJob.__init__(self, name, groupId="render")
        self.renderer = renderer
        self.tasks = tasks

        self.SetMaxProgress(len(tasks))
        
        self.imgCacheLock = threading.Lock()
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
        with self.imgCacheLock:
            if not self.imgCache.has_key(pic.GetKey()):
                self.__logger.debug("%s: GetImage(%s)", self.GetName(), pic.GetFilename())
                if len(self.imgKeyStack) > 2:
                    key = self.imgKeyStack.pop(0)
                    self.__logger.debug("%s: Pop cache (%s)", self.GetName(), key)
                    del self.imgCache[key]
                                    
                self.imgCache[pic.GetKey()] = PILBackend.GetImage(pic)
                self.imgKeyStack.append(pic.GetKey())
            return self.imgCache[pic.GetKey()]

    def Done(self):
        if self.IsAborted():
            self.renderer.ProcessAbort()
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

    def ToSink(self, pilImg):
        self.renderer.ProcessFinalize(pilImg)


    def GetWorkLoad(self):
        task = VisualJob.GetWorkLoad(self)
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
