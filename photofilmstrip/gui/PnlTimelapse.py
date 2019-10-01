# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#
import wx

from photofilmstrip.core.PicturePattern import PicturePattern
from photofilmstrip.gui.ImageSectionEditor import ImageProxy
from photofilmstrip.gui.PnlPfsProject import (
    PnlPfsProject, ID_PIC_IMPORT, ID_MUSIC, ID_RENDER_FILMSTRIP)


class PnlTimelapse(PnlPfsProject):

    def _GetEditorName(self):
        return _(u"Timelapse")

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
        toolBar.AddSeparator()
        toolBar.AddTool(ID_RENDER_FILMSTRIP, '',
                          wx.ArtProvider.GetBitmap('PFS_RENDER_24'),
                          wx.ArtProvider.GetBitmap('PFS_RENDER_D_24'),
                          wx.ITEM_NORMAL,
                          _(u'Render filmstrip'),
                          _(u'Render filmstrip'),
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
            return u"%s: %d" % (_(u"Images"), imgCount)

        elif index == 1:
            return u"%s: %d" % (_(u"Frames"), frameCount)
        else:
            return u""

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
                raise ValueError(_(u"The picture counter is not "
                                   u"increasing: %s") % nextPic.GetFilename())

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
                _(u"Filename '%s' does not match a number pattern "
                  u"which is necessary for a time lapse slide "
                  u"show!") % path,
                _(u"Error"),
                wx.OK | wx.ICON_ERROR)
            dlgErr.ShowModal()
            dlgErr.Destroy()
            return False
        else:
            return True

    def _InitImageProxy(self):
        self.imgProxyLeft = ImageProxy()
        self.imgProxyLeft.AddObserver(self.bitmapLeft)
        self.imgProxyRight = ImageProxy()
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
