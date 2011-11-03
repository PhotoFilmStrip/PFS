# encoding: UTF-8


class JobAbortedException(Exception):
    pass


class Job(object):
    def __init__(self, evt, target=None, args=None, kwargs=None):
        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}

        assert callable(target), "target must be callable"
        assert isinstance(args, list) or isinstance(args, tuple), \
                    "args must be of type list or tuple"
        assert isinstance(kwargs, dict), \
                    "kwargs must be of type dict"

        self.target = target
        self.evt = evt
        self.args = args
        self.kwargs = kwargs

        self.__done = False
        self.__aborted = False

    def _AbortRun(self):
        self.__aborted = True
        
        self.evt.exception = JobAbortedException()
        self.evt.DispatchEvent()

    def _Execute(self):
        """
        called by the jobbing framework
        """
        try:
            return self.Run()
        finally:
            self.__done = True
            self._Finish()
            
    def _Finish(self):
        pass

    def Run(self):
        return self.target(*self.args, **self.kwargs)

    def IsAborted(self):
        return self.__aborted

    def IsDone(self):
        return self.__done
