# encoding: UTF-8

import logging
import Queue
import sys
import threading
import traceback

from .IJobContext import IWorker
from .IWorkLoad import IWorkLoad
from .ResultObject import ResultObject
from .JobAbortedException import JobAbortedException


class Worker(threading.Thread, IWorker):
    
    def __init__(self, jobManager, ctxGroupId, num):
        threading.Thread.__init__(self, name="{0}-{1}".format(ctxGroupId, num))
        
        self.__jobManager = jobManager
        self.__ctxGroupId = ctxGroupId

        self.__busy = threading.Event()
        self.__busy.clear()
        self.__wantAbort = False
        
        self.__logger = logging.getLogger("Worker")

    def GetContextGroupId(self):
        return self.__ctxGroupId

    def IsBusy(self):
        return self.__busy.isSet()
    def GetBusyEvent(self):
        return self.__busy

    def Kill(self):
        self.__wantAbort = True

    def run(self):
        self.__logger.debug("<%s> Started...", self.getName())
        while not self.__wantAbort:
            self.__logger.log(logging.NOTSET, "<%s> Worker alive", self.getName())
            
#            jobContext = self.__jobManager._GetJobContext(self.GetContextGroupId())
            try:
                self.__logger.debug("<%s> waiting for job", self.getName())
                jobContext, workLoad = self.__jobManager._GetWorkLoad(self.GetContextGroupId())
            except Queue.Empty:
                continue
            
            if not isinstance(workLoad, IWorkLoad):
                self.__logger.debug("<%s> Retrieved invalid job object from Queue: %s", 
                                    self.getName(), jobContext, workLoad)
                continue
            
            if self.__wantAbort:
                # maybe destroying is in progress, don|t start last job
                self.__logger.debug("<%s> got job while destroying. worload not processed", self.getName())
            else:
                self.__busy.set()
                self.__ProcessWorkLoad(jobContext, workLoad)
                self.__busy.clear()
                
        self.__logger.debug("<%s> Worker gone...", self.getName())

    def __ProcessWorkLoad(self, jobContext, workLoad):
        ro = ResultObject(workLoad)
        try:
            self.__logger.debug("<%s> processing work load %s", self.getName(), workLoad)
            ro.result = workLoad._Execute(jobContext) # IGNORE:W0212
            self.__logger.debug("<%s> execution done, result = %s", self.getName(), ro.result)
        except Exception, inst: # IGNORE:R0703
            self.__logger.error("<%s> job exception: %s", self.getName(), inst, exc_info=1)
            ro.exception = inst
            ro.traceback = "Traceback (within worker):\n" + "".join(traceback.format_tb(sys.exc_info()[2]))

        if jobContext.IsAborted():
            ro.exception = JobAbortedException()

        try:
            self.__logger.debug("<%s> pushing result %s", self.getName(), workLoad)
            jobContext.PushResult(ro)
            self.__logger.debug("<%s> result pushed %s", self.getName(), workLoad)
        except Exception, inst: # IGNORE:R0703
            self.__logger.error("<%s> push result exception: %s", self.getName(), inst, exc_info=1)
