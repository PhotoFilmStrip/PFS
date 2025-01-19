# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2011 Jens Goepfert
#

import wx

from photofilmstrip.lib.common.ObserverPattern import Observer
from photofilmstrip.lib.jobimpl.Job import Job
from photofilmstrip.lib.jobimpl.JobManager import JobManager

from photofilmstrip.core import PILBackend


class ImageCache(Observer):

    SIZE = 400

    def __init__(self, win, thumbSize, thumb=None):
        self._picRegistry = {}
        self._wxImgCache = {}
        self._wxBmpCache = {}
        self._pilCache = {}
        self._inScalingQueue = object()

        self.win = win
        self.thumbDefault = thumb
        self.thumbSize = thumbSize

    def Destroy(self):
        self.win = None
        self._wxImgCache.clear()
        self._wxBmpCache.clear()
        self._picRegistry.clear()
        self._pilCache.clear()

    def ObservableUpdate(self, obj, arg):
        if arg == 'bitmap':
            self.UpdatePicture(obj)

    def RegisterPicture(self, picture, pilThumb=None):
#        if pilThumb is None:
#            pilThumb = PILBackend.GetThumbnail(picture, height=120)

        key = picture.GetKey()
        self._picRegistry[key] = picture
        self._pilCache[key] = pilThumb

        picture.AddObserver(self)

    def UpdatePicture(self, picture):
        key = picture.GetKey()
        if key in self._wxImgCache:
            del self._wxImgCache[key]
        if key in self._wxBmpCache:
            del self._wxBmpCache[key]
        if key in self._pilCache:
            del self._pilCache[key]

        self.RegisterPicture(picture)

    def GetImage(self, picture):
        key = picture.GetKey()
        if key not in self._wxImgCache:
            pilImg = PILBackend.GetThumbnail(picture, width=ImageCache.SIZE)
            wxImg = wx.Image(PILBackend.ImageToStream(pilImg), wx.BITMAP_TYPE_JPEG)
            self._wxImgCache[key] = wxImg
        return self._wxImgCache[key]

    def GetThumbBmp(self, picture):
        key = picture.GetKey()
        if key not in self._wxBmpCache:
            pilImg = self._pilCache.get(key)
            if pilImg is None:
                self._pilCache[key] = self._inScalingQueue
                tgj = ThumbnailGeneratorJob(picture, self)
                JobManager().EnqueueContext(tgj)
                return self.thumbDefault
            elif pilImg is self._inScalingQueue:
                return self.thumbDefault
            else:
                wxImg = wx.Image(PILBackend.ImageToStream(pilImg), wx.BITMAP_TYPE_JPEG)
                self._wxBmpCache[key] = wxImg.ConvertToBitmap()
        return self._wxBmpCache[key]


class ThumbnailGeneratorJob(Job):

    def __init__(self, pic, imgCache):
        Job.__init__(self, groupId="scale" )
        self.pic = pic
        self.imgCache = imgCache
        self.pilImg = None

    def Begin(self):
        self.pilImg = PILBackend.GetThumbnail(self.pic, self.imgCache.thumbSize)

    def Done(self):
        self.imgCache.RegisterPicture(self.pic, self.pilImg)
        if self.imgCache.win:
            evt = ThumbnailReadyEvent(self.pic)
            wx.PostEvent(self.imgCache.win, evt)


_EVT_THUMB_READY_TYPE = wx.NewEventType()
EVT_THUMB_READY = wx.PyEventBinder(_EVT_THUMB_READY_TYPE, 1)


class ThumbnailReadyEvent(wx.PyEvent):

    def __init__(self, pic):
        wx.PyEvent.__init__(self, eventType=_EVT_THUMB_READY_TYPE)
        self.__pic = pic

    def GetPicture(self):
        return self.__pic
