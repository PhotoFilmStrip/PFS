# encoding: UTF-8

import Queue
import time

from .IJobContext import IJobContext
from .WorkLoad import WorkLoad


class Job(IJobContext):
    def __init__(self, target=None, args=None, kwargs=None):
        IJobContext.__init__(self)
        
        self.__workQueue = Queue.Queue()
        self.__resultObject = None
        self.__done = False

        if target:
            self.__workQueue.put(SingleWorkLoad(target, args, kwargs))

    def GetGroupId(self):
        return "general"
    
    def GetWorkLoad(self, block, timeout):
        return self.__workQueue.get(block, timeout)
    
    def PushResult(self, resultObject):
        self.__resultObject = resultObject
    
    def Begin(self):
        pass
    def Done(self):
        self.__done = True
    
    def GetResultObject(self, block=True):
        while block and not self.__done:
            time.sleep(0.1)
        return self.__resultObject



class SingleWorkLoad(WorkLoad):

    def __init__(self, target, args=None, kwargs=None):
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

        self.__target = target
        self.__args = args
        self.__kwargs = kwargs

    def Run(self, jobContext):
        return self.__target(*self.__args, **self.__kwargs)
