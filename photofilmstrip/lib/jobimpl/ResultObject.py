# encoding: UTF-8

import sys
from .IWorkLoad import IWorkLoad


class ResultObject(object):

    def __init__(self, source):
        assert isinstance(source, IWorkLoad)
        self.__source = source
        self.result = None
        self.exception = None
        self.traceback = None

    def GetSource(self):
        return self.__source

    def GetResult(self, printTraceback=True):
        if self.exception:
            if printTraceback and self.traceback is not None:
                print(self.traceback, end=' ', file=sys.stderr)
            raise self.exception  # pylint: disable=raising-bad-type
        else:
            return self.result


class NoResultObject(ResultObject):
    pass
