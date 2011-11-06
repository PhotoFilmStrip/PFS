# encoding: UTF-8


from photofilmstrip.lib.jobimpl.WorkLoad import WorkLoad


class Task(WorkLoad):
    def __init__(self, backend, resolution):
        self.backend = backend
        self.resolution = resolution
        self.idx = None
        self.info = u""

        self.result = None
        
    def GetInfo(self):
        return self.info
    def SetInfo(self, info):
        self.info = info
        
    def GetIdx(self):
        return self.idx
    def SetIdx(self, idx):
        self.idx = idx
        
    def __str__(self):
        return "%s_%s" % (self.__class__.__name__, self.idx)


class TaskCropResize(Task):
    def __init__(self, backend, picture, rect, resolution):
        Task.__init__(self, backend, resolution)
        self.picture = picture
        self.rect = rect
        
    def Run(self, jobContext):
        image = jobContext.FetchImage(self.backend, self.picture)
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
        
    def Run(self, jobContext):
        image1 = self.taskPic1.Run(jobContext)
        image2 = self.taskPic2.Run(jobContext)
        
        img = self.backend.Transition(self.kind, 
                                      image1, image2, 
                                      self.percentage)
        
        return img
