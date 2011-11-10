# encoding: UTF-8

class IWorkLoad(object):
    def _Execute(self, jobContext):
        raise NotImplementedError()
            
    def _Finish(self):
        raise NotImplementedError()

    def Run(self, jobContext):
        raise NotImplementedError()
