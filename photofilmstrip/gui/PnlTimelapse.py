# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#
import wx

from photofilmstrip.core.PicturePattern import PicturePattern

from photofilmstrip.gui.Art import Art
from photofilmstrip.gui.ImageSectionEditor import ImageProxy
from photofilmstrip.gui.PnlPfsProject import (
    PnlPfsProject, ID_PIC_IMPORT, ID_MUSIC, ID_RENDER_FILMSTRIP)


class PnlTimelapse(PnlPfsProject):

    def _GetEditorName(self):
        return _("Timelapse")

    def AddToolBarActions(self, toolBar):
        toolBar.AddTool(ID_PIC_IMPORT, "",
                        Art.GetBitmapBundle('PFS_IMPORT_PICTURES', wx.ART_TOOLBAR),
                        Art.GetBitmapBundle('PFS_IMPORT_PICTURES_D', wx.ART_TOOLBAR),
                        wx.ITEM_NORMAL,
                        _("Import Pictures"),
                        _("Import Pictures"),
                        None)
        toolBar.AddSeparator()
        toolBar.AddTool(ID_MUSIC, "",
                        Art.GetBitmapBundle('PFS_MUSIC', wx.ART_TOOLBAR),
                        wx.NullBitmap,
                        wx.ITEM_NORMAL,
                        _("Configure music"),
                        _("Configure music"),
                        None)
        toolBar.AddSeparator()
        toolBar.AddTool(ID_RENDER_FILMSTRIP, "",
                        Art.GetBitmapBundle('PFS_RENDER', wx.ART_TOOLBAR),
                        Art.GetBitmapBundle('PFS_RENDER_D', wx.ART_TOOLBAR),
                        wx.ITEM_NORMAL,
                        _("Render filmstrip"),
                        _("Render filmstrip"),
                        None)

    def GetStatusText(self, index):
        project = self.GetProject()

        try:
            imgCount, frameCount = self.__CalcDuration()
        except ValueError as err:
            if index == 0:
                return str(err)
            else:
                return ""

        totalTime = project.GetDuration(False)
        if totalTime == -1:
            # TODO: calc from audio files
            totalTime = 0
        elif totalTime is None:
            pass  # totalTime = project.GetDuration(True)
        else:
            assert True, "totalTime is invalid"

        if index == 0:
            return "%s: %d" % (_("Images"), imgCount)

        elif index == 1:
            return "%s: %d" % (_("Frames"), frameCount)
        else:
            return ""

    def __CalcDuration(self):
        pics = self.GetProject().GetPictures()
        idxPic = 0
        imgCount = 0
        frameCount = 0
        while idxPic < len(pics) - 1:
            pic = pics[idxPic]
            picPattern = PicturePattern.Create(pic.GetFilename())
            assert picPattern.IsOk()

            picNum = picPattern.num

            # get number from next pic
            nextPic = pics[idxPic + 1]
            nextPicPattern = PicturePattern.Create(nextPic.GetFilename())
            assert nextPicPattern.IsOk()

            picCount = nextPicPattern.num - picNum
            if picCount < 0:
                raise ValueError(_("The picture counter is not "
                                   "increasing: %s") % nextPic.GetFilename())

            picDur = int(pic.GetDuration())
            transDur = int(pic.GetTransitionDuration())

            imgCount += picCount
            frameCount += (picCount * (picDur + transDur))

            idxPic += 1

        return imgCount, frameCount

    def _CheckImportedPic(self, path):
        picPattern = PicturePattern.Create(path)
        if not picPattern.IsOk():
            dlgErr = wx.MessageDialog(
                self,
                _("Filename '%s' does not match a number pattern "
                  "which is necessary for a time lapse slide "
                  "show!") % path,
                _("Error"),
                wx.OK | wx.ICON_ERROR)
            dlgErr.ShowModal()
            dlgErr.Destroy()
            return False
        else:
            return True

    def _InitImageProxy(self):
        self.imgProxyLeft = ImageProxy(self.__imageCache)
        self.imgProxyLeft.AddObserver(self.bitmapLeft)
        self.imgProxyRight = ImageProxy(self.__imageCache)
        self.imgProxyRight.AddObserver(self.bitmapRight)

        self.bitmapLeft.SetImgProxy(self.imgProxyLeft)
        self.bitmapRight.SetImgProxy(self.imgProxyRight)

    def _OnPicsSelectionChanged(self, selItems, selPics):
        if selItems:
            selIdx = selItems[0]
            selPic = self.lvPics.GetPicture(selIdx)
            nextPic = self.lvPics.GetPicture(selIdx + 1)
            self._CheckAndSetLock(selPic)

            self.imgProxyLeft.SetPicture(selPic)
            self.bitmapLeft.SetSection(wx.Rect(*selPic.GetStartRect()))
            if nextPic:
                self.imgProxyRight.SetPicture(nextPic)
                self.bitmapRight.SetSection(wx.Rect(*nextPic.GetStartRect()))
                self.bitmapRight.Enable(True)
            else:
                self.bitmapRight.Enable(False)
