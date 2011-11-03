#Boa:FramePanel:PnlJobVisual

import wx

from photofilmstrip.lib.jobimpl.JobManager import JobManager

from photofilmstrip.action.DynamicAction import DynamicAction
from photofilmstrip.action.ActionPlayVideo import ActionPlayVideo
from photofilmstrip.action.ActionOpenFolder import ActionOpenFolder


[wxID_PNLJOBVISUAL, wxID_PNLJOBVISUALBMPJOB, wxID_PNLJOBVISUALCMDACTION, 
 wxID_PNLJOBVISUALCMDMENU, wxID_PNLJOBVISUALGAUGEPROGRESS, 
 wxID_PNLJOBVISUALSTATICLINE, wxID_PNLJOBVISUALSTJOBINFO, 
 wxID_PNLJOBVISUALSTJOBNAME, 
] = [wx.NewId() for _init_ctrls in range(8)]


class PnlJobVisual(wx.Panel):
    def _init_coll_szMain_Items(self, parent):
        # generated method, don't edit

        parent.AddSizer(self.szTop, 0, border=4,
              flag=wx.EXPAND | wx.RIGHT | wx.LEFT)
        parent.AddWindow(self.staticLine, 0, border=0, flag=wx.EXPAND)

    def _init_coll_szMiddle_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stJobName, 0, border=4, flag=wx.EXPAND | wx.TOP | wx.BOTTOM)
        parent.AddWindow(self.gaugeProgress, 0, border=0, flag=wx.EXPAND)
        parent.AddWindow(self.stJobInfo, 0, border=4, flag=wx.EXPAND | wx.TOP | wx.BOTTOM)

    def _init_coll_szTop_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.bmpJob, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddSpacer(wx.Size(4, 4), border=0, flag=0)
        parent.AddSizer(self.szMiddle, 1, border=0, flag=0)
        parent.AddSpacer(wx.Size(4, 4), border=0, flag=0)
        parent.AddWindow(self.cmdAction, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddSpacer(wx.Size(4, 4), border=0, flag=0)
        parent.AddWindow(self.cmdMenu, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddSpacer(wx.Size(4, 4), border=0, flag=0)

    def _init_sizers(self):
        # generated method, don't edit
        self.szMain = wx.BoxSizer(orient=wx.VERTICAL)

        self.szMiddle = wx.BoxSizer(orient=wx.VERTICAL)

        self.szTop = wx.BoxSizer(orient=wx.HORIZONTAL)

        self._init_coll_szMain_Items(self.szMain)
        self._init_coll_szMiddle_Items(self.szMiddle)
        self._init_coll_szTop_Items(self.szTop)

        self.SetSizer(self.szMain)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Panel.__init__(self, id=wxID_PNLJOBVISUAL, name=u'PnlJobVisual',
              parent=prnt, pos=wx.Point(-1, -1), size=wx.Size(-1, -1), 
              style=wx.TAB_TRAVERSAL)
        self.SetBackgroundColour(wx.Colour(255, 255, 255))

        self.bmpJob = wx.StaticBitmap(bitmap=wx.ArtProvider.GetBitmap('wxART_EXECUTABLE_FILE',
              wx.ART_TOOLBAR, wx.DefaultSize), id=wxID_PNLJOBVISUALBMPJOB,
              name=u'bmpJob', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.stJobName = wx.StaticText(id=wxID_PNLJOBVISUALSTJOBNAME,
              label=u'job name', name=u'stJobName', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.gaugeProgress = wx.Gauge(id=wxID_PNLJOBVISUALGAUGEPROGRESS,
              name=u'gaugeProgress', parent=self, pos=wx.Point(-1, -1),
              range=100, size=wx.Size(-1, -1), style=wx.GA_HORIZONTAL)

        self.stJobInfo = wx.StaticText(id=wxID_PNLJOBVISUALSTJOBINFO,
              label=u'job info', name=u'stJobInfo', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.cmdAction = wx.StaticBitmap(bitmap=wx.ArtProvider.GetBitmap('wxART_FOLDER_OPEN',
              wx.ART_TOOLBAR, wx.DefaultSize), id=wxID_PNLJOBVISUALCMDACTION,
              name=u'cmdAction', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)
        self.cmdAction.Bind(wx.EVT_LEFT_DOWN, self.OnCmdActionLeftDown)

        self.cmdMenu = wx.StaticBitmap(bitmap=wx.ArtProvider.GetBitmap('wxART_GO_DOWN',
              wx.ART_TOOLBAR, wx.DefaultSize), id=wxID_PNLJOBVISUALCMDMENU,
              name=u'cmdMenu', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)
        self.cmdMenu.Bind(wx.EVT_LEFT_DOWN, self.OnCmdMenuLeftDown)

        self.staticLine = wx.StaticLine(id=wxID_PNLJOBVISUALSTATICLINE,
              name=u'staticLine', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self._init_sizers()

    def __init__(self, parent, pnlJobManager, jobContext):
        self._init_ctrls(parent)
        self.pnlJobManager = pnlJobManager
        for ctrl in (self, self.stJobName, self.stJobInfo, self.gaugeProgress):
            ctrl.Bind(wx.EVT_LEFT_DOWN, self.__OnLeftDown)
        
        font = self.stJobName.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.stJobName.SetFont(font)

        self.stJobName.SetLabel(jobContext.GetName())
        self.gaugeProgress.SetRange(jobContext.GetMaxProgress())
        
        self.jobContext = jobContext
        
        self._actPause = DynamicAction(
                _(u"Pause"), 
                self._PauseResume, 
                bmp={wx.ART_MENU: wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_MENU, wx.DefaultSize),
                     wx.ART_TOOLBAR: wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_TOOLBAR, wx.DefaultSize)}
        )
        self._actResume = DynamicAction(
                 _(u"Resume"), 
                self._PauseResume, 
                bmp={wx.ART_MENU: wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_MENU, wx.DefaultSize),
                     wx.ART_TOOLBAR: wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_TOOLBAR, wx.DefaultSize)}
        )
        self._actRemove = DynamicAction(
                _("Remove from list"),
                self._Remove,
                bmp={wx.ART_MENU: wx.ArtProvider.GetBitmap(wx.ART_CROSS_MARK, wx.ART_MENU, wx.DefaultSize),
                     wx.ART_TOOLBAR: wx.ArtProvider.GetBitmap(wx.ART_CROSS_MARK, wx.ART_TOOLBAR, wx.DefaultSize)}
        )
        self._actPlay = DynamicAction(
                _("Play video"),
                self._PlayVideo,
                bmp={wx.ART_MENU: wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_MENU, wx.DefaultSize),
                     wx.ART_TOOLBAR: wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, wx.DefaultSize)}
        )
        self._actOpenFldr = DynamicAction(
                    _(u"Open folder"),
                self._OpenFolder,
                bmp={wx.ART_MENU: wx.ArtProvider.GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_MENU, wx.DefaultSize),
                     wx.ART_TOOLBAR: wx.ArtProvider.GetBitmap(wx.ART_FOLDER_OPEN, wx.ART_TOOLBAR, wx.DefaultSize)}
        )

        self.curAction = None
        
    def OnTimer(self):
        progress = self.jobContext.GetCurrentProgress()
        self.stJobInfo.SetLabel(self.jobContext.GetInfo())
        self.gaugeProgress.SetValue(progress)
        
        self._SetupAction()

    def __OnLeftDown(self, event):
        evt = wx.ListEvent(wx.EVT_LIST_ITEM_SELECTED.typeId, self.GetId())
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)

    def Select(self, value):
        if value:
            if self.IsShownOnScreen():
                self.SetFocus()
            bgCol = wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT)
            txtCol = wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT)
        else:
            bgCol = wx.WHITE
            txtCol = wx.SystemSettings_GetColour(wx.SYS_COLOUR_LISTBOXTEXT)
        self.SetBackgroundColour(bgCol)
        self.stJobName.SetForegroundColour(txtCol)
        self.stJobInfo.SetForegroundColour(txtCol)
        
        self.Refresh()

    def OnCmdActionLeftDown(self, event):
        self.curAction.Execute()
        event.Skip()

    def OnCmdMenuLeftDown(self, event):
        menu = wx.Menu()
        id2 = wx.NewId()
        id3 = wx.NewId()

        if self.jobContext.IsPaused():
            self._actResume.ToMenu(self, menu)
        elif self.jobContext.IsRunning():
            self._actPause.ToMenu(self, menu)
        
        if self.jobContext.IsDone() or self.jobContext.IsAborted():
            self._actRemove.ToMenu(self, menu)
        else:
            menu.Append(id3, _(u"Abort"))
        
        menu.AppendSeparator()
        mitm = self._actPlay.ToMenu(self, menu)
        menu.Enable(mitm.GetId(), not self.jobContext.IsAborted())
        self._actOpenFldr.ToMenu(self, menu)
        
        self.Bind(wx.EVT_MENU, self._Remove, id=id2)
        self.Bind(wx.EVT_MENU, self._Abort, id=id3)
        
        self.cmdMenu.PopupMenu(menu)
        
    def _SetupAction(self):
        if self.jobContext.IsRunning():
            self.curAction = self._actPause
        elif self.jobContext.IsPaused():
            self.curAction = self._actResume
        elif self.jobContext.IsAborted():
            self.curAction = self._actRemove
        elif self.jobContext.IsDone():
            self.curAction = self._actPlay
        else:
            self.curAction = None
        
        curTip = self.cmdAction.GetToolTip()
        if curTip:
            curTip = curTip.GetTip()
        
        if curTip != self.curAction.GetName():
            self.cmdAction.SetBitmap(self.curAction.GetBitmap(wx.ART_TOOLBAR))
            self.cmdAction.SetToolTipString(self.curAction.GetName())
        
    def _PauseResume(self):    
        self.jobContext.PauseResume()
    
    def _Abort(self, event):
        dlg = wx.MessageDialog(self,
                               _(u"Abort selected process?"), 
                               _(u"Question"),
                               wx.YES_NO | wx.ICON_EXCLAMATION)
        resp = dlg.ShowModal()
        dlg.Destroy()
        if resp == wx.ID_YES:
            JobManager().Abort(self.jobContext)
        event.Skip()
        
    def _Remove(self):
        wx.CallAfter(self.pnlJobManager.RemovePnlJobVisual, self, True)
#        self.pnlJobManager.RemovePnlJobVisual(self, True)
        
    def _PlayVideo(self):
        print "Play video"
        ActionPlayVideo(None).Execute()
        
    def _OpenFolder(self):
        print "Open folder"
        ActionOpenFolder(None).Execute()



"""
Actions:
State = running: Pause --> paused
State = paused:  Resume --> running
State = finished: Play video
State = aborted: Clear (Msg: Delete files?)

Menu:
- Abort
- - 
- Open folder

2. Continue
State = finished
3. 
"""