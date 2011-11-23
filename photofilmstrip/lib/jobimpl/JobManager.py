# encoding: UTF-8

import logging
import multiprocessing
import Queue
import time
import threading

from photofilmstrip.lib.common.Singleton import Singleton
from .IVisualJobManager import IVisualJobManager
from .LogVisualJobManager import LogVisualJobManager
from .Worker import Worker
from .JobAbortedException import JobAbortedException


class _JobCtxGroup(object):
    
    def __init__(self, ctxGroup, workers):
        self.__ctxGroup = ctxGroup
        self.__idleQueue = Queue.Queue()
        self.__active = None
        getJobLock = threading.Lock()
        self.__getJobCond = threading.Condition(getJobLock)
       
        getJobLock = threading.Lock()
        self.__getJobCond = threading.Condition(getJobLock)
        
        self.__workers = workers

        self.__lock = threading.Lock()
    
    def Put(self, jobContext):
        self.__idleQueue.put(jobContext)
        
    def Notify(self):
        with self.__getJobCond:
            self.__getJobCond.notifyAll()
            
    def Get(self, timeout):
        return self.__idleQueue.get(timeout is not None, 
                                    timeout)
            
    def __enter__(self):
        self.__lock.acquire()
        return self
    def __exit__(self, typ, value, traceback):
        self.__lock.release()
    
    def Active(self):
        return self.__active
    
    def SetActive(self, jobContext):
        self.__active = jobContext
        self.Notify()
        
    def Wait(self, timeout=None):
        if self.__lock.acquire(False):
            self.__lock.release()
        else:
            raise RuntimeError("cannot acquire lock before long blocking operation")
        with self.__getJobCond:
            self.__getJobCond.wait(timeout)
            
    def Workers(self):
        return self.__workers


class JobManager(Singleton):
    
    DEFAULT_CTXGROUP_ID = "general"
    
    def __init__(self):
        self.__defaultVisual = LogVisualJobManager()
        self.__visuals = [self.__defaultVisual]
        
        self.__destroying = False
        self.__jobCtxGroups = {}
        
        self.__logger = logging.getLogger("JobManager")
        
    def AddVisual(self, visual):
        assert isinstance(visual, IVisualJobManager)
        if self.__defaultVisual in self.__visuals:
            self.__visuals.remove(self.__defaultVisual)

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
            
    def _GetWorkLoad(self, workerCtxGroup, block=True, timeout=None):
        jcGroup = self.__jobCtxGroups[workerCtxGroup]
        
        with jcGroup:
            while jcGroup.Active() is None:
                # no context active, get one from idle queue
                jcIdle = jcGroup.Get(1.0)
                if self.__StartCtx(jcIdle):
                    jcGroup.SetActive(jcIdle)
            
            jobCtxActive = jcGroup.Active()
            try:
                workLoad = jobCtxActive.GetWorkLoad(False, None)
                return jobCtxActive, workLoad # FIXME: no tuple
            except Queue.Empty:
                # no more workloads, job done, only __FinishCtx() needs to be done
                # wait for all workers to be done (better use WaitForMultipleObjects) 
                while not self.__destroying:
                    result = True
                    for worker in jcGroup.Workers(): 
                        result = result and not worker.IsBusy()
                    if result:
                        break
                    else:
                        time.sleep(0.05)
                
                jobCtxActive = jcGroup.Active()
                if jobCtxActive is not None:
                    jcGroup.SetActive(None)
                    self.__FinishCtx(jobCtxActive)
            
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
            
    def Destroy(self):
        self.__logger.debug("start destroying")
        self.__destroying = True
        for jcGroup in self.__jobCtxGroups.values():
            for worker in jcGroup.Workers():
                worker.Kill()

            jcGroup.Notify()
        
            for worker in jcGroup.Workers():
                self.__logger.debug("<%s> joining...", worker.getName())
                worker.join(3)
                if worker.isAlive():
                    self.__logger.warning("<%s> join failed", worker.getName())
                else:
                    self.__logger.debug("<%s> joined!", worker.getName())

        self.__logger.debug("destroyed")

