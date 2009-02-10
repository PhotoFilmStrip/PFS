#Boa:Dialog:DlgUpdateInfo

import wx
import wx.lib.hyperlink

from wx.lib.wordwrap import wordwrap


[wxID_DLGUPDATEINFO, wxID_DLGUPDATEINFOCMDCLOSE, 
 wxID_DLGUPDATEINFOHYPERLINKCTRL, wxID_DLGUPDATEINFOSTATICBITMAP, 
 wxID_DLGUPDATEINFOSTINFO, wxID_DLGUPDATEINFOSTVERSION, 
 wxID_DLGUPDATEINFOTCCHANGES, 
] = [wx.NewId() for _init_ctrls in range(7)]


class DlgUpdateInfo(wx.Dialog):
    def _init_coll_sizerMain_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.staticBitmap, 0, border=8,
              flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        parent.AddWindow(self.stVersion, 0, border=0,
              flag=wx.ALIGN_CENTER_HORIZONTAL)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.stInfo, 0, border=4, flag=wx.ALL)
        parent.AddWindow(self.tcChanges, 1, border=4, flag=wx.ALL | wx.EXPAND)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.hyperLinkCtrl, 0, border=0,
              flag=wx.ALIGN_CENTER_HORIZONTAL)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.cmdClose, 0, border=4,
              flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)

    def _init_sizers(self):
        # generated method, don't edit
        self.sizerMain = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_sizerMain_Items(self.sizerMain)

        self.SetSizer(self.sizerMain)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_DLGUPDATEINFO, name=u'DlgUpdateInfo',
              parent=prnt, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.DEFAULT_DIALOG_STYLE, title=_(u'New version available'))
        self.SetClientSize(wx.Size(400, 500))

        self.staticBitmap = wx.StaticBitmap(bitmap=wx.NullBitmap,
              id=wxID_DLGUPDATEINFOSTATICBITMAP, name=u'staticBitmap',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.stVersion = wx.StaticText(id=wxID_DLGUPDATEINFOSTVERSION,
              label=u'', name=u'stVersion', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.tcChanges = wx.TextCtrl(id=wxID_DLGUPDATEINFOTCCHANGES,
              name=u'tcChanges', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.TE_MULTILINE | wx.TE_READONLY,
              value=u'')

        self.cmdClose = wx.Button(id=wx.ID_OK, label=_(u'Close'), name=u'cmdClose',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.stInfo = wx.StaticText(id=wxID_DLGUPDATEINFOSTINFO,
              label='',
              name=u'stInfo', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.hyperLinkCtrl = wx.lib.hyperlink.HyperLinkCtrl(id=wxID_DLGUPDATEINFOHYPERLINKCTRL,
              label=_(u'Goto download site'), name=u'hyperLinkCtrl', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self._init_sizers()

    def __init__(self, parent, appVer, bmp, url, changes, info=None):
        self._init_ctrls(parent)

        font = self.stVersion.GetFont()
        font.SetWeight(wx.BOLD)
        font.SetPointSize(font.GetPointSize() * 2)
        self.stVersion.SetFont(font)
        self.stVersion.SetLabel(appVer)
        
        self.hyperLinkCtrl.SetURL(url)

        self.staticBitmap.SetBitmap(bmp)
        self.tcChanges.SetValue(changes)
        
        if info is None:
            info = _(u'A new version is available online. The following changes has been made:')
        self.stInfo.SetLabel(wordwrap(info, self.GetClientSizeTuple()[0], wx.ClientDC(self)))
        