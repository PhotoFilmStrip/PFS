# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2018 Jens Goepfert
#

import wx

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
        return _(u"Slideshow")

    def AddMenuFileActions(self, menu):
        PnlPfsProject.AddMenuFileActions(self, menu)
        CreateMenuItem(menu, ID_PROJECT_PROPS,
                       _(u"&Properties"),
                       wx.ArtProvider.GetBitmap('PFS_PROPERTIES_16'))
        return True

    def AddToolBarActions(self, toolBar):
        toolBar.AddTool(ID_PIC_IMPORT, '',
                          wx.ArtProvider.GetBitmap('PFS_IMPORT_PICTURES_24'),
                          wx.ArtProvider.GetBitmap('PFS_IMPORT_PICTURES_D_24'),
                          wx.ITEM_NORMAL,
                          _(u'Import Pictures'),
                          _(u'Import Pictures'),
                          None)
        toolBar.AddSeparator()
        toolBar.AddTool(ID_MUSIC, '',
                          wx.ArtProvider.GetBitmap('PFS_MUSIC_24'),
                          wx.NullBitmap,
                          wx.ITEM_NORMAL,
                          _(u'Configure music'),
                          _(u'Configure music'),
                          None)
        toolBar.AddTool(ID_PIC_DURATION_BY_AUDIO, '',
                          wx.ArtProvider.GetBitmap('PFS_MUSIC_DURATION_24'),
                          wx.NullBitmap,
                          wx.ITEM_NORMAL,
                          _(u'Adjust picture durations'),
                          _(u'Adjust picture durations'),
                          None)
        toolBar.AddSeparator()
        toolBar.AddTool(ID_RENDER_FILMSTRIP, '',
                          wx.ArtProvider.GetBitmap('PFS_RENDER_24'),
                          wx.ArtProvider.GetBitmap('PFS_RENDER_D_24'),
                          wx.ITEM_NORMAL,
                          _(u'Render filmstrip'),
                          _(u'Render filmstrip'),
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
            return u"%s: %d" % (_(u"Images"), imgCount)

        elif index == 1:
            minutes = totalTime // 60
            seconds = totalTime % 60
            return u"%s: %02d:%02d" % (_(u"Duration"),
                                       minutes,
                                       seconds)
        else:
            return u""

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
