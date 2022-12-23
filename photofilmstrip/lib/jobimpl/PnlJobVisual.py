# Boa:FramePanel:PnlJobVisual
# -*- coding: utf-8 -*-
#
# Copyright (C) 2018 Jens Goepfert
#

import wx

from photofilmstrip.action.WxAction import WxAction
from photofilmstrip.lib.jobimpl.WxVisualJobHandler import (
    WxVisualJobHandler, EVT_JOB_UPDATE)

[wxID_PNLJOBVISUAL, wxID_PNLJOBVISUALBMPJOB, wxID_PNLJOBVISUALCMDACTION,
 wxID_PNLJOBVISUALCMDMENU, wxID_PNLJOBVISUALGAUGEPROGRESS,
 wxID_PNLJOBVISUALSTATICLINE, wxID_PNLJOBVISUALSTJOBINFO,
 wxID_PNLJOBVISUALSTJOBNAME,
] = [wx.NewId() for _init_ctrls in range(8)]


class PnlJobVisual(wx.Panel, WxVisualJobHandler):

    def _init_coll_szMain_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.szTop, 0, border=4,
              flag=wx.EXPAND | wx.RIGHT | wx.LEFT)
        parent.Add(self.staticLine, 0, border=0, flag=wx.EXPAND)

    def _init_coll_szMiddle_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.stJobName, 0, border=4, flag=wx.EXPAND | wx.TOP | wx.BOTTOM)
        parent.Add(self.gaugeProgress, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.stJobInfo, 0, border=4, flag=wx.EXPAND | wx.TOP | wx.BOTTOM)

    def _init_coll_szTop_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.bmpJob, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddSpacer(4)
        parent.Add(self.szMiddle, 1, border=0, flag=0)
        parent.AddSpacer(4)
        parent.Add(self.cmdAction, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddSpacer(4)
        parent.Add(self.cmdMenu, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddSpacer(4)

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
        wx.Panel.__init__(self, id=wxID_PNLJOBVISUAL, name="PnlJobVisual",
              parent=prnt, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.TAB_TRAVERSAL)
        self.SetBackgroundColour(wx.Colour(255, 255, 255))

        self.bmpJob = wx.StaticBitmap(
              bitmap=wx.ArtProvider.GetBitmap('PFS_RENDER', wx.ART_TOOLBAR),
              id=wxID_PNLJOBVISUALBMPJOB,
              name="bmpJob", parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.stJobName = wx.StaticText(id=wxID_PNLJOBVISUALSTJOBNAME,
              label="job name", name="stJobName", parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.ST_NO_AUTORESIZE | wx.ST_ELLIPSIZE_START)

        self.gaugeProgress = wx.Gauge(id=wxID_PNLJOBVISUALGAUGEPROGRESS,
              name="gaugeProgress", parent=self, pos=wx.Point(-1, -1),
              range=100, size=wx.Size(-1, -1), style=wx.GA_HORIZONTAL)

        self.stJobInfo = wx.StaticText(id=wxID_PNLJOBVISUALSTJOBINFO,
              label="job info", name="stJobInfo", parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.cmdAction = wx.StaticBitmap(
              bitmap=wx.ArtProvider.GetBitmap('PFS_FOLDER_OPEN', wx.ART_TOOLBAR),
              id=wxID_PNLJOBVISUALCMDACTION,
              name="cmdAction", parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)
        self.cmdAction.Bind(wx.EVT_LEFT_DOWN, self.OnCmdActionLeftDown)

        self.cmdMenu = wx.StaticBitmap(
              bitmap=wx.ArtProvider.GetBitmap('PFS_MENU', wx.ART_TOOLBAR),
              id=wxID_PNLJOBVISUALCMDMENU,
              name="cmdMenu", parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)
        self.cmdMenu.Bind(wx.EVT_LEFT_DOWN, self.OnCmdMenuLeftDown)

        self.staticLine = wx.StaticLine(id=wxID_PNLJOBVISUALSTATICLINE,
              name="staticLine", parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self._init_sizers()

    def __init__(self, parent, pnlJobManager, jobContext):
        self._init_ctrls(parent)
        WxVisualJobHandler.__init__(self)
        self.pnlJobManager = pnlJobManager
        for ctrl in (self, self.stJobName, self.stJobInfo, self.gaugeProgress):
            ctrl.Bind(wx.EVT_LEFT_DOWN, self.__OnLeftDown)

        font = self.stJobName.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.stJobName.SetFont(font)

        self.stJobName.SetLabel(jobContext.GetName())
        self.gaugeProgress.SetRange(jobContext.GetMaxProgress())

        self.jobContext = jobContext

        self._actAbort = WxAction(
                 _("Abort"),
                self._Abort,
                bmp={wx.ART_MENU: wx.ArtProvider.GetBitmap('PFS_ABORT', wx.ART_MENU),
                     wx.ART_TOOLBAR: wx.ArtProvider.GetBitmap('PFS_ABORT', wx.ART_TOOLBAR)}
        )
        self._actRemove = WxAction(
                _("Remove from list"),
                self._Remove,
                bmp={wx.ART_MENU: wx.ArtProvider.GetBitmap('PFS_LIST_REMOVE', wx.ART_MENU),
                     wx.ART_TOOLBAR: wx.ArtProvider.GetBitmap('PFS_LIST_REMOVE', wx.ART_TOOLBAR)}
        )

        self.curAction = None
        self.jobContext.AddVisualJobHandler(self)

        self.Bind(EVT_JOB_UPDATE, self.OnJobUpdate)

    def OnJobUpdate(self, event):
        fields = event.GetFields()
        if "progress" in fields:
            self.gaugeProgress.SetValue(self.jobContext.GetProgress())
        if "info" in fields:
            self.stJobInfo.SetLabel(self.jobContext.GetInfo())
        if "maxProgress" in fields:
            self.gaugeProgress.SetRange(self.jobContext.GetMaxProgress())
        if "name" in fields:
            self.stJobName.SetLabel(self.jobContext.GetName())
        self._SetupAction()

    def __OnLeftDown(self, event):
        evt = wx.ListEvent(wx.EVT_LIST_ITEM_SELECTED.typeId, self.GetId())
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)

    def Select(self, value):
        if value:
            if self.IsShownOnScreen():
                self.SetFocus()
            bgCol = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
            txtCol = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT)
        else:
            bgCol = wx.WHITE
            txtCol = wx.SystemSettings.GetColour(wx.SYS_COLOUR_LISTBOXTEXT)
        self.SetBackgroundColour(bgCol)
        self.stJobName.SetForegroundColour(txtCol)
        self.stJobInfo.SetForegroundColour(txtCol)

        self.Refresh()

    def OnCmdActionLeftDown(self, event):
        self.curAction.Execute()
        event.Skip()

    def OnCmdMenuLeftDown(self, event):
        menu = wx.Menu()

        mitm = self._actAbort.ToMenu(self, menu)
        menu.Enable(mitm.GetId(),
                    self.jobContext.IsIdle() or not self.jobContext.IsDone())

        mitm = self._actRemove.ToMenu(self, menu)
        menu.Enable(mitm.GetId(),
                    self.jobContext.IsDone())

        menu.AppendSeparator()

        self._OnMenuActions(menu)

        self.cmdMenu.PopupMenu(menu)

    def _OnMenuActions(self, menu):
        pass

    def _SetupAction(self):
        if self.jobContext.IsIdle() or not self.jobContext.IsDone():
            self.curAction = self._actAbort
        elif self.jobContext.IsAborted() or self.jobContext.IsDone():
            self.curAction = self._actRemove
        else:
            self.curAction = None

        self._OnSetupAction()

        curTip = self.cmdAction.GetToolTip()
        if curTip:
            curTip = curTip.GetTip()

        if self.curAction and curTip != self.curAction.GetName():
            self.cmdAction.SetBitmap(self.curAction.GetBitmap(wx.ART_TOOLBAR))
            self.cmdAction.SetToolTip(self.curAction.GetName())

    def _OnSetupAction(self):
        pass

    def _Abort(self):
        dlg = wx.MessageDialog(self,
                               _("Abort selected process?"),
                               _("Question"),
                               wx.YES_NO | wx.ICON_EXCLAMATION)
        try:
            if dlg.ShowModal() == wx.ID_YES:
                self.jobContext.Abort()
        finally:
            dlg.Destroy()

    def _Remove(self):
        wx.CallAfter(self.pnlJobManager.RemovePnlJobVisual, self, True)
#        self.pnlJobManager.RemovePnlJobVisual(self, True)
