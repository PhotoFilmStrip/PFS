# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2018 Jens Goepfert
#

import gi
gi.require_version('Notify', '0.7')
gi.require_version('GdkPixbuf', '2.0')

from gi.repository import GdkPixbuf, Gio, GLib, Notify

from photofilmstrip import Constants
from photofilmstrip.lib.jobimpl.IVisualJobManager import IVisualJobManager
from photofilmstrip.lib.jobimpl.JobManager import JobManager
from photofilmstrip.res.images import ICON_16
from photofilmstrip.ux.Ux import UxAdapter


class UxGnome(UxAdapter, IVisualJobManager):

    def __init__(self):
        JobManager().AddVisual(self)
        self.notifications = {}
        self.notificationKey = 0

    def OnInit(self):
        Notify.init(Constants.APP_NAME)

    def RegisterJob(self, job):
        pass

    def ShowNotification(self, title, info, path):
        data = ICON_16.GetData()

        data_bytes = GLib.Bytes.new(list(data))
        data_stream = Gio.MemoryInputStream.new_from_bytes(data_bytes)

        icon = GdkPixbuf.Pixbuf.new_from_stream(data_stream)

        notification = Notify.Notification.new(title, info)
        notification.set_image_from_pixbuf(icon)
        notification.add_action(
            "default", _("Play video"),
            self._PlayVideoAction, self.notificationKey, path)
        notification.add_action(
            "play", _("Play video"),
            self._PlayVideoAction, self.notificationKey, path)
        notification.show()

        # keep reference to make callback work
        self.notifications[self.notificationKey] = notification
        self.notificationKey += 1

    def RemoveJob(self, job):
        if job.GetGroupId() != "render":
            return
        if not job.IsAborted():
            self.ShowNotification(
                _("Slideshow created!"), job.GetName(), job.GetOutputFile())

    def _PlayVideoAction(self, notifictn, name, notificationKey, path):  # @UnusedVariable pylint: disable=unused-argument
        from photofilmstrip.action.ActionPlayVideo import ActionPlayVideo
        ActionPlayVideo(path).Execute()
        del self.notifications[notificationKey]


def ux_init():
    return UxGnome()
