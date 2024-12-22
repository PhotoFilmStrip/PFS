# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2018 Jens Goepfert
#

import wx

from photofilmstrip.gui.Art import Art
from photofilmstrip.gui.PnlPfsProject import (
    PnlPfsProject, ID_PIC_IMPORT, ID_MUSIC, ID_RENDER_FILMSTRIP)
from photofilmstrip.gui.DlgDuration import DlgDuration
from photofilmstrip.gui.DlgPicDurationByAudio import DlgPicDurationByAudio
from photofilmstrip.gui.helper import CreateMenuItem
from photofilmstrip.gui.ImageSectionEditor import ImageProxy


[ID_PROJECT_PROPS,
 ID_PIC_DURATION_BY_AUDIO,
] = [wx.NewId() for __ in range(2)]


class PnlSlideshow(PnlPfsProject):

    def _GetEditorName(self):
        return _("Slideshow")

    def AddMenuFileActions(self, menu):
        PnlPfsProject.AddMenuFileActions(self, menu)
        CreateMenuItem(menu, ID_PROJECT_PROPS,
                       _("&Properties"),
                       Art.GetBitmapBundle('PFS_PROPERTIES', wx.ART_MENU))
        return True

    def AddToolBarActions(self, toolBar):
        toolBar.AddTool(ID_PIC_IMPORT, '',
                          Art.GetBitmapBundle('PFS_IMPORT_PICTURES', wx.ART_TOOLBAR),
                          Art.GetBitmapBundle('PFS_IMPORT_PICTURES_D', wx.ART_TOOLBAR),
                          wx.ITEM_NORMAL,
                          _("Import Pictures"),
                          _("Import Pictures"),
                          None)
        toolBar.AddSeparator()
        toolBar.AddTool(ID_MUSIC, '',
                          Art.GetBitmapBundle('PFS_MUSIC', wx.ART_TOOLBAR),
                          wx.NullBitmap,
                          wx.ITEM_NORMAL,
                          _("Configure music"),
                          _("Configure music"),
                          None)
        toolBar.AddTool(ID_PIC_DURATION_BY_AUDIO, '',
                          Art.GetBitmapBundle('PFS_MUSIC_DURATION', wx.ART_TOOLBAR),
                          wx.NullBitmap,
                          wx.ITEM_NORMAL,
                          _("Adjust picture durations"),
                          _("Adjust picture durations"),
                          None)
        toolBar.AddSeparator()
        toolBar.AddTool(ID_RENDER_FILMSTRIP, '',
                          Art.GetBitmapBundle('PFS_RENDER', wx.ART_TOOLBAR),
                          Art.GetBitmapBundle('PFS_RENDER_D', wx.ART_TOOLBAR),
                          wx.ITEM_NORMAL,
                          _("Render filmstrip"),
                          _("Render filmstrip"),
                          None)

    def ConnectEvents(self, evtHandler):
        PnlPfsProject.ConnectEvents(self, evtHandler)
        evtHandler.Bind(wx.EVT_MENU, self.OnProperties, id=ID_PROJECT_PROPS)
        evtHandler.Bind(wx.EVT_MENU, self.OnPicDurationByAudio, id=ID_PIC_DURATION_BY_AUDIO)
        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectReady, id=ID_PIC_DURATION_BY_AUDIO)

    def DisconnEvents(self, evtHandler):
        PnlPfsProject.DisconnEvents(self, evtHandler)
        for wId in [ID_PIC_DURATION_BY_AUDIO]:
            evtHandler.Disconnect(wId)

    def GetStatusText(self, index):
        project = self.GetProject()

        imgCount = len(project.GetPictures())
        totalTime = project.GetDuration(False)
        if totalTime == -1:
            # TODO: calc from audio files
            totalTime = 0
        elif totalTime is None:
            totalTime = project.GetDuration(True)

        if index == 0:
            return "%s: %d" % (_("Images"), imgCount)

        elif index == 1:
            minutes = totalTime // 60
            seconds = totalTime % 60
            return "%s: %02d:%02d" % (_("Duration"),
                                      minutes,
                                      seconds)
        else:
            return ""

    def OnStatusBarClick(self, index):
        if index == 1:
            self.OnProperties(None)

    def OnProperties(self, event):  # pylint: disable=unused-argument
        dlg = DlgDuration(self, self.GetProject())
        dlg.ShowModal()
        dlg.Destroy()

    def OnPicDurationByAudio(self, event):  # pylint: disable=unused-argument
        DlgPicDurationByAudio.Interact(self, self.GetProject())

    def _InitImageProxy(self):
        self.imgProxyLeft = self.imgProxyRight = ImageProxy()
        self.imgProxyLeft.AddObserver(self.bitmapLeft)
        self.imgProxyRight.AddObserver(self.bitmapRight)

        self.bitmapLeft.SetImgProxy(self.imgProxyLeft)
        self.bitmapRight.SetImgProxy(self.imgProxyRight)

    def _OnPicsSelectionChanged(self, selItems, selPics):
        if selPics:
#             assert self.imgProxyLeft is self.imgProxyRight
            self.imgProxyLeft.SetPicture(selPics[0])
            self.imgProxyRight.SetPicture(selPics[0])

            self._CheckAndSetLock(selPics[0])
            self.bitmapLeft.SetSection(wx.Rect(*selPics[0].GetStartRect()))
            self.bitmapRight.SetSection(wx.Rect(*selPics[0].GetTargetRect()))
