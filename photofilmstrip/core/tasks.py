# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2017 Jens Goepfert
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import os

from photofilmstrip.core.Subtitle import SubtitleSrt
from photofilmstrip.core import PILBackend


class Task:

    def __init__(self):
        self.info = u""
        self.subTasks = []

    def __str__(self):
        return "%s: %s" % (self.__class__.__name__, self.info)

    def IterSubTasks(self):
        for subTask in self.subTasks:
            for subSubTask in subTask.IterSubTasks():
                yield subSubTask
            yield subTask

    def GetInfo(self):
        return self.info

    def SetInfo(self, info):
        self.info = info

    def GetKey(self):
        raise NotImplementedError()

    def Run(self, jobContext):
        raise NotImplementedError()


class TaskSubtitle(Task):

    def __init__(self, picCountFactor, pics):
        Task.__init__(self)
        self.__picCountFactor = picCountFactor
        self.__pics = pics
        self.SetInfo(_(u"generating subtitle"))

    def __HasComments(self):
        for pic in self.__pics:
            if pic.GetComment():
                return True
        return False

    def GetKey(self):
        return "subtitle"

    def Run(self, jobContext):
        if self.__HasComments():
            outFile = jobContext.GetOutputFile()
            baseFile = os.path.splitext(outFile)[0]
            st = SubtitleSrt(baseFile,
                             self.__picCountFactor)
            st.Start(self.__pics)


class TaskLoadPic(Task):

    def __init__(self, picture):
        Task.__init__(self)
        self.picture = picture

    def GetKey(self):
        return 'LoadPic_{}'.format(
            self.picture.GetKey())

    def Run(self, jobContext):
        return PILBackend.GetImage(self.picture)


class TaskImaging(Task):

    def __init__(self, resolution):
        Task.__init__(self)
        self.resolution = resolution
        self.draft = False

    def SetDraft(self, value):
        self.draft = value


class TaskCropResize(TaskImaging):

    def __init__(self, picture, rect, resolution):
        TaskImaging.__init__(self, resolution)
        self.picture = picture
        self.rect = rect
        self.taskLoadPic = TaskLoadPic(picture)
        self.subTasks.append(self.taskLoadPic)

    def GetKey(self):
        return 'CropAndResize_{}_{}_{}'.format(
            self.taskLoadPic.GetKey(), self.rect, self.resolution)

    def Run(self, jobContext):
        image = jobContext.ProcessSubTask(self.taskLoadPic)
        img = PILBackend.CropAndResize(image,
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
        self.subTasks.append(self.taskPic1)
        self.subTasks.append(self.taskPic2)

    def SetDraft(self, value):
        TaskImaging.SetDraft(self, value)
        self.taskPic1.SetDraft(self.draft)
        self.taskPic2.SetDraft(self.draft)

    def GetKey(self):
        return 'TaskTrans_{}_{}_{}_{}'.format(
            self.kind, self.percentage,
            self.taskPic1.GetKey(), self.taskPic2.GetKey())

    def Run(self, jobContext):
        image1 = jobContext.ProcessSubTask(self.taskPic1)
        image2 = jobContext.ProcessSubTask(self.taskPic2)
        img = PILBackend.Transition(self.kind,
                                    image1, image2,
                                    self.percentage)

        return img
