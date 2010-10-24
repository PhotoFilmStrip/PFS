#Boa:FramePanel:PnlDlgHeader
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


[wxID_PNLDLGHEADER, wxID_PNLDLGHEADERBMPLOGO, wxID_PNLDLGHEADERPNLHEADER, 
 wxID_PNLDLGHEADERSLHDR, wxID_PNLDLGHEADERSTERRMSG, wxID_PNLDLGHEADERSTHEADER, 
] = [wx.NewId() for _init_ctrls in range(6)]


class PnlDlgHeader(wx.Panel):
    def _init_coll_szHeaderText_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stHeader, 0, border=0, flag=0)
        parent.AddWindow(self.stErrMsg, 0, border=4, flag=wx.TOP)

    def _init_coll_szMain_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.pnlHeader, 0, border=0, flag=wx.EXPAND)
        parent.AddWindow(self.slHdr, 0, border=0, flag=wx.EXPAND)

    def _init_coll_szHeader_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.bmpLogo, 0, border=8,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL)
        parent.AddSizer(self.szHeaderText, 0, border=8,
              flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

    def _init_sizers(self):
        # generated method, don't edit
        self.szMain = wx.BoxSizer(orient=wx.VERTICAL)

        self.szHeader = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.szHeaderText = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_szMain_Items(self.szMain)
        self._init_coll_szHeader_Items(self.szHeader)
        self._init_coll_szHeaderText_Items(self.szHeaderText)

        self.SetSizer(self.szMain)
        self.pnlHeader.SetSizer(self.szHeader)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Panel.__init__(self, id=wxID_PNLDLGHEADER, name=u'PnlDlgHeader',
              parent=prnt, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.TAB_TRAVERSAL)

        self.pnlHeader = wx.Panel(id=wxID_PNLDLGHEADERPNLHEADER,
              name=u'pnlHeader', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.TAB_TRAVERSAL)
        self.pnlHeader.SetBackgroundColour(wx.Colour(255, 255, 255))

        self.bmpLogo = wx.StaticBitmap(bitmap=wx.ArtProvider.GetBitmap('wxART_GO_HOME',
              wx.ART_TOOLBAR, (32, 32)), id=wxID_PNLDLGHEADERBMPLOGO,
              name=u'bmpLogo', parent=self.pnlHeader, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.stHeader = wx.StaticText(id=wxID_PNLDLGHEADERSTHEADER,
              label=_(u''), name=u'stHeader', parent=self.pnlHeader,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.stErrMsg = wx.StaticText(id=wxID_PNLDLGHEADERSTERRMSG, label=u'',
              name=u'stErrMsg', parent=self.pnlHeader, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)
        self.stErrMsg.Show(False)
        self.stErrMsg.SetForegroundColour(wx.Colour(255, 0, 0))

        self.slHdr = wx.StaticLine(id=wxID_PNLDLGHEADERSLHDR, name=u'slHdr',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self._init_sizers()

    def __init__(self, parent, id, pos, size, style, name):
        self._init_ctrls(parent)

        font = self.stHeader.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.stHeader.SetFont(font)
                
    def SetErrorMessage(self, msg):
        if msg:
            self.stErrMsg.SetLabel(msg)
            self.stErrMsg.Show(True)
        else:
            self.stErrMsg.Show(False)
        self.Layout()
        
    def SetTitle(self, title):
        self.stHeader.SetLabel(title)
        
    def SetBitmap(self, bmp):
        self.bmpLogo.SetBitmap(bmp)
