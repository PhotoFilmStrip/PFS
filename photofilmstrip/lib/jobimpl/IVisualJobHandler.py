# encoding: UTF-8


class IVisualJobHandler(object):
    
    def OnHandleJobDone(self):
        raise NotImplementedError()
    
    def OnHandleJobUpdate(self, fields=None):
        raise NotImplementedError()
