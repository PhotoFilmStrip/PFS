# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2018 Jens Goepfert
#

import wx
from PIL import Image

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
 ID_PIC_REMOVE_DUPES,
 ID_PIC_SELECT_PREV,
 ID_PIC_SELECT_NEXT,
] = [wx.NewIdRef() for __ in range(6)]

# perceptual hash settings for duplicate detection
DUP_HASH_SIZE = 16
DUP_MAX_DISTANCE = 10  # max hamming distance of 256 bits to count as duplicate


def DHashFromPixels(pixels, hashSize=DUP_HASH_SIZE):
    """Difference hash (dHash) from grayscale pixels of a
    (hashSize+1) x hashSize image. Returns an int bitmask."""
    bits = 0
    for row in range(hashSize):
        for col in range(hashSize):
            bits = (bits << 1) | (1 if pixels[row * (hashSize + 1) + col + 1]
                                  > pixels[row * (hashSize + 1) + col] else 0)
    return bits


def CalcImageHash(filename, hashSize=DUP_HASH_SIZE):
    """Difference hash (dHash) of an image, robust against scaling and
    different file sizes. Returns an int bitmask or None if unreadable."""
    try:
        with Image.open(filename) as img:
            try:
                img.draft("L", (hashSize + 1, hashSize))
            except Exception:
                pass
            img = img.convert("L").resize((hashSize + 1, hashSize), Image.LANCZOS)
            pixels = list(img.getdata())
    except Exception:
        return None
    return DHashFromPixels(pixels, hashSize)


def HammingDistance(a, b):
    return bin(a ^ b).count("1")


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
        CreateMenuItem(menu, ID_PIC_SELECT_PREV,
                       _("Select &previous picture") + "\tAlt+Left",
                       Art.GetBitmapBundle('PFS_IMAGE_MOVING_LEFT', wx.ART_MENU),
                       wx.NullBitmap)
        CreateMenuItem(menu, ID_PIC_SELECT_NEXT,
                       _("Select &next picture") + "\tAlt+Right",
                       Art.GetBitmapBundle('PFS_IMAGE_MOVING_RIGHT', wx.ART_MENU),
                       wx.NullBitmap)
        CreateMenuItem(menu, ID_PIC_SHUFFLE,
                       _("&Shuffle Pictures") + "\tAlt+S",
                       Art.GetBitmapBundle('PFS_MOTION_RANDOM', wx.ART_MENU),
                       Art.GetBitmapBundle('PFS_MOTION_RANDOM_D', wx.ART_MENU))
        CreateMenuItem(menu, ID_PIC_REMOVE_DUPES,
                       _("Remove &duplicate pictures"),
                       Art.GetBitmapBundle('PFS_LIST_REMOVE', wx.ART_MENU),
                       wx.NullBitmap)
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
        toolBar.AddTool(ID_PIC_REMOVE_DUPES, '',
                          Art.GetBitmapBundle('PFS_LIST_REMOVE', wx.ART_TOOLBAR),
                          wx.NullBitmap,
                          wx.ITEM_NORMAL,
                          _("Remove duplicate pictures"),
                          _("Remove duplicate pictures (images that look the same)"),
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
        evtHandler.Bind(wx.EVT_MENU, self.OnCmdSelectPrev, id=ID_PIC_SELECT_PREV)
        evtHandler.Bind(wx.EVT_MENU, self.OnCmdSelectNext, id=ID_PIC_SELECT_NEXT)
        evtHandler.Bind(wx.EVT_MENU, self.OnCmdShuffleButton, id=ID_PIC_SHUFFLE)
        evtHandler.Bind(wx.EVT_MENU, self.OnCmdRemoveDuplicates, id=ID_PIC_REMOVE_DUPES)
        evtHandler.Bind(wx.EVT_MENU, self.OnPreview, id=ID_PREVIEW)
        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectReady, id=ID_PIC_DURATION_BY_AUDIO)
        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectReady, id=ID_PIC_SELECT_ALL)
        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectReady, id=ID_PIC_SELECT_PREV)
        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectReady, id=ID_PIC_SELECT_NEXT)
        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectReady, id=ID_PIC_SHUFFLE)
        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectReady, id=ID_PIC_REMOVE_DUPES)
        evtHandler.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectReady, id=ID_PREVIEW)
        # Bind Delete key to remove selected pictures - bind to lvPics which gets focus
        self.lvPics.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

    def DisconnEvents(self, evtHandler):
        PnlPfsProject.DisconnEvents(self, evtHandler)
        for wId in [ID_PROJECT_PROPS, ID_PIC_DURATION_BY_AUDIO, ID_PIC_SELECT_ALL,
                    ID_PIC_SELECT_PREV, ID_PIC_SELECT_NEXT, ID_PIC_SHUFFLE,
                    ID_PIC_REMOVE_DUPES, ID_PREVIEW]:
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

    def OnCmdSelectPrev(self, event):  # pylint: disable=unused-argument
        sel = self.lvPics.GetSelected()
        if sel and sel[0] > 0:
            self.lvPics.Select(sel[0] - 1)
            self.lvPics.EnsureVisible(sel[0] - 1)

    def OnCmdSelectNext(self, event):  # pylint: disable=unused-argument
        sel = self.lvPics.GetSelected()
        if sel and sel[0] < self.lvPics.GetItemCount() - 1:
            self.lvPics.Select(sel[0] + 1)
            self.lvPics.EnsureVisible(sel[0] + 1)

    def OnPreview(self, event):  # pylint: disable=unused-argument
        project = self.GetProject()
        if project:
            # Preview the selected pictures (in strip order); if nothing is
            # selected, preview all pictures
            pics = self.lvPics.GetPictures()
            selIdxs = sorted(self.lvPics.GetSelected())
            if selIdxs:
                selectedPics = [pics[i] for i in selIdxs if i < len(pics)]
            else:
                selectedPics = pics

            if len(selectedPics) > 0:
                aspectRatio = project.GetAspect()
                # Create preview dialog - it will be hidden but manage the job queue
                dlg = DlgPreview(self, project, aspectRatio, selectedPics)
                # Dialog is hidden, but it will show in job queue and close when done

    def OnCmdRemoveDuplicates(self, event):  # pylint: disable=unused-argument
        import os
        pics = self.lvPics.GetPictures()
        if len(pics) < 2:
            return

        progress = wx.ProgressDialog(_("Remove duplicate pictures"),
                                     _("Analyzing pictures..."),
                                     maximum=len(pics), parent=self,
                                     style=wx.PD_APP_MODAL | wx.PD_CAN_ABORT
                                     | wx.PD_AUTO_HIDE)
        keptHashes = []
        dupeIndices = []
        cancelled = False
        try:
            for idx, pic in enumerate(pics):
                keepGoing, _skip = progress.Update(idx, os.path.basename(pic.GetFilename()))
                if not keepGoing:
                    cancelled = True
                    break
                imgHash = CalcImageHash(pic.GetFilename())
                if imgHash is None:
                    continue
                if any(k is not None and HammingDistance(imgHash, k) <= DUP_MAX_DISTANCE
                       for k in keptHashes):
                    dupeIndices.append(idx)
                else:
                    keptHashes.append(imgHash)
        finally:
            progress.Destroy()

        if cancelled:
            return

        # remove duplicates starting at the end so indices stay valid
        for idx in sorted(dupeIndices, reverse=True):
            self.lvPics.DeleteItem(idx)

        if dupeIndices:
            msg = _("Removed %d duplicate picture(s).") % len(dupeIndices)
        else:
            msg = _("No duplicate pictures found.")
        wx.MessageBox(msg, _("Remove duplicate pictures"),
                      wx.OK | wx.ICON_INFORMATION, self)

        self.Layout()

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
