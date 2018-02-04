# encoding: UTF-8


class IVisualJobManager:

    def RegisterJob(self, job):
        raise NotImplementedError()

    def RemoveJob(self, job):
        raise NotImplementedError()
