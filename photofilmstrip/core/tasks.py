'''
Created on 15.08.2011

@author: jens
'''

import traceback


class Task(object):
    def __init__(self, backend, resolution):
        self.backend = backend
        self.resolution = resolution
        self.idx = None
        self.info = u""

        self.ok = False        
        self.result = None
        
    def GetInfo(self):
        return self.info
    def SetInfo(self, info):
        self.info = info
        
    def GetIdx(self):
        return self.idx
    def SetIdx(self, idx):
        self.idx = idx
        
    def Run(self, procCtx):
        try:
            self.result = self._Run(procCtx)
            self.ok = True
        except Exception:
            traceback.print_exc()
            self.ok = False
        return self.result
        
    def ToSink(self, sink):
        self.result.ToStream(sink, "JPEG")
        
    def IsOk(self):
        return self.ok
            
    def _Run(self, procCtx):
        raise NotImplementedError()
    
    def __str__(self):
        return "%s_%s" % (self.__class__.__name__, self.idx)


class TaskCropResize(Task):
    def __init__(self, backend, picture, rect, resolution):
        Task.__init__(self, backend, resolution)
        self.picture = picture
        self.rect = rect
        
    def _Run(self, procCtx):
        image = procCtx.FetchImage(self.backend, self.picture)
        img = self.backend.CropAndResize(image,
                                         self.rect,
                                         self.resolution)
        return img
    

class TaskTrans(Task):
    def __init__(self, backend, kind, percentage,
                 pic1, rect1, pic2, rect2, resolution):
        Task.__init__(self, backend, resolution)
        self.kind = kind
        self.percentage = percentage
        self.taskPic1 = TaskCropResize(backend, pic1, rect1, resolution)
        self.taskPic2 = TaskCropResize(backend, pic2, rect2, resolution)
        
    def _Run(self, procCtx):
        image1 = self.taskPic1.Run(procCtx)
        image2 = self.taskPic2.Run(procCtx)
        
        img = self.backend.Transition(self.kind, 
                                      image1, image2, 
                                      self.percentage)
        
        return img
