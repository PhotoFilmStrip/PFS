# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2018 Jens Goepfert
#

import wx

from photofilmstrip.gui.Art import Art
from photofilmstrip.gui.PnlPfsProject import (
    PnlPfsProject, ID_PIC_IMPORT, ID_MUSIC, ID_RENDER_FILMSTRIP,
    ID_PIC_SHUFFLE, ID_PIC_SELECT_ALL)
from photofilmstrip.gui.DlgSlideshowProperties import DlgSlideshowProperties
from photofilmstrip.gui.DlgPicDurationByAudio import DlgPicDurationByAudio
from photofilmstrip.gui.DlgPreview import DlgPreview
from photofilmstrip.gui.helper import CreateMenuItem
from photofilmstrip.gui.ImageSectionEditor import ImageProxy

[ID_PROJECT_PROPS,
 ID_PIC_DURATION_BY_AUDIO,
 ID_PREVIEW,
] = [wx.NewIdRef() for __ in range(3)]


class PnlSlideshow(PnlPfsProject):

    def _GetEditorName(self):
        return _("Slideshow")

    def AddMenuFileActions(self, menu):
        PnlPfsProject.AddMenuFileActions(self, menu)
        CreateMenuItem(menu, ID_PROJECT_PROPS,
                       _("&Properties"),
                       Art.GetBitmapBundle('PFS_PROPERTIES', wx.ART_MENU))
        return True

    def AddMenuEditActions(self, menu):
        PnlPfsProject.AddMenuEditActions(self, menu)
        menu.AppendSeparator()
        CreateMenuItem(menu, ID_PIC_SELECT_ALL,
                       _("Select &All") + "\tCtrl+A",
                       Art.GetBitmapBundle('PFS_FILMSTRIP', wx.ART_MENU),
                       wx.NullBitmap)
        CreateMenuItem(menu, ID_PIC_SHUFFLE,
                       _("&Shuffle Pictures") + "\tAlt+S",
                       Art.GetBitmapBundle('PFS_MOTION_RANDOM', wx.ART_MENU),
                       Art.GetBitmapBundle('PFS_MOTION_RANDOM_D', wx.ART_MENU))
        menu.AppendSeparator()
        CreateMenuItem(menu, ID_PREVIEW,
                       _("&Quick Preview") + "\tAlt+Q",
                       Art.GetBitmapBundle('PFS_PLAY', wx.ART_MENU),
                       wx.NullBitmap)
        return True

    def AddToolBarActions(self, toolBar):
        toolBar.AddTool(ID_PIC_IMPORT, '',
                          Art.GetBitmapBundle('PFS_IMPORT_PICTURES', wx.ART_TOOLBAR),
                          Art.GetBitmapBundle('PFS_IMPORT_PICTURES_D', wx.ART_TOOLBAR),
                          wx.ITEM_NORMAL,
                          _("Import Pictures"),
                          _("Import Pictures"),
                          None)
        toolBar.AddTool(ID_PIC_SELECT_ALL, '',
                          Art.GetBitmapBundle('PFS_FILMSTRIP', wx.ART_TOOLBAR),
                          wx.NullBitmap,
                          wx.ITEM_NORMAL,
                          _("Select All"),
                          _("Select All"),
                          None)
        toolBar.AddTool(ID_PIC_SHUFFLE, '',
                          Art.GetBitmapBundle('PFS_MOTION_RANDOM', wx.ART_TOOLBAR),
                          Art.GetBitmapBundle('PFS_MOTION_RANDOM_D', wx.ART_TOOLBAR),
                          wx.ITEM_NORMAL,
                          _("Shuffle Pictures"),
                          _("Shuffle Pictures"),
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
        toolBar.AddTool(ID_PREVIEW, '',
                          Art.GetBitmapBundle('PFS_PLAY', wx.ART_TOOLBAR),
                          wx.NullBitmap,
                          wx.ITEM_NORMAL,
                          _("Quick Preview"),
                          _("Quick Preview (Alt+Q)"),
                          None)

    def ConnectEvents(self, evtHandler):
        PnlPfsProject.ConnectEvents(self, evtHandler)
        evtHandler.Bind(wx.EVT_MENU, self.OnProperties, id=ID_PROJECT_PROPS)
        evtHandler.Bind(wx.EVT_MENU, self.OnPicDurationByAudio, id=ID_PIC_DURATION_BY_AUDIO)
        evtHandler.Bind(wx.EVT_MENU, self.OnCmdSelectAllButton, id=ID_PIC_SELECT_ALL)
        evtHandler.Bind(wx.EVT_MENU, self.OnCmdShuffleButton, id=ID_PIC_SHUFFLE)
        evtHandler.Bind(wx.EVT_MENU, self.OnPreview, id=ID_PREVIEW)
        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectReady, id=ID_PIC_DURATION_BY_AUDIO)
        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectReady, id=ID_PIC_SELECT_ALL)
        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectReady, id=ID_PIC_SHUFFLE)
        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectReady, id=ID_PREVIEW)
        # Bind Delete key to remove selected pictures - bind to lvPics which gets focus
        self.lvPics.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

    def DisconnEvents(self, evtHandler):
        PnlPfsProject.DisconnEvents(self, evtHandler)
        for wId in [ID_PROJECT_PROPS, ID_PIC_DURATION_BY_AUDIO, ID_PIC_SELECT_ALL, ID_PIC_SHUFFLE, ID_PREVIEW]:
            while evtHandler.Disconnect(wId):
                pass
        try:
            self.lvPics.Unbind(wx.EVT_KEY_DOWN)
        except Exception:
            pass

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
        elif index == 2:
            selCount = len(self.lvPics.GetSelected())
            return "%s: %d" % (_("Selected"), selCount)
        else:
            return ""

    def OnStatusBarClick(self, index):
        if index == 1:
            self.OnProperties(None)

    def OnProperties(self, event):  # pylint: disable=unused-argument
        dlg = DlgSlideshowProperties(self, self.GetProject())
        dlg.ShowModal()
        dlg.Destroy()

    def OnPicDurationByAudio(self, event):  # pylint: disable=unused-argument
        DlgPicDurationByAudio.Interact(self, self.GetProject())

    def OnKeyDown(self, event):
        """Handle Delete key to remove selected pictures."""
        if event.GetKeyCode() == wx.WXK_DELETE:
            # Delete key pressed - remove selected pictures
            self.OnCmdRemoveButton(None)
        event.Skip()

    def OnPreview(self, event):  # pylint: disable=unused-argument
        project = self.GetProject()
        if project:
            # Get selected pictures
            selectedIndices = self.lvPics.GetSelected()
            if len(selectedIndices) > 0:
                selectedPics = [project.GetPictures()[i] for i in selectedIndices]
            else:
                # If nothing selected, use all pictures
                selectedPics = project.GetPictures()
            
            if len(selectedPics) > 0:
                aspectRatio = project.GetAspect()
                # Create preview dialog - it will be hidden but manage the job queue
                dlg = DlgPreview(self, project, aspectRatio, selectedPics)
                # Dialog is hidden, but it will show in job queue and close when done

    def _InitImageProxy(self):
        self.imgProxyLeft = self.imgProxyRight = ImageProxy(self._imageCache)
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
