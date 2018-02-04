# encoding: UTF-8


class IVisualJobHandler:

    def OnHandleJobBegin(self, jobContext):
        raise NotImplementedError()

    def OnHandleJobDone(self, jobContext):
        raise NotImplementedError()

    def OnHandleJobUpdate(self, jobContext, fields=None):
        raise NotImplementedError()
