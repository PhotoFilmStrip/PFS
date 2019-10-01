# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#

import wx

from photofilmstrip.action.WxAction import WxAction
from photofilmstrip.action.ActionPlayVideo import ActionPlayVideo
from photofilmstrip.action.ActionOpenFolder import ActionOpenFolder
from photofilmstrip.lib.jobimpl.PnlJobVisual import PnlJobVisual


class PnlRenderJobVisual(PnlJobVisual):

    def __init__(self, parent, pnlJobManager, jobContext):
        PnlJobVisual.__init__(self, parent, pnlJobManager, jobContext)

        self._actPlay = WxAction(
                _(u"Play video"),
                self._PlayVideo,
                bmp={wx.ART_MENU: wx.ArtProvider.GetBitmap('PFS_PLAY_16'),
                     wx.ART_TOOLBAR: wx.ArtProvider.GetBitmap('PFS_PLAY_24')}
        )
        self._actOpenFldr = WxAction(
                    _(u"Open folder"),
                self._OpenFolder,
                bmp={wx.ART_MENU: wx.ArtProvider.GetBitmap('PFS_FOLDER_OPEN_16'),
                     wx.ART_TOOLBAR: wx.ArtProvider.GetBitmap('PFS_FOLDER_OPEN_24')}
        )

    def _OnMenuActions(self, menu):
        mitm = self._actPlay.ToMenu(self, menu)
        menu.Enable(mitm.GetId(), self.jobContext.IsDone())

        mitm = self._actOpenFldr.ToMenu(self, menu)
        menu.Enable(mitm.GetId(), not self.jobContext.IsIdle())

    def _OnSetupAction(self):
        if self.jobContext.IsDone():
            self.curAction = self._actPlay

    def _PlayVideo(self):
        ActionPlayVideo(self.jobContext.GetOutputFile()).Execute()

    def _OpenFolder(self):
        ActionOpenFolder(self.jobContext.GetOutputFile()).Execute()
