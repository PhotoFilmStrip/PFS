# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2018 Jens Goepfert
#

import gi
gi.require_version('Notify', '0.7')

from gi.repository import GdkPixbuf, Gio, GLib, Notify

from photofilmstrip import Constants
from photofilmstrip.lib.jobimpl.IVisualJobManager import IVisualJobManager
from photofilmstrip.lib.jobimpl.JobManager import JobManager
from photofilmstrip.res.images import ICON_16
from photofilmstrip.ux.Ux import UxAdapter


class UxGnome(UxAdapter, IVisualJobManager):

    def __init__(self):
        JobManager().AddVisual(self)

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
        notification.add_action("action", _(u'Play video'), lambda: None)
        notification.show()

    def RemoveJob(self, job):
        if job.GetGroupId() != "render":
            return
        if not job.IsAborted():
            self.ShowNotification(
                _("Slideshow created!"), job.GetName(), job.GetOutputFile())


def ux_init():
    return UxGnome()
