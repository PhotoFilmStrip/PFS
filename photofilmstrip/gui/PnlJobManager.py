#Boa:FramePanel:PnlJobManager

import wx

from photofilmstrip.lib.common.ObserverPattern import Observer
from photofilmstrip.gui.PnlJobVisual import PnlJobVisual
from photofilmstrip.core.JobManager import JobManager


[wxID_PNLJOBMANAGER, wxID_PNLJOBMANAGERCMDABORT, 
 wxID_PNLJOBMANAGERCMDPAUSERESUME, wxID_PNLJOBMANAGERPNLACTIONS, 
 wxID_PNLJOBMANAGERPNLJOBS, wxID_PNLJOBMANAGERSTATICLINE1, 
 wxID_PNLJOBMANAGERSTATICTEXT1, 
] = [wx.NewId() for _init_ctrls in range(7)]

class PnlJobManager(wx.Panel, Observer):
    def _init_coll_szMain_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.pnlJobs, 3, border=0, flag=wx.EXPAND)
        parent.AddSizer(self.szRight, 1, border=0, flag=0)

    def _init_coll_szActions_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.staticText1, 0, border=0, flag=0)

    def _init_coll_szRight_Items(self, parent):
        # generated method, don't edit

        parent.AddSizer(self.szCmds, 0, border=0, flag=0)
        parent.AddWindow(self.staticLine1, 0, border=0, flag=wx.EXPAND)
        parent.AddWindow(self.pnlActions, 0, border=0, flag=wx.EXPAND)

    def _init_coll_szCmds_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.cmdPauseResume, 0, border=0, flag=0)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.cmdAbort, 0, border=0, flag=0)

    def _init_sizers(self):
        # generated method, don't edit
        self.szMain = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.szJobs = wx.BoxSizer(orient=wx.VERTICAL)

        self.szRight = wx.BoxSizer(orient=wx.VERTICAL)

        self.szCmds = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.szActions = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_szMain_Items(self.szMain)
        self._init_coll_szRight_Items(self.szRight)
        self._init_coll_szCmds_Items(self.szCmds)
        self._init_coll_szActions_Items(self.szActions)

        self.SetSizer(self.szMain)
        self.pnlJobs.SetSizer(self.szJobs)
        self.pnlActions.SetSizer(self.szActions)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Panel.__init__(self, id=wxID_PNLJOBMANAGER, name=u'PnlJobManager',
              parent=prnt, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.TAB_TRAVERSAL)
        self.SetClientSize(wx.Size(400, 250))

        self.pnlJobs = wx.Panel(id=wxID_PNLJOBMANAGERPNLJOBS, name=u'pnlJobs',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.SUNKEN_BORDER | wx.TAB_TRAVERSAL)

        self.cmdPauseResume = wx.BitmapButton(bitmap=wx.ArtProvider.GetBitmap('wxART_GO_DOWN',
              wx.ART_TOOLBAR, wx.DefaultSize),
              id=wxID_PNLJOBMANAGERCMDPAUSERESUME, name=u'cmdPauseResume',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.BU_AUTODRAW)
        self.cmdPauseResume.Bind(wx.EVT_BUTTON, self.OnCmdPauseResumeButton,
              id=wxID_PNLJOBMANAGERCMDPAUSERESUME)

        self.cmdAbort = wx.BitmapButton(bitmap=wx.ArtProvider.GetBitmap('wxART_DELETE',
              wx.ART_TOOLBAR, wx.DefaultSize), id=wxID_PNLJOBMANAGERCMDABORT,
              name=u'cmdAbort', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.BU_AUTODRAW)
        self.cmdAbort.Bind(wx.EVT_BUTTON, self.OnCmdAbortButton,
              id=wxID_PNLJOBMANAGERCMDABORT)

        self.staticLine1 = wx.StaticLine(id=wxID_PNLJOBMANAGERSTATICLINE1,
              name='staticLine1', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.pnlActions = wx.Panel(id=wxID_PNLJOBMANAGERPNLACTIONS,
              name=u'pnlActions', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.TAB_TRAVERSAL)

        self.staticText1 = wx.StaticText(id=wxID_PNLJOBMANAGERSTATICTEXT1,
              label=u'Aktionen', name='staticText1', parent=self.pnlActions,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self._init_sizers()

    def __init__(self, parent):
        self._init_ctrls(parent)
        self.Bind(wx.EVT_TIMER, self.OnTimer)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectItem)
        self._selected = None

        self.pnlJobVisuals = []
        
        JobManager().AddObserver(self)
        
        self.timerUpdate = wx.Timer(self)
        self.timerUpdate.Start(100)

    def ObservableUpdate(self, obj, arg):
        jobContext = arg
        
        pjv = PnlJobVisual(self.pnlJobs, jobContext)
        self.szJobs.Add(pjv, 0, wx.EXPAND)
        self.Layout()
        
        self.pnlJobVisuals.append(pjv)
        
        if self._selected is None:
            pjv.Select(True)
            self._selected = pjv
        
    def OnTimer(self, event):
        for pjv in self.pnlJobVisuals:
            pjv.OnTimer()

    def OnSelectItem(self, event):
        pnl = event.GetEventObject()
        if pnl != self._selected:
            if self._selected is not None:
                self._selected.Select(False)
            pnl.Select(True)
            self._selected = pnl

    def __OnDone(self):
        isAborted = self.__progressHandler.IsAborted()
        if isAborted:
            self.stProgress.SetLabel(_(u"...aborted!"))
        else:
            self.stProgress.SetLabel(_(u"all done"))

        errMsg = self.__renderEngine.GetErrorMessage()
        errCls = self.__renderEngine.GetErrorClass()
        if errMsg:
            dlg = wx.MessageDialog(self,
                                   errMsg,
                                   _(u"Error"),
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

        self.cmdClose.SetLabel(_(u"&Close"))
        self.cmdStart.Enable(True)
        self.cmdBatch.Enable(True)
        self.pnlSettings.Enable(True)

        self.__progressHandler = None
        self.__renderEngine    = None
        self.Layout()
        
        if errCls is RendererException:
            return
        
        dlg = DlgFinalize(self, 
                          self.__GetOutputPath(),
                          isAborted, 
                          errMsg=errMsg)
        dlg.ShowModal()
        dlg.Destroy()
        
        if not isAborted and errMsg is None:
            self.Destroy()
        

    def OnCmdAbortButton(self, event):
        if self._selected:
            dlg = wx.MessageDialog(self,
                                   _(u"Abort selected process?"), 
                                   _(u"Question"),
                                   wx.YES_NO | wx.ICON_EXCLAMATION)
            resp = dlg.ShowModal()
            dlg.Destroy()
            if resp == wx.ID_YES:
                JobManager().Abort(self._selected.jobContext)

#    def ObservableUpdate(self, obj, arg):
#        if isinstance(obj, ProgressHandler):
#            if arg == 'maxProgress':
#                wx.CallAfter(self.gaugeProgress.SetRange, obj.GetMaxProgress())
#            elif arg == 'currentProgress':
#                wx.CallAfter(self.gaugeProgress.SetValue, obj.GetCurrentProgress())
#            elif arg == 'info':
#                wx.CallAfter(self.__OnProgressInfo, obj.GetInfo())
#            elif arg == 'done':
#                wx.CallAfter(self.__OnDone)
#            elif arg == 'aborting':
#                wx.CallAfter(self.__OnProgressInfo, obj.GetInfo())

#    def __OnProgressInfo(self, info):
#        self.stProgress.SetLabel(info)
#        self.Layout()

    def __CheckAbort(self):
        if self.__progressHandler.IsAborted():
            self.__aRenderer.ProcessAbort()
            return True
        return False

    def OnCmdPauseResumeButton(self, event):
        self._selected.jobContext.PauseResume()
        event.Skip()
