#Boa:Frame:FrmMain
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

from photofilmstrip.lib.common.ObserverPattern import Observer
from photofilmstrip.lib.Settings import Settings
from photofilmstrip.lib.util import Decode

from photofilmstrip.lib.jobimpl.WxVisualJobManager import (
        WxVisualJobManager, EVT_REGISTER_JOB, EVT_REMOVE_JOB)
from photofilmstrip.lib.jobimpl.JobManager import JobManager
from photofilmstrip.lib.jobimpl.PnlJobManager import PnlJobManager

from photofilmstrip.gui.DlgRender import DlgRender
from photofilmstrip.gui.PnlWelcome import PnlWelcome
from photofilmstrip.gui.ActionManager import ActionManager
from photofilmstrip.gui.HelpViewer import HelpViewer
from photofilmstrip.gui.DlgProjectProps import DlgProjectProps
from photofilmstrip.gui.PnlPfsProject import PnlPfsProject
from photofilmstrip.gui.WxProjectFile import WxProjectFile
from photofilmstrip.gui.PnlRenderJobVisual import PnlRenderJobVisual

from photofilmstrip.res.license import licenseText
from photofilmstrip.core.RenderJob import RenderJob


class FrmMain(wx.Frame, Observer, WxVisualJobManager):
    
    def __init__(self):
        wx.Frame.__init__(self, None, -1, name=u'FrmMain',
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL,
              title='PhotoFilmStrip')
        WxVisualJobManager.__init__(self)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.SetTitle(Constants.APP_NAME)
        
        iconBundle = wx.IconBundle()
        iconBundle.AddIcon(wx.ArtProvider_GetIcon("PFS_ICON_16", wx.ART_OTHER))
        iconBundle.AddIcon(wx.ArtProvider_GetIcon("PFS_ICON_24", wx.ART_OTHER))
        iconBundle.AddIcon(wx.ArtProvider_GetIcon("PFS_ICON_32", wx.ART_OTHER))
        iconBundle.AddIcon(wx.ArtProvider_GetIcon("PFS_ICON_48", wx.ART_OTHER))
        iconBundle.AddIcon(wx.ArtProvider_GetIcon("PFS_ICON_64", wx.ART_OTHER))
        iconBundle.AddIcon(wx.ArtProvider_GetIcon("PFS_ICON_128", wx.ART_OTHER))
        self.SetIcons(iconBundle)
        
        self.statusBar = wx.StatusBar(self)
        self.statusBar.SetFieldsCount(4)
        self.statusBar.Bind(wx.EVT_LEFT_DOWN, self.OnStatusBarLeftDown)
        self.SetStatusBar(self.statusBar)
        
        self.actionManager = ActionManager()
        
        menuBar = self.actionManager.GetMenuBar()
        self.SetMenuBar(menuBar)
        toolBar = self.actionManager.GetToolBar(self)
        self.SetToolBar(toolBar)
        
        self.notebook = wx.aui.AuiNotebook(self, -1, style=wx.aui.AUI_NB_CLOSE_ON_ACTIVE_TAB)
        self.notebook.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CHANGED, self.OnPageChanged)
        self.notebook.Bind(wx.aui.EVT_AUINOTEBOOK_PAGE_CLOSE, self.OnPageClose)
        
        self.pnlWelcome = PnlWelcome(self.notebook, self)
        self.pnlWelcome.SetDropTarget(ProjectDropTarget(self))
        
        self.notebook.AddPage(self.pnlWelcome, _(u"Welcome"), True)
        
        self.frmJobManager = wx.Frame(self, -1, _(u"Job queue"),
                                      size=wx.Size(600,400),
                                      style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.frmJobManager.Bind(wx.EVT_CLOSE, self.OnCloseFrameJobManager)
        pnlJobManager = PnlJobManager(self.frmJobManager, pnlJobClass=PnlRenderJobVisual)
        
        self.Bind(wx.EVT_MENU, self.OnProjectNew, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.OnProjectLoad, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.OnProjectSave, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.OnProjectClose, id=ActionManager.ID_PROJECT_CLOSE)
        self.Bind(wx.EVT_MENU, self.OnProjectSaveAs, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.OnProjectExport, id=ActionManager.ID_PROJECT_EXPORT)
        self.Bind(wx.EVT_MENU, self.OnProjectImport, id=ActionManager.ID_PROJECT_IMPORT)
        self.Bind(wx.EVT_MENU, self.OnProjectProps, id=ActionManager.ID_PROJECT_PROPS)
        self.Bind(wx.EVT_MENU, self.OnExit, id=wx.ID_EXIT)
        
        self.Bind(wx.EVT_MENU, self.OnCmdMoveLeftButton, id=ActionManager.ID_PIC_MOVE_LEFT)
        self.Bind(wx.EVT_MENU, self.OnCmdMoveRightButton, id=ActionManager.ID_PIC_MOVE_RIGHT)
        self.Bind(wx.EVT_MENU, self.OnCmdRemoveButton, id=ActionManager.ID_PIC_REMOVE)

        self.Bind(wx.EVT_MENU, self.OnCmdRotateLeftButton, id=ActionManager.ID_PIC_ROTATE_CCW)
        self.Bind(wx.EVT_MENU, self.OnCmdRotateRightButton, id=ActionManager.ID_PIC_ROTATE_CW)
        self.Bind(wx.EVT_MENU, self.OnCmdMotionRandom, id=ActionManager.ID_PIC_MOTION_RANDOM)
        self.Bind(wx.EVT_MENU, self.OnCmdMotionCenter, id=ActionManager.ID_PIC_MOTION_CENTER)

        self.Bind(wx.EVT_MENU, self.OnImportPics, id=ActionManager.ID_PIC_IMPORT)

        self.Bind(wx.EVT_MENU, self.OnAbout, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnHelpIndex, id=wx.ID_HELP)
        for wxId in ActionManager.LANG_MAP.keys():
            self.Bind(wx.EVT_MENU, self.OnChangeLanguage, id=wxId)

        self.Bind(wx.EVT_MENU, self.OnRenderFilmstrip, id=ActionManager.ID_RENDER_FILMSTRIP)
        self.Bind(wx.EVT_MENU, self.OnShowFrameJobManager, id=ActionManager.ID_JOB_QUEUE)
        
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectChanged, id=wx.ID_SAVE)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectActive, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectActive, id=ActionManager.ID_PIC_IMPORT)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectActive, id=ActionManager.ID_PROJECT_EXPORT)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectActive, id=ActionManager.ID_PROJECT_PROPS)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectActive, id=ActionManager.ID_PROJECT_CLOSE)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectReady, id=ActionManager.ID_RENDER_FILMSTRIP)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckImageSelected, id=ActionManager.ID_PIC_REMOVE)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckImageSelected, id=ActionManager.ID_PIC_ROTATE_CCW)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckImageSelected, id=ActionManager.ID_PIC_ROTATE_CW)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckImageSelected, id=ActionManager.ID_PIC_MOVE_LEFT)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckImageSelected, id=ActionManager.ID_PIC_MOVE_RIGHT)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckImageSelected, id=ActionManager.ID_PIC_MOTION_RANDOM)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckImageSelected, id=ActionManager.ID_PIC_MOTION_CENTER)
        
        self.SetInitialSize((720, 680))
        
        id1 = wx.NewId()
        id2 = wx.NewId()
        at = wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_F1, wx.ID_HELP_CONTENTS),
                                  (wx.ACCEL_CTRL, wx.WXK_PAGEDOWN, id1),
                                  (wx.ACCEL_CTRL, wx.WXK_PAGEUP, id2)])
        self.SetAcceleratorTable(at)
        self.Bind(wx.EVT_MENU, self.OnHelpContent, id=wx.ID_HELP_CONTENTS)
        self.Bind(wx.EVT_MENU, self.OnPageNext, id=id1)
        self.Bind(wx.EVT_MENU, self.OnPagePrev, id=id2)

        self.actionManager.SelectLanguage(Settings().GetLanguage())
        JobManager().AddVisual(self)
        
        self.Bind(EVT_REGISTER_JOB, self.OnRegisterJob)
        self.Bind(EVT_REMOVE_JOB, self.OnRemoveJob)
        
    def ObservableUpdate(self, obj, arg):
        if obj is self.__GetCurrentProject():
            self.UpdateStatusText()

    def OnRegisterJob(self, event):
        job = event.GetJob()
        if isinstance(job, RenderJob):
            self.statusBar.SetStatusText(_(u"Rendering in progress..."), 3)
    
    def OnRemoveJob(self, event):
        self.statusBar.SetStatusText("", 3)

    def OnStatusBarLeftDown(self, event):
        if self.statusBar.GetFieldRect(3).Contains(event.GetPosition()) \
        and self.statusBar.GetStatusText(3) != "":
            self.frmJobManager.Show()

    def __GetCurrentPnlPfs(self):
        sel = self.notebook.GetSelection()
        page = self.notebook.GetPage(sel)
        if isinstance(page, PnlPfsProject):
            return page
    
    def __GetCurrentProject(self):
        page = self.__GetCurrentPnlPfs()
        if page:
            return page.GetProject()
        return None
    
    def OnCheckProjectActive(self, event):
        pnl = self.__GetCurrentPnlPfs()
        event.Enable(pnl is not None)
    def OnCheckProjectChanged(self, event):
        pnl = self.__GetCurrentPnlPfs()
        if pnl:
            event.Enable(pnl.HasChanged())
        else:
            event.Enable(False)
    def OnCheckProjectReady(self, event):
        pnl = self.__GetCurrentPnlPfs()
        if pnl:
            event.Enable(pnl.IsReady())
        else:
            event.Enable(False)
    def OnCheckImageSelected(self, event):
        pnl = self.__GetCurrentPnlPfs()
        if pnl:
            value = pnl.IsPictureSelected()
            kind = pnl.GetSelectedImageState()
            if event.GetId() == ActionManager.ID_PIC_MOVE_LEFT:
                # FIXME: does not work with multiselect
                value = kind not in ['first', 'none'] and value
            elif event.GetId() == ActionManager.ID_PIC_MOVE_RIGHT:
                # FIXME: does not work with multiselect
                value = kind not in ['last', 'none'] and value
            event.Enable(value)
        else:
            event.Enable(False)
    
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
    
    def OnPageChanged(self, event):
        sel = event.GetSelection()
        if sel == 0:
            self.notebook.SetWindowStyleFlag(0)
            self.SetTitle(Constants.APP_NAME)
        else:
            page = self.notebook.GetPage(sel)
            self.notebook.SetWindowStyleFlag(wx.aui.AUI_NB_CLOSE_ON_ACTIVE_TAB)
            filepath = page.GetProject().GetFilename()
            self.SetTitle(Constants.APP_NAME + u' - ' + Decode(filepath))
            
        self.UpdateStatusText()
        
    def OnPageNext(self, event):
        idx = self.notebook.GetSelection()
        idx += 1
        if idx < self.notebook.GetPageCount():
            self.notebook.SetSelection(idx)
    
    def OnPagePrev(self, event):
        idx = self.notebook.GetSelection()
        idx -= 1
        if idx >=0:
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
    
    def OnCloseFrameJobManager(self, event):
        self.frmJobManager.Show(False)
        
    def OnShowFrameJobManager(self, event):
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

    def OnExit(self, event):
        self.Close()

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
        
    def OnProjectNew(self, event):
        dlg = DlgProjectProps(self)
        if dlg.ShowModal() == wx.ID_OK:
            photoFilmStrip = dlg.GetProject()
            self.NewProject(photoFilmStrip)
        dlg.Destroy()
        
    def OnProjectLoad(self, event):
        dlg = wx.FileDialog(self, _(u"Select %s-Project") % Constants.APP_NAME, 
                            Settings().GetProjectPath(), "", 
                            Constants.APP_NAME + u'-' + _(u"Project") + " (*.pfs)|*.pfs", 
                            wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.LoadProject(dlg.GetPath())
            
    def OnProjectSave(self, event):
        pnlPfs = self.__GetCurrentPnlPfs()
        prj = self.__GetCurrentProject()
        if prj:
            if self.SaveProject(prj.GetFilename(), False):
                pnlPfs.SetChanged(False)

    def OnProjectSaveAs(self, event):
        prj = self.__GetCurrentProject()
        if prj is None:
            return
        curFilePath = prj.GetFilename()
        dlg = wx.FileDialog(self, _(u"Save %s-Project") % Constants.APP_NAME, 
                            Settings().GetProjectPath(), 
                            curFilePath, 
                            Constants.APP_NAME + u'-' + _(u"Project") + " (*.pfs)|*.pfs", 
                            wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            filepath = dlg.GetPath()
            if os.path.splitext(filepath)[1].lower() != ".pfs":
                filepath += ".pfs"
                
            if os.path.isfile(filepath):
                dlg2 = wx.MessageDialog(self,
                                        _(u"Overwrite existing file '%s'?") % filepath, 
                                        _(u"Question"),
                                        wx.YES_NO | wx.ICON_QUESTION)
                if dlg2.ShowModal() == wx.ID_NO:
                    return False
                
            return self.SaveProject(filepath, False)
        return False
    
    def OnProjectClose(self, event):
        sel = self.notebook.GetSelection()
        if self.ClosePage(sel):
            self.notebook.DeletePage(sel)
    
    def OnProjectExport(self, event):
        prj = self.__GetCurrentProject()
        if prj is None:
            return
        curFilePath = prj.GetFilename()
        dlg = wx.FileDialog(self, _(u"Export %s-Project") % Constants.APP_NAME, 
                            Settings().GetProjectPath(), 
                            curFilePath, 
                            u"%s %s-%s %s" % (_(u"Portable"), Constants.APP_NAME, _(u"Project"), "(*.ppfs)|*.ppfs"), 
                            wx.FD_SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            filepath = dlg.GetPath()
            if os.path.splitext(filepath)[1].lower() != ".ppfs":
                filepath += ".ppfs"
            self.SaveProject(filepath, True)

    def OnProjectImport(self, event):
        dlg = wx.FileDialog(self, _(u"Import %s-Project") % Constants.APP_NAME, 
                            Settings().GetProjectPath(), "", 
                            u"%s %s-%s %s" % (_(u"Portable"), Constants.APP_NAME, _(u"Project"), "(*.ppfs)|*.ppfs"), 
                            wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.LoadProject(dlg.GetPath(), True)
            
    def OnProjectProps(self, event):
        pnlPfs = self.__GetCurrentPnlPfs()
        if pnlPfs is None:
            return
        
        dlg = DlgProjectProps(self, self.__GetCurrentProject())
        if dlg.ShowModal() == wx.ID_OK:
            dlg.GetProject()
            pnlPfs.UpdateProperties()
        dlg.Destroy()

    def OnHelpIndex(self, event):
        HelpViewer().DisplayID(HelpViewer.ID_INDEX)
        event.Skip()
    def OnHelpContent(self, event):
        HelpViewer().DisplayID(HelpViewer.ID_CREATE_PFS)
        event.Skip()
        
    def OnCmdMoveLeftButton(self, event):
        sel = self.notebook.GetSelection()
        if sel > 0:
            page = self.notebook.GetPage(sel)
            page.OnCmdMoveLeftButton(event)
    def OnCmdMoveRightButton(self, event):
        sel = self.notebook.GetSelection()
        if sel > 0:
            page = self.notebook.GetPage(sel)
            page.OnCmdMoveRightButton(event)
    def OnCmdRemoveButton(self, event):
        sel = self.notebook.GetSelection()
        if sel > 0:
            page = self.notebook.GetPage(sel)
            page.OnCmdRemoveButton(event)
    def OnCmdRotateLeftButton(self, event):
        sel = self.notebook.GetSelection()
        if sel > 0:
            page = self.notebook.GetPage(sel)
            page.pnlEditPicture.OnCmdRotateLeftButton(event)
    def OnCmdRotateRightButton(self, event):
        sel = self.notebook.GetSelection()
        if sel > 0:
            page = self.notebook.GetPage(sel)
            page.pnlEditPicture.OnCmdRotateRightButton(event)
    def OnCmdMotionRandom(self, event):
        sel = self.notebook.GetSelection()
        if sel > 0:
            page = self.notebook.GetPage(sel)
            page.OnMotionRandom()
    def OnCmdMotionCenter(self, event):
        sel = self.notebook.GetSelection()
        if sel > 0:
            page = self.notebook.GetPage(sel)
            page.OnMotionCenter()
    def OnImportPics(self, event):
        sel = self.notebook.GetSelection()
        if sel > 0:
            page = self.notebook.GetPage(sel)
            page.OnImportPics(event)

    def OnRenderFilmstrip(self, event):
        sel = self.notebook.GetSelection()
        if sel > 0:
            page = self.notebook.GetPage(sel)
            photoFilmStrip = page.GetProject()
            dlg = DlgRender(self, photoFilmStrip)
            dlg.ShowModal()
#            dlg.Destroy()
            
    def ClosePage(self, idx):
        page = self.notebook.GetPage(idx)
        if self.CheckAndAskSaving(page):
            page.Close()
            return True
        else:
            return False

    def AddFileToHistory(self, filename):
        fileList = Settings().GetFileHistory()
        if filename in fileList:
            fileList.remove(filename)
        fileList.insert(0, filename)
        Settings().SetFileHistory(fileList)
        
    def CheckAndAskSaving(self, pnlPfs):
        if pnlPfs.HasChanged():
            filepath = pnlPfs.GetProject().GetFilename()
                
            dlg = wx.MessageDialog(self,
                                   _(u"'%s' has been modified. Save changes?") % Decode(filepath), 
                                   _(u"Question"),
                                   wx.YES_NO | wx.CANCEL | wx.ICON_EXCLAMATION)
            response = dlg.ShowModal()
            dlg.Destroy()
            
            if response == wx.ID_CANCEL:
                return False
            elif response == wx.ID_YES and not self.SaveProject(filepath, False):
                return False
        return True

    def UpdateStatusText(self):
        page = self.__GetCurrentPnlPfs()
        if page is None:
            self.statusBar.SetStatusText(Constants.APP_URL, 1)
            self.statusBar.SetStatusText("%s %s" % (Constants.APP_NAME, Constants.APP_VERSION), 2)
        else:
            project = page.GetProject()

            imgCount = len(project.GetPictures())
            totalTime = project.GetDuration(False)
            if project.GetTimelapse():
                # TODO: calc from image count
                totalTime = 1
                imgCount = 0
            elif totalTime == -1:
                # TODO: calc from audio files
                totalTime = 0
            elif totalTime is None:
                totalTime = project.GetDuration(True)

            self.statusBar.SetStatusText("%s: %d" % (_(u"Images"), imgCount), 1)

            minutes = totalTime / 60
            seconds = totalTime % 60
            self.statusBar.SetStatusText("%s: %02d:%02d" % (_(u"Duration"), 
                                                            minutes, 
                                                            seconds), 2)

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
        
#            self.pnlWelcome.RefreshPage() # crashes on unix
            wx.CallAfter(self.pnlWelcome.RefreshPage)
    
    def SaveProject(self, filepath, includePics):
        project = self.__GetCurrentProject()
        prjFile = WxProjectFile(self, project, filepath)
        try:
            prjFile.Save(includePics)
        except StandardError, err:
            dlg = wx.MessageDialog(self,
                                   _(u"Could not save the file '%(file)s': %(errMsg)s") % \
                                            {'file': Decode(filepath),
                                             'errMsg': unicode(err)}, 
                                   _(u"Question"),
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if not includePics:
            self.AddFileToHistory(filepath)
            
#            self.pnlWelcome.RefreshPage() # crashes on unix
            wx.CallAfter(self.pnlWelcome.RefreshPage)
        
        return True
    
        
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


