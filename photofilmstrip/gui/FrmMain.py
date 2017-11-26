# Boa:Frame:FrmMain
# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
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

import os

import wx
import wx.aui
from wx.lib.wordwrap import wordwrap

from photofilmstrip import Constants

from photofilmstrip.action.ActionI18N import ActionI18N

from photofilmstrip.core.RenderJob import RenderJob

from photofilmstrip.lib.common.ObserverPattern import Observer
from photofilmstrip.lib.Settings import Settings
from photofilmstrip.lib.util import Decode

from photofilmstrip.lib.jobimpl.WxVisualJobManager import (
        WxVisualJobManager, EVT_REGISTER_JOB, EVT_REMOVE_JOB)
from photofilmstrip.lib.jobimpl.JobManager import JobManager
from photofilmstrip.lib.jobimpl.PnlJobManager import PnlJobManager

from photofilmstrip.gui.ActionManager import ActionManager
from photofilmstrip.gui.PnlWelcome import PnlWelcome
from photofilmstrip.gui.HelpViewer import HelpViewer
from photofilmstrip.gui.DlgProjectProps import DlgProjectProps
from photofilmstrip.gui.PnlPfsProject import PnlPfsProject
from photofilmstrip.gui.WxProjectFile import WxProjectFile
from photofilmstrip.gui.PnlRenderJobVisual import PnlRenderJobVisual
from photofilmstrip.gui.PnlEditorPage import PnlEditorPage

from photofilmstrip.res.license import licenseText

ID_PAGE_UP = wx.NewId()
ID_PAGE_DOWN = wx.NewId()


class FrmMain(wx.Frame, Observer, WxVisualJobManager):

    def __init__(self):
        wx.Frame.__init__(self, None, -1, name=u'FrmMain',
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL)
        WxVisualJobManager.__init__(self)
        self.SetTitle(Constants.APP_NAME)

        iconBundle = wx.IconBundle()
        iconBundle.AddIcon(wx.ArtProvider.GetIcon("PFS_ICON_16", wx.ART_OTHER))
        iconBundle.AddIcon(wx.ArtProvider.GetIcon("PFS_ICON_24", wx.ART_OTHER))
        iconBundle.AddIcon(wx.ArtProvider.GetIcon("PFS_ICON_32", wx.ART_OTHER))
        iconBundle.AddIcon(wx.ArtProvider.GetIcon("PFS_ICON_48", wx.ART_OTHER))
        iconBundle.AddIcon(wx.ArtProvider.GetIcon("PFS_ICON_64", wx.ART_OTHER))
        iconBundle.AddIcon(wx.ArtProvider.GetIcon("PFS_ICON_128", wx.ART_OTHER))
        self.SetIcons(iconBundle)

        self.statusBar = wx.StatusBar(self)
        self.statusBar.SetFieldsCount(4)
        self.statusBar.Bind(wx.EVT_LEFT_DOWN, self.OnStatusBarLeftDown)
        self.SetStatusBar(self.statusBar)

        self.menuBar = wx.MenuBar()
        self.SetMenuBar(self.menuBar)

        self.toolBar = wx.ToolBar(self)
        self.SetToolBar(self.toolBar)

        self._actionMgr = ActionManager(self, self.menuBar, self.toolBar)

        self.notebook = wx.aui.AuiNotebook(self, -1, style=wx.aui.AUI_NB_CLOSE_ON_ACTIVE_TAB)
        self.notebook.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.notebook.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnPageClose)

        self.pnlWelcome = PnlWelcome(self.notebook, self)
        self.pnlWelcome.SetDropTarget(ProjectDropTarget(self))

        self.notebook.AddPage(self.pnlWelcome, _(u"Welcome"), True)

        self.frmJobManager = wx.Frame(self, -1, _(u"Job queue"),
                                      size=wx.Size(600, 400),
                                      style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.frmJobManager.Bind(wx.EVT_CLOSE, self.OnCloseFrameJobManager)
        PnlJobManager(self.frmJobManager, pnlJobClass=PnlRenderJobVisual)

        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.Bind(wx.EVT_MENU, self.OnProjectNew, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.OnProjectLoad, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.OnProjectSave, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.OnProjectSaveAs, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.OnProjectClose,
                  id=ActionManager.ID_PROJECT_CLOSE)
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)

        self.Bind(wx.EVT_MENU, self.OnAbout, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnHelpIndex, id=wx.ID_HELP)
        for wxId in ActionManager.LANG_MAP.keys():
            self.Bind(wx.EVT_MENU, self.OnChangeLanguage, id=wxId)

        self.Bind(wx.EVT_MENU, self.OnShowFrameJobManager,
                  id=ActionManager.ID_JOB_QUEUE)

        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectChanged, id=wx.ID_SAVE)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectActive, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectActive,
                  id=ActionManager.ID_PROJECT_CLOSE)

        self.Bind(wx.EVT_MENU, self.OnHelpContent, id=wx.ID_HELP_CONTENTS)
        self.Bind(wx.EVT_MENU, self.OnPageNext, id=ID_PAGE_DOWN)
        self.Bind(wx.EVT_MENU, self.OnPagePrev, id=ID_PAGE_UP)

        self.SetInitialSize((720, 680))

        at = wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_F1, wx.ID_HELP_CONTENTS),
                                  (wx.ACCEL_CTRL, wx.WXK_PAGEDOWN, ID_PAGE_DOWN),
                                  (wx.ACCEL_CTRL, wx.WXK_PAGEUP, ID_PAGE_UP)])
        self.SetAcceleratorTable(at)

        JobManager().AddVisual(self)

        self.Bind(EVT_REGISTER_JOB, self.OnRegisterJob)
        self.Bind(EVT_REMOVE_JOB, self.OnRemoveJob)

    def ObservableUpdate(self, obj, arg):
        if obj is self.__GetCurrentProject():
            self.UpdateStatusText()

#### Event-Handler - Begin #####################################################
# Jobs
    def OnRegisterJob(self, event):
        job = event.GetJob()
        if isinstance(job, RenderJob):
            self.statusBar.SetStatusText(_(u"Rendering in progress..."), 3)

    def OnRemoveJob(self, event):
        self.statusBar.SetStatusText("", 3)

    def OnCloseFrameJobManager(self, event):
        self.frmJobManager.Show(False)

    def OnShowFrameJobManager(self, event):
        self.frmJobManager.Show()

# Pages
    def OnPageChanged(self, event):
        sel = event.GetSelection()
        page = None
        if sel == 0:
            self.notebook.SetWindowStyleFlag(0)
            self.SetTitle(Constants.APP_NAME)
        else:
            page = self.notebook.GetPage(sel)
            self.notebook.SetWindowStyleFlag(wx.aui.AUI_NB_CLOSE_ON_ACTIVE_TAB)

            filepath = page.GetProject().GetFilename()
            self.SetTitle(Constants.APP_NAME + u' - ' + Decode(filepath))

        self._actionMgr.UpdateActions(page)
        self.UpdateStatusText()

    def OnPageNext(self, event):
        idx = self.notebook.GetSelection()
        idx += 1
        if idx < self.notebook.GetPageCount():
            self.notebook.SetSelection(idx)

    def OnPagePrev(self, event):
        idx = self.notebook.GetSelection()
        idx -= 1
        if idx >= 0:
            self.notebook.SetSelection(idx)

    def OnPageClose(self, event):
        sel = event.GetSelection()
        if sel == 0:
            event.Veto()
            return
        else:
            if self.ClosePage(sel):
                event.Skip()
            else:
                event.Veto()

# UpdateUI
    def OnCheckProjectActive(self, event):
        pnl = self.__GetCurrentPnlEditor()
        event.Enable(pnl is not None)

    def OnCheckProjectChanged(self, event):
        pnl = self.__GetCurrentPnlEditor()
        if pnl:
            event.Enable(pnl.HasChanged())
        else:
            event.Enable(False)

# Misc
    def OnStatusBarLeftDown(self, event):
        if self.statusBar.GetFieldRect(3).Contains(event.GetPosition()) \
        and self.statusBar.GetStatusText(3) != "":
            self.frmJobManager.Show()

    def OnClose(self, event):
        while self.notebook.GetPageCount() > 1:
            idx = 1
            self.notebook.SetSelection(idx)
            if self.ClosePage(idx):
                self.notebook.DeletePage(idx)
            else:
                return
        JobManager().RemoveVisual(self)
        self.frmJobManager.Destroy()
        event.Skip()

# Menu
    def OnProjectNew(self, event):
        dlg = DlgProjectProps(self)
        if dlg.ShowModal() == wx.ID_OK:
            photoFilmStrip = dlg.GetProject()
            self.NewProject(photoFilmStrip)
        dlg.Destroy()

    def OnProjectLoad(self, event):
        dlg = wx.FileDialog(self, _(u"Select %s-Project") % Constants.APP_NAME,
                            Settings().GetProjectPath(), "",
                            Constants.APP_NAME + u'-' + _(u"Files") + " (*.pfs)|*.pfs",
                            wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.LoadProject(dlg.GetPath())

    def OnProjectSave(self, event):
        pnlEditor = self.__GetCurrentPnlEditor()
        if pnlEditor:
            if pnlEditor.OnSave():
                self.AddFileToHistory(pnlEditor.GetSaveFilePath())

    def OnProjectSaveAs(self, event):
        pnlEditor = self.__GetCurrentPnlEditor()
        if pnlEditor:
            if pnlEditor.OnSaveAs():
                self.AddFileToHistory(pnlEditor.GetSaveFilePath())

    def OnProjectClose(self, event):
        sel = self.notebook.GetSelection()
        if self.ClosePage(sel):
            self.notebook.DeletePage(sel)

    def OnExit(self, event):
        self.Close()

    def OnHelpIndex(self, event):
        HelpViewer().DisplayID(HelpViewer.ID_INDEX)
        event.Skip()

    def OnHelpContent(self, event):
        HelpViewer().DisplayID(HelpViewer.ID_CREATE_PFS)
        event.Skip()

    def OnChangeLanguage(self, event):
        lang = ActionManager.LANG_MAP.get(event.GetId(), "en")
        Settings().SetLanguage(lang)
        ActionI18N().Execute()
        dlg = wx.MessageDialog(self,
                               _(u"You must restart %s for your new language setting to take effect.") % Constants.APP_NAME,
                               _(u"Information"),
                               wx.ICON_INFORMATION | wx.OK)
        dlg.ShowModal()
        dlg.Destroy()

    def OnAbout(self, event):
        info = wx.AboutDialogInfo()
        info.Name = Constants.APP_NAME
        info.Version = Constants.APP_VERSION_EX
        info.Copyright = u"(C) 2017 %s" % Constants.DEVELOPERS[0]
        info.Description = wordwrap(_("PhotoFilmStrip creates movies out of your pictures in just 3 steps. First select your photos, customize the motion path and render the video. There are several output possibilities for VCD, SVCD, DVD up to FULL-HD."),
                                    350,
                                    wx.ClientDC(self))
        info.WebSite = (Constants.APP_URL, "%s %s" % (Constants.APP_NAME, _(u"online")))
        info.Developers = Constants.DEVELOPERS
        info.Translators = Constants.TRANSLATORS

        info.License = wordwrap(licenseText, 500, wx.ClientDC(self))

        wx.AboutBox(info)

#### Event-Handler - END #######################################################

    def __GetCurrentPnlEditor(self):
        sel = self.notebook.GetSelection()
        page = self.notebook.GetPage(sel)
        if isinstance(page, PnlEditorPage):
            return page

    def __GetCurrentProject(self):
        page = self.__GetCurrentPnlEditor()
        if page:
            return page.GetProject()
        return None

    def AddFileToHistory(self, filename):
        fileList = Settings().GetFileHistory()
        if filename in fileList:
            fileList.remove(filename)
        fileList.insert(0, filename)
        Settings().SetFileHistory(fileList)

    def UpdateStatusText(self):
        page = self.__GetCurrentPnlEditor()
        if page is None:
            self.statusBar.SetStatusText(Constants.APP_URL, 1)
            self.statusBar.SetStatusText("%s %s" % (Constants.APP_NAME, Constants.APP_VERSION), 2)
        else:
            self.statusBar.SetStatusText(page.GetStatusText(0), 1)
            self.statusBar.SetStatusText(page.GetStatusText(1), 2)

    def ClosePage(self, idx):
        page = self.notebook.GetPage(idx)
        if page.CheckAndAskSaving():
            page.Close()
            return True
        else:
            return False

    def NewProject(self, project):
        pnl = PnlPfsProject(self.notebook, project)
        project.AddObserver(self)
        filepath = os.path.basename(project.GetFilename())
        self.notebook.AddPage(pnl, os.path.basename(filepath), True)
        return pnl

    def LoadProject(self, filepath, skipHistory=False):
        for idx in range(1, self.notebook.GetPageCount()):
            page = self.notebook.GetPage(idx)
            if page.GetProject().GetFilename() == filepath:
                self.notebook.SetSelection(idx)
                return

        prjFile = WxProjectFile(self, filename=filepath)
        result = prjFile.Load()
        if not result:
            dlg = wx.MessageDialog(self,
                                   _(u"Invalid %(app)s-Project: %(file)s") % {"app": Constants.APP_NAME,
                                                                              "file": filepath},
                                   _(u"Error"),
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        photoFilmStrip = prjFile.GetProject()
        pics = photoFilmStrip.GetPictures()

        pnl = self.NewProject(photoFilmStrip)
        pnl.InsertPictures(pics)
        pnl.SetChanged(False)

        if not skipHistory:
            self.AddFileToHistory(filepath)

#             self.pnlWelcome.RefreshPage() # crashes on unix
            wx.CallAfter(self.pnlWelcome.RefreshPage)


class ProjectDropTarget(wx.FileDropTarget):

    def __init__(self, frmMain):
        wx.FileDropTarget.__init__(self)
        self.frmMain = frmMain

    def OnDropFiles(self, x, y, filenames):
        if len(filenames) == 1:
            path = filenames[0]
            ext = os.path.splitext(path)[1].lower()
            if ext == '.pfs':
                self.frmMain.LoadProject(path)
                return True

        return False
