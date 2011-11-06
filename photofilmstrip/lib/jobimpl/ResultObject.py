
import sys


class ResultObject(object):

    def __init__(self):
        self.result = None
        self.exception = None
        self.traceback = None

    def GetResult(self, printTraceback=True):
        if self.exception:
            if printTraceback:
                print >> sys.stderr, self.traceback,
            raise self.exception
        else:
            return self.result

