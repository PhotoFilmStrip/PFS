# encoding: UTF-8

import logging
import Queue
import sys
import threading
import traceback

from .IJobContext import IWorker
from .IWorkLoad import IWorkLoad
from .ResultObject import ResultObject


class Worker(threading.Thread, IWorker):
    
    def __init__(self, jobManager, ctxGroupId, num):
        threading.Thread.__init__(self, name="{0}-{1}".format(ctxGroupId, num))
        
        self.__jobManager = jobManager
        self.__ctxGroupId = ctxGroupId

        self.__busy = threading.Event()
        self.__busy.clear()
        self.__wantAbort = False
        
        self.__logger = logging.getLogger(self.getName())

    def GetContextGroupId(self):
        return self.__ctxGroupId

    def IsBusy(self):
        return self.__busy.isSet()
    def GetBusyEvent(self):
        return self.__busy

    def Kill(self):
        self.__wantAbort = True

    def __GetWorkLoad(self):
        # throws QueueEmpty Exception
        return self.__jobManager._GetWorkLoad(self.GetContextGroupId())

    def run(self):
        self.__logger.debug("Started...")
        while not self.__wantAbort:
            self.__logger.log(logging.NOTSET, "Worker alive")
            
#            jobContext = self.__jobManager._GetJobContext(self.GetContextGroupId())
            try:
                self.__logger.debug("waiting for job")
                jobContext, workLoad = self.__GetWorkLoad() # Wartet auf Job, bricht nach 1s ab und wirft eine QueueEmpty Exception.
            except Queue.Empty:
                continue

            if not isinstance(workLoad, IWorkLoad):
                self.__logger.debug("Retrieved invalid job object from Queue: %s", (jobContext, workLoad))
                continue
            
            self.__busy.set()
            if 1:
#            if not job.IsAborted():
                ## Job nicht ausführen, wenn er auf "Aborted" steht. In diesem Fall ist
                ## das Result Event bereits versendet und eine Ausführung unerwünscht.
                self.__ProcessWorkLoad(jobContext, workLoad)
            self.__busy.clear()
        self.__logger.debug("Worker gone...")

    def __ProcessWorkLoad(self, jobContext, workLoad):
        ro = ResultObject(workLoad)
        try:
            self.__logger.debug("processing work load %s", workLoad)
            ro.result = workLoad._Execute(jobContext) # IGNORE:W0212
            self.__logger.debug("execution done, result = %s", ro.result)
        except Exception, inst: # IGNORE:R0703
            self.__logger.error("job exception: %s", inst, exc_info=1)
            ro.exception = inst
            ro.traceback = "Traceback (within worker):\n" + "".join(traceback.format_tb(sys.exc_info()[2]))

        if jobContext.IsAborted():
            ro.exception = JobAbortedException()

        try:
            self.__logger.debug("pushing result %s", workLoad)
            jobContext.PushResult(ro)
            self.__logger.debug("result pushed %s", workLoad)
        except Exception, inst: # IGNORE:R0703
            self.__logger.error("push result exception: %s", inst, exc_info=1)
        
#        self.__logger.debug("notifying: %s", job.evt.notifyObject)
#        try:
#            job.evt.DispatchEvent()
#        except Exception, inst: # IGNORE:R0703
#            self.__logger.error("notification exception: %s", inst, exc_info=1)


class JobAbortedException(Exception):
    pass
