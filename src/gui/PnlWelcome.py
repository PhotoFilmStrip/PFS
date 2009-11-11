#Boa:FramePanel:PnlWelcome

import wx

[wxID_PNLWELCOME, wxID_PNLWELCOMECMDBROWSE, wxID_PNLWELCOMESTINFO, 
 wxID_PNLWELCOMESTTITLE, 
] = [wx.NewId() for _init_ctrls in range(4)]

class PnlWelcome(wx.Panel):
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
        wx.Panel.__init__(self, id=wxID_PNLWELCOME, name=u'PnlWelcome',
              parent=prnt, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.TAB_TRAVERSAL)

        self.stTitle = wx.StaticText(id=wxID_PNLWELCOMESTTITLE,
              label=u'staticText1', name=u'stTitle', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.stInfo = wx.StaticText(id=wxID_PNLWELCOMESTINFO,
              label=u'staticText1', name=u'stInfo', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.ALIGN_CENTRE)

        self.cmdBrowse = wx.BitmapButton(bitmap=wx.ArtProvider.GetBitmap('wxART_ADD_BOOKMARK',
              wx.ART_TOOLBAR, (32, 32)), id=wxID_PNLWELCOMECMDBROWSE,
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
