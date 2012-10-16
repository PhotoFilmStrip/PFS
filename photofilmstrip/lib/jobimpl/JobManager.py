# encoding: UTF-8

import logging
import multiprocessing
import Queue
import threading

from photofilmstrip.lib.common.Singleton import Singleton
from photofilmstrip.lib.DestructionManager import Destroyable

from .IVisualJobManager import IVisualJobManager
from .IVisualJob import IVisualJob
from .LogVisualJobManager import LogVisualJobManager
from .Worker import Worker, WorkerAbortSignal
from .JobAbortedException import JobAbortedException


class _JobCtxGroup(object):
    
    def __init__(self, ctxGroup, workers):
        self.__ctxGroup = ctxGroup
        self.__idleQueue = Queue.Queue()
        self.__active = None

        self.__doneCount = 0
        self.__doneEvent = threading.Event()
        
        self.__workers = workers

        self.__lock = threading.Lock()
    
    def Put(self, jobContext):
        self.__idleQueue.put(jobContext)
        
    def Get(self):
        return self.__idleQueue.get()
            
    def __enter__(self):
        self.__lock.acquire()
        return self
    def __exit__(self, typ, value, traceback):
        self.__lock.release()
    
    def Active(self):
        return self.__active
    
    def SetActive(self, jobContext):
        self.__active = jobContext
        if jobContext is not None:
            self.__doneCount = 0
            self.__doneEvent.clear()
        
    def DoneCount(self):
        return self.__doneCount
    def CheckBusy(self):
        return self.__doneCount < len(self.__workers)
    def IncDoneCount(self):
        self.__doneCount += 1
    
    def SetDoneEvent(self):
        self.__doneEvent.set()
    def WaitDoneEvent(self):
        self.__doneEvent.wait()
        
    def Workers(self):
        return self.__workers


class JobManager(Singleton, Destroyable):
    
    DEFAULT_CTXGROUP_ID = "general"
    
    def __init__(self):
        Destroyable.__init__(self)
        self.__defaultVisual = LogVisualJobManager()
        self.__visuals = [self.__defaultVisual]
        
        self.__destroying = False
        self.__jobCtxGroups = {}
        
        self.__logger = logging.getLogger("JobManager")
        
    def AddVisual(self, visual):
        assert isinstance(visual, IVisualJobManager)
        if self.__defaultVisual in self.__visuals:
            self.__visuals.remove(self.__defaultVisual)

        if visual not in self.__visuals:
            self.__visuals.append(visual)
    
    def RemoveVisual(self, visual):
        if visual in self.__visuals:
            self.__visuals.remove(visual)
        
        if len(self.__visuals) == 0:
            self.__visuals.append(self.__defaultVisual)
        
    def Init(self, workerCtxGroup=None, workerCount=None):
        if workerCtxGroup is None:
            workerCtxGroup = JobManager.DEFAULT_CTXGROUP_ID
        if workerCount is None:
            workerCount = multiprocessing.cpu_count()
            
        if self.__jobCtxGroups.has_key(workerCtxGroup):
            raise RuntimeError("group already initialized")
        
        workers = []
        i = 0
        while i < workerCount:
            self.__logger.debug("creating worker for group %s", workerCtxGroup)
            worker = Worker(self, workerCtxGroup, i)
            workers.append(worker)
                            
            i += 1

        jcGroup = _JobCtxGroup(workerCtxGroup, workers)
        self.__jobCtxGroups[workerCtxGroup] = jcGroup
            
        for worker in workers:
            worker.start()

            
    def EnqueueContext(self, jobContext):
        assert isinstance(threading.current_thread(), threading._MainThread)
        
        if not self.__jobCtxGroups.has_key(jobContext.GetGroupId()):
            raise RuntimeError("job group %s not available" % jobContext.GetGroupId()) 

        self.__logger.debug("%s: register job", jobContext)
        
        jcGroup = self.__jobCtxGroups[jobContext.GetGroupId()]
        jcGroup.Put(jobContext)
        
        for visual in self.__visuals:
            visual.RegisterJob(jobContext)
                
    def _GetWorkLoad(self, workerCtxGroup):
        jcGroup = self.__jobCtxGroups[workerCtxGroup]
        
        try:
            with jcGroup:
                while jcGroup.Active() is None:
                    jcIdle = jcGroup.Get()
                    if jcIdle is None:
                        raise WorkerAbortSignal()
                    if self.__StartCtx(jcIdle):
                        jcGroup.SetActive(jcIdle)
                
                jobCtxActive = jcGroup.Active()
                if self.__destroying:
                    # if in destroying state raise Queue.Empty() to enter
                    # the except section and get FinishCtx() called
                    raise Queue.Empty()
                workLoad = jobCtxActive.GetWorkLoad()
                return jobCtxActive, workLoad # FIXME: no tuple
        except Queue.Empty:
            # no more workloads, job done, only __FinishCtx() needs to be done
            # wait for all workers to be done
            jcGroup.IncDoneCount()
            if jcGroup.CheckBusy():
                self.__logger.debug("<%s> block until ready... %s", 
                                    threading.currentThread().getName(), 
                                    jcGroup.DoneCount())
                jcGroup.WaitDoneEvent()
                self.__logger.debug("<%s> block released continuing... %s", 
                                    threading.currentThread().getName(), 
                                    jcGroup.DoneCount())
            else:
                with jcGroup:
                    jobCtxActive = jcGroup.Active()
                    if jobCtxActive is not None:
                        jcGroup.SetActive(None)
                        self.__FinishCtx(jobCtxActive)
                
                self.__logger.debug("<%s> set done... %s", 
                                    threading.currentThread().getName(), 
                                    jcGroup.DoneCount())
                jcGroup.SetDoneEvent()
                
            if self.__destroying:
                raise WorkerAbortSignal()
            else:
                raise Queue.Empty()

    def __StartCtx(self, ctx):
        self.__logger.debug("<%s> starting %s...", 
                            threading.currentThread().getName(), ctx.GetName())
        try:
            ctx._Begin() # IGNORE:W0212
        except JobAbortedException:
            return False    
        except:
            self.__logger.error("<%s> not started %s", # IGNORE:W0702
                                threading.currentThread().getName(), ctx.GetName(), exc_info=1) 
            return False            

        self.__logger.debug("<%s> started %s", 
                            threading.currentThread().getName(), ctx.GetName())
        return True
    
    def __FinishCtx(self, ctx):
        self.__logger.debug("<%s> finalizing %s...", 
                            threading.currentThread().getName(), ctx.GetName())
        try:
            ctx._Done() # IGNORE:W0212
        except:
            self.__logger.error("<%s> error %s", # IGNORE:W0702
                                threading.currentThread().getName(), ctx.GetName(), exc_info=1)
        finally:
            self.__logger.debug("<%s> finished %s", 
                                threading.currentThread().getName(), ctx.GetName())

        for visual in self.__visuals:
            visual.RemoveJob(ctx)
            
    def Destroy(self):
        self.__logger.debug("start destroying")
        self.__destroying = True
        for jcGroup in self.__jobCtxGroups.values():
            for worker in jcGroup.Workers():
                # put invalid jobs in idle queue to release the blocking state
                jcGroup.Put(None)

            for worker in jcGroup.Workers():
                self.__logger.debug("<%s> joining...", worker.getName())
                worker.join(3)
                if worker.isAlive():
                    self.__logger.warning("<%s> join failed", worker.getName())
                else:
                    self.__logger.debug("<%s> joined!", worker.getName())

        self.__logger.debug("destroyed")

