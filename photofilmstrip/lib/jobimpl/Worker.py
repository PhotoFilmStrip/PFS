# encoding: UTF-8

import logging
import queue
import sys
import threading
import traceback

from .IJobContext import IWorker
from .IWorkLoad import IWorkLoad
from .ResultObject import ResultObject
from .JobAbortedException import JobAbortedException


class Worker(threading.Thread, IWorker):
    '''
    A worker thread that processes workloads of a JobContext. The worker belongs
    to a specific group id that decides which JobContexts are executed.
    '''

    def __init__(self, jobManager, ctxGroupId, num):
        threading.Thread.__init__(self, name="{0}-{1}".format(ctxGroupId, num))

        self.__jobManager = jobManager
        self.__ctxGroupId = ctxGroupId

        self.__logger = logging.getLogger("Worker")

    def GetContextGroupId(self):
        return self.__ctxGroupId

    def run(self):
        self.__logger.debug("<%s> Started...", self.getName())
        while 1:
            self.__logger.log(logging.NOTSET, "<%s> Worker alive", self.getName())

            jobContext = None
            workLoad = None

#            jobContext = self.__jobManager._GetJobContext(self.GetContextGroupId())
            try:
                self.__logger.debug("<%s> waiting for job", self.getName())
                jobContext, workLoad = self.__jobManager._GetWorkLoad(self.GetContextGroupId())
            except queue.Empty:
                continue
            except WorkerAbortSignal:
                break

            if not isinstance(workLoad, IWorkLoad):
                self.__logger.debug("<%s> Retrieved invalid job object '%s' from Queue: %s",
                                    self.getName(), jobContext, workLoad)
                continue

            self.__ProcessWorkLoad(jobContext, workLoad)

        self.__logger.debug("<%s> Worker gone...", self.getName())

    def __ProcessWorkLoad(self, jobContext, workLoad):
        ro = ResultObject(workLoad)
        try:
            self.__logger.debug("<%s> processing work load %s", self.getName(), workLoad)
            ro.result = workLoad._Execute(jobContext)  # IGNORE:W0212
            self.__logger.debug("<%s> execution done, result = %s", self.getName(), ro.result)
        except Exception as inst:  # IGNORE:R0703
            self.__logger.error("<%s> job exception: %s", self.getName(), inst, exc_info=1)
            ro.exception = inst
            ro.traceback = "Traceback (within worker):\n" + "".join(traceback.format_tb(sys.exc_info()[2]))

        if jobContext.IsAborted():
            ro.exception = JobAbortedException()

        try:
            self.__logger.debug("<%s> pushing result %s", self.getName(), workLoad)
            jobContext.PushResult(ro)
            self.__logger.debug("<%s> result pushed %s", self.getName(), workLoad)
        except Exception as inst:  # IGNORE:R0703
            self.__logger.error("<%s> push result exception: %s", self.getName(), inst, exc_info=1)


class WorkerAbortSignal(Exception):
    pass
