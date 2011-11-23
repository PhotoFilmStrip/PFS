# encoding: UTF-8


from photofilmstrip.lib.jobimpl.WorkLoad import WorkLoad

from photofilmstrip.core.Subtitle import SubtitleSrt

from photofilmstrip.core.PILBackend import PILBackend


class Task(WorkLoad):
    def __init__(self):
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
    

class TaskSubtitle(Task):
    def __init__(self, outputPath, picCountFactor, pics):
        Task.__init__(self)
        self.__outputPath = outputPath
        self.__picCountFactor = picCountFactor
        self.__pics = pics
        self.SetInfo(_(u"generating subtitle"))
            
    def __HasComments(self):
        for pic in self.__pics:
            if pic.GetComment():
                return True
        return False
    
    def Run(self, jobContext):
        if self.__HasComments():
            st = SubtitleSrt(self.__outputPath, 
                             self.__picCountFactor)
            st.Start(self.__pics)


class TaskImaging(Task):
    def __init__(self, resolution):
        Task.__init__(self)
        self.backend = PILBackend()
        self.resolution = resolution
        self.draft = False
        
    def SetDraft(self, value):
        self.draft = value


class TaskCropResize(TaskImaging):
    def __init__(self, picture, rect, resolution):
        TaskImaging.__init__(self, resolution)
        self.picture = picture
        self.rect = rect
        
    def Run(self, jobContext):
        image = jobContext.FetchImage(self.picture)
        img = self.backend.CropAndResize(image,
                                         self.rect,
                                         self.resolution,
                                         self.draft)
        return img
    

class TaskTrans(TaskImaging):
    def __init__(self, kind, percentage,
                 pic1, rect1, pic2, rect2, resolution):
        TaskImaging.__init__(self, resolution)
        self.kind = kind
        self.percentage = percentage
        self.taskPic1 = TaskCropResize(pic1, rect1, resolution)
        self.taskPic2 = TaskCropResize(pic2, rect2, resolution)
        
    def Run(self, jobContext):
        self.taskPic1.SetDraft(self.draft)
        self.taskPic2.SetDraft(self.draft)
        image1 = self.taskPic1.Run(jobContext)
        image2 = self.taskPic2.Run(jobContext)
        
        img = self.backend.Transition(self.kind, 
                                      image1, image2, 
                                      self.percentage)
        
        return img
