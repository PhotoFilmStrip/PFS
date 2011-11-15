# encoding: UTF-8

import logging
import threading

from photofilmstrip.lib.jobimpl.VisualJob import VisualJob
from photofilmstrip.lib.jobimpl.Worker import JobAbortedException


class RenderJobContext(VisualJob):
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

        self.__logger = logging.getLogger("RenderJobContext<%s>" % name)

    def FetchImage(self, backend, pic):
        if not self.imgCache.has_key(pic.GetFilename()):
#            self._GetLogger().debug("%s: GetImage(%s)", self.name, pic.GetFilename())
            if len(self.imgKeyStack) > 2:
                key = self.imgKeyStack.pop(0)
#                self._GetLogger().debug("%s: Pop cache (%s)", self.name, key)
                self.imgCache[key] = None
                                
            # TODO: gleiches bild mit unterschiedlicher rotation
            self.imgCache[pic.GetFilename()] = backend.CreateCtx(pic)
            self.imgKeyStack.append(pic.GetFilename())
        return self.imgCache[pic.GetFilename()]
        

    def Done(self):
        if self.IsAborted():
            self.renderer.ProcessAbort()
            self.SetInfo(_(u"...aborted!"))
        else:
            self.SetInfo(_(u"all done"))
        self.renderer.Finalize()

    def Begin(self):
        # prepare task queue
        self.__logger.debug("prepare task queue")
        for idx, task in enumerate(self.tasks):
            task.SetIdx(idx)
            self.AddWorkLoad(task)

        # prepare the renderer, creates the sink pipe 
        self.renderer.Prepare()
        self.sink = self.renderer.GetSink()

    def Abort(self):
        if VisualJob.Abort(self):
            self.SetInfo(_(u"aborting..."))

    def ToSink(self, pilCtx):
        pilCtx.ToStream(self.sink, "JPEG")


    def GetWorkLoad(self, block, timeout):
        task = VisualJob.GetWorkLoad(self, block, timeout)
        self.SetInfo(task.GetInfo())

        self.__logger.debug("%s - start", task)
        
        return task
        
    def PushResult(self, resultObject):
        task = resultObject.GetSource()
        self.__logger.debug("%s - done", task)
        try:
            self.results[task.idx] = resultObject.GetResult()
        except JobAbortedException:
            pass
        self.StepProgress()

        with self.resultToFetchLock:
            while self.results.has_key(self.resultToFetch):
                idx = self.resultToFetch
                
                self.__logger.debug("resultToFetch: %s",
                                    idx)
                
                pilCtx = self.results[idx]
                if pilCtx:
                    self.ToSink(pilCtx)
                del self.results[idx]
                self.resultToFetch += 1
