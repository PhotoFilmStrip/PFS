#Boa:Dialog:DlgFinalize
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


import shutil

import wx

from photofilmstrip.gui.ctrls.PnlDlgHeader import PnlDlgHeader
from photofilmstrip.action.ActionPlayVideo import ActionPlayVideo
from photofilmstrip.action.ActionOpenFolder import ActionOpenFolder


[wxID_DLGFINALIZE, wxID_DLGFINALIZECBSENDERR, wxID_DLGFINALIZECMDCLOSE, 
 wxID_DLGFINALIZEPNLHDR, wxID_DLGFINALIZERB1, wxID_DLGFINALIZERB2, 
 wxID_DLGFINALIZERB3, wxID_DLGFINALIZERB4, wxID_DLGFINALIZESTNEXTACTION, 
] = [wx.NewId() for _init_ctrls in range(9)]


class DlgFinalize(wx.Dialog):
    
    _custom_classes = {"wx.Panel": ["PnlDlgHeader"]}
    
    def _init_coll_szMain_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.pnlHdr, 0, border=0, flag=wx.EXPAND)
        parent.AddWindow(self.stNextAction, 0, border=8, flag=wx.ALL)
        parent.AddSizer(self.szRadios, 0, border=24, flag=wx.LEFT)
        parent.AddWindow(self.cbSendErr, 0, border=8, flag=wx.ALL)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.cmdClose, 0, border=8,
              flag=wx.ALL | wx.ALIGN_RIGHT)

    def _init_coll_szRadios_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.rb1, 0, border=4, flag=wx.TOP | wx.BOTTOM)
        parent.AddWindow(self.rb2, 0, border=4, flag=wx.TOP | wx.BOTTOM)
        parent.AddWindow(self.rb3, 0, border=4, flag=wx.TOP | wx.BOTTOM)
        parent.AddWindow(self.rb4, 0, border=4, flag=wx.TOP | wx.BOTTOM)

    def _init_sizers(self):
        # generated method, don't edit
        self.szMain = wx.BoxSizer(orient=wx.VERTICAL)

        self.szRadios = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_szMain_Items(self.szMain)
        self._init_coll_szRadios_Items(self.szRadios)

        self.SetSizer(self.szMain)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_DLGFINALIZE, name=u'DlgFinalize',
              parent=prnt, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.DEFAULT_DIALOG_STYLE, title=_(u'Finalizing'))
        self.SetClientSize(wx.Size(400, 250))
        self.Bind(wx.EVT_CLOSE, self.OnDlgFinalizeClose)

        self.pnlHdr = PnlDlgHeader(id=wxID_DLGFINALIZEPNLHDR, name=u'pnlHdr',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.TAB_TRAVERSAL)

        self.stNextAction = wx.StaticText(id=wxID_DLGFINALIZESTNEXTACTION,
              label=_(u'Choose your next action:'), name=u'stNextAction',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.rb1 = wx.RadioButton(id=wxID_DLGFINALIZERB1,
              label=_(u'Play video'), name=u'rb1', parent=self, pos=wx.Point(-1,
              -1), size=wx.Size(-1, -1), style=0)
        self.rb1.SetValue(True)

        self.rb2 = wx.RadioButton(id=wxID_DLGFINALIZERB2,
              label=_(u'Open folder'), name=u'rb2', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.rb3 = wx.RadioButton(id=wxID_DLGFINALIZERB3,
              label=_(u'Delete unfinished result'), name=u'rb3', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.rb4 = wx.RadioButton(id=wxID_DLGFINALIZERB4,
              label=_(u'Do nothing'), name=u'rb4', parent=self, pos=wx.Point(-1,
              -1), size=wx.Size(-1, -1), style=0)

        self.cmdClose = wx.Button(id=wxID_DLGFINALIZECMDCLOSE,
              label=_(u'&Close'), name=u'cmdClose', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)
        self.cmdClose.Bind(wx.EVT_BUTTON, self.OnCmdCloseButton,
              id=wxID_DLGFINALIZECMDCLOSE)

        self.cbSendErr = wx.CheckBox(id=wxID_DLGFINALIZECBSENDERR,
              label=_(u'Show error again and send to developer.'),
              name=u'cbSendErr', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)
        self.cbSendErr.SetValue(True)
        self.cbSendErr.Show(False)

        self._init_sizers()

    def __init__(self, parent, outpath, wasAborted=False, errMsg=None):
        self._init_ctrls(parent)
        self.outpath = outpath
        self.errMsg = errMsg
        
        if wasAborted:
            msg = _(u"The rendering process was aborted.")
            self.pnlHdr.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_WARNING,
              wx.ART_TOOLBAR, (32, 32)))
            self.rb3.SetValue(True)
        
        elif errMsg:
            msg = _(u"The rendering process was interrupted.")
            self.pnlHdr.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_ERROR,
              wx.ART_TOOLBAR, (32, 32)))
            self.rb3.SetValue(True)
            self.rb1.Show(False)
            self.cbSendErr.Show(True)
            
            lines = errMsg.split("\n")
            errMsg = u"%s %s" % (lines[0], lines[-1])
        else:
            msg = _(u"The rendering process has been finished.")
            self.rb3.Show(False)
            
            self.pnlHdr.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_TICK_MARK,
              wx.ART_TOOLBAR, (32, 32)))
            
        self.pnlHdr.SetTitle(msg)
        self.pnlHdr.SetErrorMessage(errMsg)

        self.SetInitialSize(self.GetEffectiveMinSize())
        self.CentreOnParent()
        self.SetFocus()

    def OnCmdCloseButton(self, event):
        try:
            if self.rb1.GetValue():
                # Play video
                ActionPlayVideo(self.outpath).Execute()
            
            elif self.rb2.GetValue():
                # Open folder
                ActionOpenFolder(self.outpath).Execute()
            
            elif self.rb3.GetValue():
                # Delete unfinished
                shutil.rmtree(self.outpath, True)
            
            if self.cbSendErr.IsShown() and self.cbSendErr.GetValue():
                raise RuntimeError(self.errMsg)
            
        finally:
            self.Close()

    def OnDlgFinalizeClose(self, event):
        event.Skip()
