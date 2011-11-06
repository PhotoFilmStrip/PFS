# encoding: UTF-8

import Queue
import threading

from photofilmstrip.lib.jobimpl.IVisualJob import IVisualJob
from photofilmstrip.lib.jobimpl.IJobContext import IJobContext 
import logging


class RenderJobContext(IJobContext, IVisualJob):
    def __init__(self, name, renderer, tasks):
        self.name = name
        self.renderer = renderer
        self.tasks = tasks

#        self.SetMaxProgress(len(tasks))
        
        self.imgCache = {}
        self.imgKeyStack = []

        self.resultToFetchLock = threading.Lock()
        self.resultToFetch = 0
        self.sink = None
        
        self.results = {}

#        self.activeWorkers = activeWorkers
#        self.runFlag = runFlag
        self.taskQueue = Queue.Queue()
        self.__info = ""
        self.__isDone = False

        self.__logger = logging.getLogger("RenderJobContext")

    def GetMaxProgress(self):
        return len(self.tasks)
    
    def GetProgress(self):
        return self.resultToFetch
    
    def GetGroupId(self):
        return "render"
    
    def GetName(self):
        return self.name
    
    def GetInfo(self):
        return self.__info
    def SetInfo(self, value):
        self.__info = value

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
        

    def Finalize(self):
        self.renderer.Finalize()
        self.__isDone = True

    def Begin(self):
        # prepare the renderer, creates the sink pipe 
        self.renderer.Prepare()
        
        self.__logger.debug("%s: prepare task queue", self.name)
        # prepare task queue
        for idx, task in enumerate(self.tasks):
            task.SetIdx(idx)
            self.taskQueue.put(task)

    def IsRunning(self):
        return True
    def IsIdle(self):
        return False
    def IsAborted(self):
        return False
    def IsDone(self):
        return self.__isDone

    def ToSink(self, pilCtx):
        pilCtx.ToStream(self.renderer.GetSink(), "JPEG")


    def GetTask(self, block, timeout):
        task = self.taskQueue.get(block, timeout)

        self.__logger.debug("%s: %s - start", self.name, task)
        
        self.SetInfo(task.GetInfo())
        return task
        
        
    def GetResultToFetch(self):
        return self.resultToFetch
    
    def PushResult(self, task, result):
#        if task.IsOk():
        self.__logger.debug("%s: %s - done", self.name, task)
        self.results[task.idx] = result.GetResult()
        self.FetchResult(None)
    
    def FetchResult(self, resultId):
        with self.resultToFetchLock:
            while self.results.has_key(self.resultToFetch):
                idx = self.resultToFetch
                
                self.__logger.debug("%s: resultToFetch: %s",
                                        self.name,
                                        idx)
                
                pilCtx = self.results[idx]
                self.ToSink(pilCtx)
                del self.results[idx]
                self.resultToFetch += 1




class JobContext(object):
    
    def __init__(self, jobName, renderer):
        self._jobName = jobName
        self._taskQueue = Queue.Queue()
        
        self._workers = []

        # the number of active workers
        self._activeWorkers = Value('i', 0)

        # the index of the result to process
        self._resultFlag = Value('i', 0)
        
        # a flag to control the workers
        # 0 .. normal run mode
        # 1 .. pause the workers
        self._runFlag = Value('i', 0)
        
        # a queue containing strings about the current processing info
        self._taskInfo = Queue.Queue()
        
        # the sink pipe, only needed to start new workers
        self._renderer = renderer
        
    def GetCurrentProgress(self):
#        return self.__currProgress
        return self._resultFlag.value
    
    def GetInfo(self):
        info = ProgressHandler.GetInfo(self)
        while not self.IsAborted():
            try:
                info = self._taskInfo.get(False)
                self._SetInfo(info)
            except Queue.Empty:
                break
        return info
    
    def GetName(self):
        return self._jobName
    
    def Pause(self):
        if self._runFlag.value == 0:
            self._runFlag.value = 1
#        else:
#            raise ValueError("invalid state")
    def IsIdle(self):
        if self.IsDone() or self.IsAborted():
            return False
        else:
            return self._runFlag.value == 1
    
    def Resume(self):
        if self._runFlag.value == 1:
            self._runFlag.value = 0
#        else:
#            raise ValueError("invalid state")
    
    def IsRunning(self):
        if self.IsDone() or self.IsAborted():
            return False
        else:
            return self._runFlag.value == 0

    def PauseResume(self):
        if self._runFlag.value == 0:
            self._runFlag.value = 1
        elif self._runFlag.value == 1:
            self._runFlag.value = 0

