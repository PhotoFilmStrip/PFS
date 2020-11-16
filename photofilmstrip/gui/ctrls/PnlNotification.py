# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2018 Jens Goepfert
#

import wx


class PnlNotification(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.bmp = wx.StaticBitmap(
            self, bitmap=wx.ArtProvider.GetBitmap("PFS_ALERT", size=wx.Size(24, 24)))
        self.msg = wx.StaticText(self, wx.ID_ANY)

        self.timer = wx.Timer(self)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(self.bmp, 0, border=8, flag=wx.ALL)
        sizer.Add(self.msg, 1, border=8, flag=wx.TOP | wx.BOTTOM | wx.RIGHT | wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(sizer)

        self.notifications = {}

        self.Bind(wx.EVT_TIMER, self.__OnTimer)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.__OnDestroy, id=self.GetId())

        self.timer.Start(500)
        self.SetBackgroundColour(wx.Colour(254, 183, 67))

    def __OnDestroy(self, event):  # pylint: disable=unused-argument
        if self.timer.IsRunning():
            self.timer.Stop()
        self.timer = None

    def __OnTimer(self, event):  # pylint: disable=unused-argument
        for msg, timeout in list(self.notifications.items()):
            if timeout is not None:
                timeout -= 500
                self.notifications[msg] = timeout

                if timeout < 0:
                    self.notifications.pop(msg)
                    self.__UpdateMsg()

    def __UpdateMsg(self):
        label = "\n".join(self.notifications.keys())
        self.msg.SetLabel(label)
        self.Show(bool(label))
        self.GetParent().Layout()

    def AddNotification(self, msg, timeout=None):
        if msg not in self.notifications:
            self.notifications[msg] = timeout
            self.__UpdateMsg()
        else:
            self.notifications[msg] = timeout

    def ClearNotifications(self):
        hasDropped = False
        for msg, timeout in list(self.notifications.items()):
            if timeout is None:
                self.notifications.pop(msg)
                hasDropped = True

        if hasDropped:
            self.__UpdateMsg()
