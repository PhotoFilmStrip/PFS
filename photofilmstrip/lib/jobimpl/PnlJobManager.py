#Boa:FramePanel:PnlJobManager
# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2012 Jens Goepfert
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
import wx.lib.scrolledpanel

from photofilmstrip.lib.jobimpl.WxVisualJobManager import WxVisualJobManager, EVT_REGISTER_JOB
from photofilmstrip.lib.jobimpl.JobManager import JobManager

from photofilmstrip.lib.jobimpl.PnlJobVisual import PnlJobVisual


[wxID_PNLJOBMANAGER, wxID_PNLJOBMANAGERCMDCLEAR, wxID_PNLJOBMANAGERPNLJOBS, 
] = [wx.NewId() for _init_ctrls in range(3)]


class PnlJobManager(wx.Panel, WxVisualJobManager):
    def _init_coll_szMain_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.pnlJobs, 1, border=0, flag=wx.EXPAND)
        parent.AddWindow(self.cmdClear, 0, border=4, flag=wx.ALL)

    def _init_sizers(self):
        # generated method, don't edit
        self.szMain = wx.BoxSizer(orient=wx.VERTICAL)

        self.szJobs = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_szMain_Items(self.szMain)

        self.SetSizer(self.szMain)
        self.pnlJobs.SetSizer(self.szJobs)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Panel.__init__(self, id=wxID_PNLJOBMANAGER, name=u'PnlJobManager',
              parent=prnt, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.TAB_TRAVERSAL)
        self.SetClientSize(wx.Size(400, 250))

        self.pnlJobs = wx.lib.scrolledpanel.ScrolledPanel(id=wxID_PNLJOBMANAGERPNLJOBS,
              name=u'pnlJobs', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.SUNKEN_BORDER)

        self.cmdClear = wx.Button(id=wxID_PNLJOBMANAGERCMDCLEAR,
              label=_(u'&Clear list'), name=u'cmdClear', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)
        self.cmdClear.Bind(wx.EVT_BUTTON, self.OnCmdClearButton,
              id=wxID_PNLJOBMANAGERCMDCLEAR)

        self._init_sizers()

    def __init__(self, parent, pnlJobClass=PnlJobVisual):
        self._init_ctrls(parent)
        WxVisualJobManager.__init__(self)
        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnSelectItem)
        self.pnlJobs.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        
        self.pnlJobs.SetupScrolling(scroll_x = False)
        
        self.parentFrame = None
        if isinstance(parent, wx.Frame):
            self.parentFrame = parent
        
        self._selected = None

        self.pnlJobVisuals = []
        self.pnlJobClass = pnlJobClass
        
        self.Bind(EVT_REGISTER_JOB, self.OnRegisterJob)
        
        JobManager().AddVisual(self)
        
#        for i in xrange(80):
#            dc = DummyRenderContext("TestJob %d" % i)
#            JobManager().EnqueueContext(dc)

    def OnRegisterJob(self, event):
        jobContext = event.GetJob()
        if jobContext.GetGroupId() != "render":
            return
        
        pjv = self.pnlJobClass(self.pnlJobs, self, jobContext)
        pjv.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)

        self.szJobs.Add(pjv, 0, wx.EXPAND)
        self.szJobs.Layout()
        
        self.pnlJobs.SetupScrolling(scroll_x = False)
        
        self.pnlJobVisuals.append(pjv)
        
        if self._selected is None:
            pjv.Select(True)
            self._selected = pjv
        
        if self.parentFrame:
            self.parentFrame.Show()
        
    def OnSelectItem(self, event):
        pnl = event.GetEventObject()
        if pnl != self._selected:
            if self._selected is not None:
                self._selected.Select(False)
            self._selected = pnl
        self._selected.Select(True)

    def OnKeyDown(self, event):
        key = event.GetKeyCode()
        try:
            idx = self.pnlJobVisuals.index(self._selected)
        except ValueError:
            idx = -1    
        if key == wx.WXK_DOWN:
            if self._selected is not None and len(self.pnlJobVisuals) > idx + 1:
                self._selected.Select(False)
                self._selected = self.pnlJobVisuals[idx + 1]
                self._selected.Select(True)
        elif key == wx.WXK_UP:
            if self._selected is not None and idx > 0:
                self._selected.Select(False)
                self._selected = self.pnlJobVisuals[idx - 1]
                self._selected.Select(True)
        else:
            event.Skip()

    def __OnDone(self):
        errMsg = self.__renderEngine.GetErrorMessage()
        errCls = self.__renderEngine.GetErrorClass()
        if errMsg:
            dlg = wx.MessageDialog(self,
                                   errMsg,
                                   _(u"Error"),
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

        self.Layout()
        
        if errCls is RendererException:
            return
        
        if not isAborted and errMsg is None:
            self.Destroy()
        
    def RemovePnlJobVisual(self, pnlJobVisual, layout=False):
        if pnlJobVisual.jobContext.IsDone():
            if pnlJobVisual is self._selected:
                self._selected = None
            self.pnlJobVisuals.remove(pnlJobVisual)
            self.szJobs.Remove(pnlJobVisual)
            pnlJobVisual.Destroy()

            if layout:
                self.szJobs.Layout()
                self.pnlJobs.SetupScrolling(scroll_x = False)
            return True
        else:
            return False

    def OnCmdClearButton(self, event):
        removedOne = False
        idx = 0
        while idx < len(self.pnlJobVisuals):
            pnlJobVis = self.pnlJobVisuals[idx]
            if self.RemovePnlJobVisual(pnlJobVis):
                removedOne = True
            else:
                idx += 1
        
        if removedOne:
            self.szJobs.Layout()
            self.pnlJobs.SetupScrolling(scroll_x = False)


from photofilmstrip.lib.jobimpl.VisualJob import VisualJob
class DummyRenderContext(VisualJob):
    
    def __init__(self, name):
        VisualJob.__init__(self, name, target=lambda: None)
        self.SetMaxProgress(100)

    def Done(self):
        self.StepProgress("Done", 95)