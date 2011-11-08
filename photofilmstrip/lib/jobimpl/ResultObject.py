
import sys
from photofilmstrip.lib.jobimpl.IWorkLoad import IWorkLoad


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
            if printTraceback:
                print >> sys.stderr, self.traceback,
            raise self.exception
        else:
            return self.result

