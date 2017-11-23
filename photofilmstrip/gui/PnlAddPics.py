#Boa:FramePanel:PnlAddPics
# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2010 Jens Goepfert
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

import wx

[wxID_PNLADDPICS, wxID_PNLADDPICSCMDBROWSE, wxID_PNLADDPICSSTINFO,
 wxID_PNLADDPICSSTTITLE,
] = [wx.NewId() for _init_ctrls in range(4)]

class PnlAddPics(wx.Panel):
    def _init_coll_szMain_Items(self, parent):
        # generated method, don't edit

        parent.AddSizer(self.szCentered, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)

    def _init_coll_szCentered_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stTitle, 0, border=4,
              flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL)
        parent.AddSpacer(wx.Size(8, 16), border=0, flag=0)
        parent.AddWindow(self.stInfo, 0, border=4,
              flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.cmdBrowse, 0, border=4,
              flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL)

    def _init_sizers(self):
        # generated method, don't edit
        self.szCentered = wx.BoxSizer(orient=wx.VERTICAL)

        self.szMain = wx.BoxSizer(orient=wx.HORIZONTAL)

        self._init_coll_szCentered_Items(self.szCentered)
        self._init_coll_szMain_Items(self.szMain)

        self.SetSizer(self.szMain)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Panel.__init__(self, id=wxID_PNLADDPICS, name=u'PnlAddPics',
              parent=prnt, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.TAB_TRAVERSAL)
        self.SetClientSize(wx.Size(400, 250))

        self.stTitle = wx.StaticText(id=wxID_PNLADDPICSSTTITLE,
              label=u'staticText1', name=u'stTitle', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.stInfo = wx.StaticText(id=wxID_PNLADDPICSSTINFO,
              label=u'staticText1', name=u'stInfo', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.ALIGN_CENTRE)

        self.cmdBrowse = wx.BitmapButton(bitmap=wx.ArtProvider.GetBitmap('PFS_IMPORT_PICTURES_32'),
              id=wxID_PNLADDPICSCMDBROWSE,
              name=u'cmdBrowse', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.BU_AUTODRAW)

        self._init_sizers()

    def __init__(self, parent, id=wx.ID_ANY,
                 pos=wx.DefaultPosition, size=wx.DefaultSize,
                 style=0, name='panel'):
        self._init_ctrls(parent)

        font = self.stTitle.GetFont()
        font.SetWeight(wx.BOLD)
        self.stTitle.SetFont(font)

        self.stTitle.SetLabel(_(u"Welcome to PhotoFilmStrip"))
        self.stInfo.SetLabel(_(u"Drag some pictures onto this text or\nclick the button below\nto add pictures to your new PhotoFilmStrip."))

    def GetButton(self):
        return self.cmdBrowse
