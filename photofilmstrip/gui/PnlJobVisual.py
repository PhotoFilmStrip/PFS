#Boa:FramePanel:PnlJobVisual

import wx

[wxID_PNLJOBVISUAL, wxID_PNLJOBVISUALGAUGEPROGRESS, 
 wxID_PNLJOBVISUALSTATICLINE, wxID_PNLJOBVISUALSTJOBINFO, 
 wxID_PNLJOBVISUALSTJOBNAME, 
] = [wx.NewId() for _init_ctrls in range(5)]

class PnlJobVisual(wx.Panel):
    def _init_coll_szMain_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stJobName, 0, border=4, flag=wx.ALL)
        parent.AddWindow(self.stJobInfo, 0, border=4, flag=wx.LEFT | wx.RIGHT)
        parent.AddWindow(self.gaugeProgress, 0, border=4, flag=wx.EXPAND | wx.ALL)
        parent.AddWindow(self.staticLine, 0, border=0, flag=wx.EXPAND)

    def _init_sizers(self):
        # generated method, don't edit
        self.szMain = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_szMain_Items(self.szMain)

        self.SetSizer(self.szMain)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Panel.__init__(self, id=wxID_PNLJOBVISUAL, name=u'PnlJobVisual',
              parent=prnt, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.TAB_TRAVERSAL)
        self.SetClientSize(wx.Size(600, 96))
        self.SetBackgroundColour(wx.Colour(255, 255, 255))

        self.stJobName = wx.StaticText(id=wxID_PNLJOBVISUALSTJOBNAME,
              label=u'job name', name=u'stJobName', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.stJobInfo = wx.StaticText(id=wxID_PNLJOBVISUALSTJOBINFO,
              label=u'job info', name=u'stJobInfo', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.gaugeProgress = wx.Gauge(id=wxID_PNLJOBVISUALGAUGEPROGRESS,
              name=u'gaugeProgress', parent=self, pos=wx.Point(-1, -1),
              range=100, size=wx.Size(-1, -1), style=wx.GA_HORIZONTAL)

        self.staticLine = wx.StaticLine(id=wxID_PNLJOBVISUALSTATICLINE,
              name=u'staticLine', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self._init_sizers()

    def __init__(self, parent, jobContext):
        self._init_ctrls(parent)
        for ctrl in (self, self.stJobName, self.stJobInfo, self.gaugeProgress):
            ctrl.Bind(wx.EVT_LEFT_DOWN, self.__OnLeftDown)
        
        font = self.stJobName.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.stJobName.SetFont(font)

        self.stJobName.SetLabel(jobContext.GetName())
        self.gaugeProgress.SetRange(jobContext.GetMaxProgress())
        
        self.jobContext = jobContext
        
    def OnTimer(self):
        progress = self.jobContext.GetCurrentProgress()
        self.stJobInfo.SetLabel(self.jobContext.GetInfo())
        self.gaugeProgress.SetValue(progress)
        self.gaugeProgress.Update()
        self.Refresh()

    def __OnLeftDown(self, event):
        evt = wx.ListEvent(wx.EVT_LIST_ITEM_SELECTED.typeId, self.GetId())
        evt.SetEventObject(self)
#        evt.m_itemIndex = idx
#        evt.m_oldItemIndex = self.__selIdx

#        self.__selIdx = idx
        
        self.GetEventHandler().ProcessEvent(evt)

    def Select(self, value):
        if value:
            bgCol = wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT)
            txtCol = wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT)
        else:
            bgCol = wx.WHITE
            txtCol = wx.SystemSettings_GetColour(wx.SYS_COLOUR_LISTBOXTEXT)
        self.SetBackgroundColour(bgCol)
        self.stJobName.SetForegroundColour(txtCol)
        self.stJobInfo.SetForegroundColour(txtCol)
        
        self.Refresh()
