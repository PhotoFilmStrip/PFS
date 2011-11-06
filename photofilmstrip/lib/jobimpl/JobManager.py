'''
Created on 15.08.2011

@author: jens
'''

import logging
import multiprocessing
import Queue
import time
import threading

from photofilmstrip.lib.common.Singleton import Singleton
from photofilmstrip.lib.jobimpl.IVisualJobManager import IVisualJobManager
from photofilmstrip.lib.jobimpl.LogVisualJobManager import LogVisualJobManager
from photofilmstrip.lib.jobimpl.Worker import Worker



class JobManager(Singleton):
    
    DEFAULT_CTXGROUP_ID = "general"
    
    def __init__(self):
#        threading.Thread.__init__(self, name="JobManager")
        self._defaultVisual = LogVisualJobManager()
        self._visuals = [self._defaultVisual]
        
        self._active = True
        self._worker = []

        self._jobCtxIdleLock = threading.Lock()
        self._jobCtxsIdle = {}
        
        self._jobCtxActiveLock = threading.Lock()
        self._jobCtxsActive = {}
        
        self.__logger = logging.getLogger("JobManager")
        
    def AddVisual(self, visual):
        assert isinstance(visual, IVisualJobManager)
        if self._defaultVisual in self._visuals:
            self._visuals.remove(self._defaultVisual)

        self._visuals.append(visual)
    
    def RemoveVisual(self, visual):
        if visual in self._visuals:
            self._visuals.remove(visual)
        
        if len(self._visuals) == 0:
            self._visuals.append(self._defaultVisual)
        
    def Init(self, workerCtxGroup=None, workerCount=None):
        if workerCtxGroup is None:
            workerCtxGroup = JobManager.DEFAULT_CTXGROUP_ID
        if workerCount is None:
            workerCount = multiprocessing.cpu_count()
            
        # initialize queues
        with self._jobCtxIdleLock:
            if not self._jobCtxsIdle.has_key(workerCtxGroup):
                self._jobCtxsIdle[workerCtxGroup] = Queue.Queue()
        with self._jobCtxActiveLock:
            if not self._jobCtxsActive.has_key(workerCtxGroup):
                self._jobCtxsActive[workerCtxGroup] = None
        
        newWorkers = []
        i = 0
        while i < workerCount:
            self.__logger.debug("creating worker for group %s", workerCtxGroup)
            worker = Worker(self, workerCtxGroup, i)
            newWorkers.append(worker)
                            
            i += 1
            
        for worker in newWorkers:
            self._worker.append(worker)
            worker.start()

    def EnqueueContext(self, jobContext):
        assert isinstance(threading.current_thread(), threading._MainThread)
        
        if not self._jobCtxsIdle.has_key(jobContext.GetGroupId()):
            raise RuntimeError("no worker for job group available") 

        self.__logger.debug("%s: register job", jobContext)
        
        self._jobCtxsIdle[jobContext.GetGroupId()].put(jobContext)

        for visual in self._visuals:
            visual.RegisterJob(jobContext)

    def _GetWorkLoad(self, workerCtxGroup, block=True, timeout=0.1):
        jcIdleQueue = self._jobCtxsIdle[workerCtxGroup]
        
        jobCtxActive = self._jobCtxsActive[workerCtxGroup]
        if jobCtxActive is None:
            # no context active, get one from idle queue
            jcIdle = jcIdleQueue.get(True, 1)
            self.__StartCtx(jcIdle)
            jobCtxActive = jcIdle
            self._jobCtxsActive[workerCtxGroup] = jobCtxActive
    
        try:
            return jobCtxActive, jobCtxActive.GetTask(block, timeout) # FIXME: no tuple
        except Queue.Empty:
            self._jobCtxsActive[workerCtxGroup] = None
            self.__FinishCtx(jobCtxActive)
            raise

    def __StartCtx(self, ctx):
        self.__logger.debug("starting %s...", ctx.GetName())
        try:
            ctx.Begin()
        finally:
            self.__logger.debug("started %s", ctx.GetName())
    
    def __FinishCtx(self, ctx):
        self.__logger.debug("finalizing %s...", ctx.GetName())
        try:
            ctx.Finalize()
        finally:
            self.__logger.debug("finished %s", ctx.GetName())
            
#    def Abort(self, jobContext):
#        self.__logger.debug("%s: aborting...", jobContext.GetName())
#        
#        # the workers should stop processing tasks
#        jobContext.Pause()
#        
#        # set the abort flag in the progress handler
#        jobContext.Abort()
#        
#        while 1:
#            self.__logger.debug("%s: emptying task queue", jobContext.GetName())
#            try:
#                jobContext.GetTaskQueue().get(True, 0.05)
#            except Queue.Empty:
#                self.__logger.debug("%s: task queue empty", jobContext.GetName())
#                break
#            
#        # release the pause loop in the workers
#        jobContext.Resume()
#            
#        # wait for workers to terminate
#        for tw in jobContext.GetWorkers():
#            self.__logger.debug("%s: joining worker: %s", jobContext.GetName(), tw)
#            tw.join(3.0)
#            if tw.is_alive():
#                self.__logger.debug("%s: killing worker: %s", jobContext.GetName(), tw)
#                tw.terminate()
                
    def Destroy(self):
        self.__logger.debug("start destroying")
        for worker in self._worker:
            worker.Kill()

        for worker in self._worker:
            self.__logger.debug("joining worker %s", worker.getName())
            worker.join(3)
            if worker.isAlive():
                self.__logger.warning("could not join worker %s", worker.getName())

        self.__logger.debug("destroyed")

