# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2010 Jens Goepfert
#

import wx


class PnlAddPics(wx.Panel):

    def _InitSizers(self):
        szCentered = wx.BoxSizer(wx.VERTICAL)
        szCentered.Add(self.stTitle, 0, border=4,
              flag=wx.EXPAND | wx.ALL)
        szCentered.AddSpacer(8)
        szCentered.Add(self.stInfo, 0, border=4,
              flag=wx.EXPAND | wx.ALL)
        szCentered.AddSpacer(8)
        szCentered.Add(self.cmdBrowse, 0, border=4,
              flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL)

        szMain = wx.BoxSizer(wx.HORIZONTAL)
        szMain.Add(szCentered, flag=wx.ALIGN_CENTER_VERTICAL)

        self.SetSizer(szMain)

    def __init__(self, parent, id=wx.ID_ANY,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0, name='PnlAddPics'):
        wx.Panel.__init__(self, id=id, name=name, parent=parent,
                          pos=pos, size=size, style=style)
        self.SetClientSize(wx.Size(400, 250))

        self.stTitle = wx.StaticText(
            self, wx.ID_ANY, name=u'stTitle', style=wx.ALIGN_CENTRE)

        self.stInfo = wx.StaticText(
            self, wx.ID_ANY, name=u'stInfo', style=wx.ALIGN_CENTRE)

        self.cmdBrowse = wx.BitmapButton(
            self, wx.ID_ANY, name=u'cmdBrowse',
            bitmap=wx.ArtProvider.GetBitmap('PFS_IMPORT_PICTURES_32'))

        font = self.stTitle.GetFont()
        font.SetWeight(wx.BOLD)
        self.stTitle.SetFont(font)

        self.stTitle.SetLabel(_(u"Welcome to PhotoFilmStrip"))
        self.stInfo.SetLabel(
            _(u"Drag some pictures onto this text or\n"
              u"click the button below\n"
              u"to add pictures to your new PhotoFilmStrip."))

        self._InitSizers()

    def GetButton(self):
        return self.cmdBrowse
