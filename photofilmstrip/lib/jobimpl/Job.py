# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Jens Goepfert
#

import logging
import queue

from .IJobContext import IJobContext
from .WorkLoad import WorkLoad
from .IWorkLoad import IWorkLoad
from .ResultObject import NoResultObject
from .JobAbortedException import JobAbortedException


class Job(IJobContext):
    '''
    A Job implements the JobContext interface and handles the smaller workloads
    in a queue.
    '''

    def __init__(self, target=None, args=None, kwargs=None,
                 groupId="general"):
        IJobContext.__init__(self)
        self.__groupId = groupId

        self.__logger = logging.getLogger("Job<%s> %s" % (groupId, self))

        self.__workQueue = queue.Queue()
        self.__resultObject = NoResultObject(WorkLoad())

        self.__done = False
        self.__aborted = False
        self.__idle = True

        if target:
            self.AddWorkLoad(SingleWorkLoad(self, target, args, kwargs))

    def GetGroupId(self):
        return self.__groupId

    def AddWorkLoad(self, workLoad):
        assert isinstance(workLoad, IWorkLoad)
        self.__workQueue.put(workLoad)

    def GetWorkLoad(self):
        if self.__aborted:
            while 1:
                self.__logger.debug("emptying task queue")
                try:
                    self.__workQueue.get(False)
                finally:
                    self.__logger.debug("task queue empty")
        else:
            return self.__workQueue.get(False)

    def PushResult(self, resultObject):
        self.__resultObject = resultObject

    def _Begin(self):
        if self.__aborted:
            self.__done = True
            raise JobAbortedException()

        self.Begin()
        self.__idle = False

    def Begin(self):
        pass

    def IsIdle(self):
        return self.__idle

    def _Done(self):
        try:
            self.Done()
        finally:
            self.__done = True

    def Done(self):
        pass

    def IsDone(self):
        return self.__done

    def IsAborted(self):
        return self.__aborted

    def Abort(self, msg=None):
        if self.__aborted:
            return False

        if self.__done:
            self.__logger.debug("cannot abort finished job!")
            return False
        else:
            self.__aborted = True
            if self.__idle:
                # Abort() got called while job is idle
                # Begin() was not called yet so Done wont get called
                self.__idle = False
                self.__done = True
                return False

            self.__logger.debug("aborting... (%s)", msg)

        return True

    def GetResultObject(self):  # , block=True):
        return self.__resultObject


class SingleWorkLoad(WorkLoad):
    '''
    A helper class to wrap a simple method call as a Workload.
    '''

    def __init__(self, job, target, args=None, kwargs=None):
        WorkLoad.__init__(self)
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}

        assert callable(target), "target must be callable"
        assert isinstance(args, list) or isinstance(args, tuple), \
                    "args must be of type list or tuple"
        assert isinstance(kwargs, dict), \
                    "kwargs must be of type dict"

        self.__job = job
        self.__target = target
        self.__args = args
        self.__kwargs = kwargs

    def Run(self, jobContext):
        return self.__target(*self.__args, job=jobContext, **self.__kwargs)

    def GetJob(self):
        return self.__job
