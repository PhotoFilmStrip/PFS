# encoding: UTF-8

from photofilmstrip.lib.jobimpl.IWorkLoad import IWorkLoad


class WorkLoad(IWorkLoad):
    def __init__(self):
        self.result = None

    def _Execute(self, jobContext):
        """
        called by the jobbing framework
        """
        try:
            return self.Run(jobContext)
        finally:
            self._Finish()
            
    def _Finish(self):
        pass
