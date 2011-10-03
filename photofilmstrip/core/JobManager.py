'''
Created on 15.08.2011

@author: jens
'''

import logging
import multiprocessing
import time

from multiprocessing.queues import Queue, Full, Empty
from multiprocessing.sharedctypes import Value

import threading

from photofilmstrip.lib.common.Singleton import Singleton
from photofilmstrip.lib.common.ObserverPattern import Observable
from photofilmstrip.core.ProgressHandler import ProgressHandler


class JobContext(ProgressHandler):
    
    def __init__(self, jobName, renderer):
        ProgressHandler.__init__(self)
        self._jobName = jobName
        self._taskQueue = Queue()
        
        self._workers = []
        
        # the index of the result to process
        self._resultFlag = Value('i', 0)
        
        # a flag to control the workers
        # 0 .. normal run mode
        # 1 .. pause the workers
        # 2 .. aborted
        # 3 .. workers are done
        self._runFlag = Value('i', 0)
        
        # a queue containing strings about the current processing info
        self._taskInfo = Queue()
        
        # the sink pipe, only needed to start new workers
        self._renderer = renderer
        
    def AddWorker(self, worker):
        self._workers.append(worker)
    def GetWorkers(self):
        return self._workers
    
    def GetTaskQueue(self):
        return self._taskQueue
    def AppendTask(self, task):
        self._taskQueue.put(task)
        
    def GetResultFlag(self):
        return self._resultFlag
    def GetRunFlag(self):
        return self._runFlag
    
    def GetInfoQueue(self):
        return self._taskInfo
    
    def GetRenderer(self):
        return self._renderer

    def GetCurrentProgress(self):
#        return self.__currProgress
        return self._resultFlag.value
    
    def GetInfo(self):
        info = ProgressHandler.GetInfo(self)
        while not self.IsAborted():
            try:
                info = self._taskInfo.get(False)
                self._SetInfo(info)
            except multiprocessing.queues.Empty:
                break
        return info
    
    def GetName(self):
        return self._jobName
    
    def GetWorkerCount(self):
        return len(self._workers)
    
    def Pause(self):
        if self._runFlag.value == 0:
            self._runFlag.value = 1
#        else:
#            raise ValueError("invalid state")
    def Resume(self):
        if self._runFlag.value == 1:
            self._runFlag.value = 0
#        else:
#            raise ValueError("invalid state")

    def PauseResume(self):
        if self._runFlag.value == 0:
            self._runFlag.value = 1
        elif self._runFlag.value == 1:
            self._runFlag.value = 0


class JobManager(Singleton, threading.Thread, Observable):
    
    def __init__(self):
        threading.Thread.__init__(self, name="JobManager")
        Observable.__init__(self)
        self._active = True
        self._jobCtxs = []
        self._jobCtxLock = threading.Lock()
        
        self.__logger = logging.getLogger("JobManager")
        
        self.start()
        
    def run(self):
        self.__logger.debug("started")
        while self._active:
            
            with self._jobCtxLock:
                jcIdx = 0
                while jcIdx < len(self._jobCtxs):
                    jc = self._jobCtxs[jcIdx]
                    if jc.GetRunFlag().value >= 2:
                        self.__logger.debug("JobContext %s finished", jc.GetName())
                        self._jobCtxs.remove(jc)
                        jc.GetRenderer().Finalize()
                        jc.Done()
                    else:
                        jcIdx += 1
                
            time.sleep(0.1)
        
    def Register(self, jobName, renderer, tasks):
        self.__logger.debug("%s: register job", jobName)
        
        # prepare the renderer, creates the sink pipe 
        renderer.Prepare()
        
        jc = JobContext(jobName, renderer)
        jc.SetMaxProgress(len(tasks))
        
        # prepare workers
        cpuCount = multiprocessing.cpu_count()
        cpuCount = 1
        for num in range(cpuCount):
            tw = TaskWorker("%d" % num,
                            jc.GetRunFlag(),
                            jc.GetTaskQueue(),
                            jc.GetInfoQueue(),
                            jc.GetResultFlag(),
                            renderer.GetSink())
            jc.AddWorker(tw)

        self.__logger.debug("%s: prepare task queue", jobName)
        # prepare task queue
        idx = 0
        for idx, task in enumerate(tasks):
            task.SetIdx(idx)
            jc.AppendTask(task)

        for tw in jc.GetWorkers():            
            tw.start()

        with self._jobCtxLock:
            self._jobCtxs.append(jc)

        self.Notify(jc)
        
    def Abort(self, jobContext):
        self.__logger.debug("%s: aborting...", jobContext.GetName())
        
        # the workers should stop processing tasks
        jobContext.Pause()
        
        # set the abort flag in the progress handler
        jobContext.Abort()
        
        while 1:
            self.__logger.debug("%s: emptying task queue", jobContext.GetName())
            try:
                jobContext.GetTaskQueue().get(True, 0.05)
            except Empty:
                self.__logger.debug("%s: task queue empty", jobContext.GetName())
                break
            
        # release the pause loop in the workers
        jobContext.Resume()
            
        # wait for workers to terminate
        for tw in jobContext.GetWorkers():
            self.__logger.debug("%s: joining worker: %s", jobContext.GetName(), tw)
            tw.join(3.0)
            if tw.is_alive():
                self.__logger.debug("%s: killing worker: %s", jobContext.GetName(), tw)
                tw.terminate()
                
        # set the run flag to aborted
        jobContext.GetRunFlag().value = 2
        
    def Destroy(self):
        self.__logger.debug("start destroying")
        with self._jobCtxLock:
            # empty all queues, so that workers will finish their main loop
            for jc in self._jobCtxs:
                self.Abort(jc)

        self._active = False
        
        self.__logger.debug("joining...")
        self.join()
        self.__logger.debug("destroyed")
            

class TaskWorker(multiprocessing.Process):
#class TaskWorker(threading.Thread):
    
    def __init__(self, name, runFlag, taskQueue, infoQueue, resultToFetch, sink):
        multiprocessing.Process.__init__(self, name=name)#, verbose=1)
#        threading.Thread.__init__(self, name=name)#, verbose=1)
        
        self.runFlag = runFlag
        self.taskQueue = taskQueue
        self.infoQueue = infoQueue
        self.resultToFetch = resultToFetch
        self.sink = sink
        
        self.imgCache = {}
        self.imgKeyStack = []
        self.results = {}
        
        self.__logger = logging.getLogger("TaskWorker")
        
    def FetchImage(self, backend, pic):
        if not self.imgCache.has_key(pic.GetFilename()):
            self.__logger.debug("%s: GetImage(%s)", self.name, pic.GetFilename())
            if len(self.imgKeyStack) > 1:
                key = self.imgKeyStack.pop(0)
                self.__logger.debug("%s: Pop cache (%s)", self.name, key)
                self.imgCache[key] = None
                                
            # TODO: gleiches bild mit unterschiedlicher rotation
            self.imgCache[pic.GetFilename()] = backend.CreateCtx(pic)
            self.imgKeyStack.append(pic.GetFilename())
        return self.imgCache[pic.GetFilename()]
        
    def run(self):
        self.__logger.debug("%s: worker started", self.name)
        active = True
        while active:
            task = None

            # check the pause state
            while self.runFlag.value == 1:
                time.sleep(0.1)
            
            try:
                task = self.taskQueue.get(True, 0.1)
            except multiprocessing.queues.Empty:
                self.__logger.debug("%s: Queue empty", self.name)
                active = False
            
            if task:
                self.__logger.debug("%s: %s - start", self.name, task)
                
                self.infoQueue.put(task.GetInfo())
                
                task.Run(self)
                if task.IsOk():
                    self.__logger.debug("%s: %s - done", self.name, task)
                    self.results[task.idx] = task
                else:
                    self.__logger.error("shit")
                
            self.__logger.debug("%s: resultToFetch: %s", self.name, self.resultToFetch.value)
            while self.results.has_key(self.resultToFetch.value):
                idx = self.resultToFetch.value
                task = self.results[idx]
                task.ToSink(self.sink)
                del self.results[idx]
                self.resultToFetch.value += 1
        
        self.__logger.debug("%s: worker finished", self.name)
        self.runFlag.value = 3
