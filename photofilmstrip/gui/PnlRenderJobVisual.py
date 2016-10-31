#Boa:FramePanel:PnlJobVisual
# encoding: UTF-8

import wx

from photofilmstrip.action.WxAction import WxAction
from photofilmstrip.action.ActionPlayVideo import ActionPlayVideo
from photofilmstrip.action.ActionOpenFolder import ActionOpenFolder
from photofilmstrip.lib.jobimpl.PnlJobVisual import PnlJobVisual


class PnlRenderJobVisual(PnlJobVisual):

    def __init__(self, parent, pnlJobManager, jobContext):
        PnlJobVisual.__init__(self, parent, pnlJobManager, jobContext)
        
        ms = wx.ArtProvider.GetSizeHint(wx.ART_MENU)
        ts = wx.ArtProvider.GetSizeHint(wx.ART_TOOLBAR)

        self._actPlay = WxAction(
                _(u"Play video"),
                self._PlayVideo,
                bmp={wx.ART_MENU: wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, 
                                                           wx.ART_MENU, 
                                                           ms),
                     wx.ART_TOOLBAR: wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, 
                                                              wx.ART_TOOLBAR, 
                                                              ts)}
        )
        self._actOpenFldr = WxAction(
                    _(u"Open folder"),
                self._OpenFolder,
                bmp={wx.ART_MENU: wx.ArtProvider.GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_MENU, ms),
                     wx.ART_TOOLBAR: wx.ArtProvider.GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_TOOLBAR, ts)}
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
        ActionPlayVideo(self.jobContext.GetOutputPath()).Execute()
        
    def _OpenFolder(self):
        ActionOpenFolder(self.jobContext.GetOutputPath()).Execute()
