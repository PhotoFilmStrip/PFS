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

from core.PhotoFilmStrip import PhotoFilmStrip

from lib.Settings import Settings

from gui.DlgRender import DlgRender
from gui.PnlWelcome import PnlWelcome
from gui.ActionManager import ActionManager
from gui.HelpViewer import HelpViewer
from gui.DlgProjectProps import DlgProjectProps
from gui.PnlPfsProject import PnlPfsProject, EVT_UPDATE_STATUSBAR

from res.license import licenseText


class FrmMain(wx.Frame):
    
    def __init__(self):
        wx.Frame.__init__(self, None, -1, name=u'FrmMain',
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.DEFAULT_FRAME_STYLE | wx.TAB_TRAVERSAL,
              title='PhotoFilmStrip')
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.SetTitle(Settings.APP_NAME)
        
        iconBundle = wx.IconBundle()
        iconBundle.AddIcon(wx.ArtProvider_GetIcon("PFS_ICON_32", wx.ART_OTHER))
        iconBundle.AddIcon(wx.ArtProvider_GetIcon("PFS_ICON_48", wx.ART_OTHER))
        self.SetIcons(iconBundle)
        
        self.statusBar = wx.StatusBar(self)
        self.statusBar.SetFieldsCount(3)
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
        
        self.Bind(wx.EVT_MENU, self.OnProjectNew, id=wx.ID_NEW)
        self.Bind(wx.EVT_MENU, self.OnProjectLoad, id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, self.OnProjectSave, id=wx.ID_SAVE)
        self.Bind(wx.EVT_MENU, self.OnProjectSaveAs, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_MENU, self.OnProjectExport, id=ActionManager.ID_PROJECT_EXPORT)
        self.Bind(wx.EVT_MENU, self.OnProjectImport, id=ActionManager.ID_PROJECT_IMPORT)
        self.Bind(wx.EVT_MENU, self.OnProjectProps, id=ActionManager.ID_PROJECT_PROPS)
        self.Bind(wx.EVT_MENU, self.OnClose, id=wx.ID_EXIT)
        
        self.Bind(wx.EVT_MENU, self.OnCmdMoveLeftButton, id=ActionManager.ID_PIC_MOVE_LEFT)
        self.Bind(wx.EVT_MENU, self.OnCmdMoveRightButton, id=ActionManager.ID_PIC_MOVE_RIGHT)
        self.Bind(wx.EVT_MENU, self.OnCmdRemoveButton, id=ActionManager.ID_PIC_REMOVE)

        self.Bind(wx.EVT_MENU, self.OnCmdRotateLeftButton, id=ActionManager.ID_PIC_ROTATE_CCW)
        self.Bind(wx.EVT_MENU, self.OnCmdRotateRightButton, id=ActionManager.ID_PIC_ROTATE_CW)

        self.Bind(wx.EVT_MENU, self.OnImportPics, id=ActionManager.ID_PIC_IMPORT)

        self.Bind(wx.EVT_MENU, self.OnAbout, id=wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnHelpIndex, id=wx.ID_HELP)
        self.Bind(wx.EVT_MENU, self.OnChangeLanguage, id=ActionManager.ID_LANG_EN)
        self.Bind(wx.EVT_MENU, self.OnChangeLanguage, id=ActionManager.ID_LANG_FR)
        self.Bind(wx.EVT_MENU, self.OnChangeLanguage, id=ActionManager.ID_LANG_DE)
        self.Bind(wx.EVT_MENU, self.OnChangeLanguage, id=ActionManager.ID_LANG_PT)
        self.Bind(wx.EVT_MENU, self.OnChangeLanguage, id=ActionManager.ID_LANG_CS)

        self.Bind(wx.EVT_MENU, self.OnRenderFilmstrip, id=ActionManager.ID_RENDER_FILMSTRIP)
        
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectChanged, id=wx.ID_SAVE)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectActive, id=wx.ID_SAVEAS)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectActive, id=ActionManager.ID_PIC_IMPORT)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectActive, id=ActionManager.ID_PROJECT_EXPORT)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectActive, id=ActionManager.ID_PROJECT_PROPS)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckProjectReady, id=ActionManager.ID_RENDER_FILMSTRIP)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckImageSelected, id=ActionManager.ID_PIC_REMOVE)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckImageSelected, id=ActionManager.ID_PIC_ROTATE_CCW)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckImageSelected, id=ActionManager.ID_PIC_ROTATE_CW)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckImageSelected, id=ActionManager.ID_PIC_MOVE_LEFT)
        self.Bind(wx.EVT_UPDATE_UI, self.OnCheckImageSelected, id=ActionManager.ID_PIC_MOVE_RIGHT)
        
        self.SetInitialSize((720, 680))
        
        at = wx.AcceleratorTable([(wx.ACCEL_NORMAL, wx.WXK_F1, wx.ID_HELP_CONTENTS)])
        self.SetAcceleratorTable(at)
        self.Bind(wx.EVT_MENU, self.OnHelpContent, id=wx.ID_HELP_CONTENTS)

        self.actionManager.SelectLanguage(Settings().GetLanguage())
        
    def __GetCurrentPnlPfs(self):
        sel = self.notebook.GetSelection()
        if sel > 0:
            return self.notebook.GetPage(sel)
    
    def __GetCurrentPhotoFilmStrip(self):
        page = self.__GetCurrentPnlPfs()
        if page:
            return page.GetPhotoFilmStrip()
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
                value = kind not in ['first', 'none'] and value
            elif event.GetId() == ActionManager.ID_PIC_MOVE_RIGHT:
                value = kind not in ['last', 'none'] and value
            event.Enable(value)
        else:
            event.Enable(False)
    
    def OnChangeLanguage(self, event):
        lang = ActionManager.LANG_MAP.get(event.GetId(), "en")
        Settings().SetLanguage(lang)
        Settings().InitLanguage()
        dlg = wx.MessageDialog(self,
                               _(u"You must restart %s for your new language setting to take effect.") % Settings.APP_NAME,
                               _(u"Information"),
                               wx.ICON_INFORMATION | wx.OK)
        dlg.ShowModal()
        dlg.Destroy()
    
    def OnPageChanged(self, event):
        sel = event.GetSelection()
        if sel == 0:
            self.notebook.SetWindowStyleFlag(0)
            self.SetTitle(Settings.APP_NAME)
        else:
            page = self.notebook.GetPage(sel)
            self.notebook.SetWindowStyleFlag(wx.aui.AUI_NB_CLOSE_ON_ACTIVE_TAB)
            filepath = page.GetPhotoFilmStrip().GetFilename()
            self.SetTitle(Settings.APP_NAME + ' - ' + filepath)
            
        self.UpdateStatusText(None)
        
    def OnPageClose(self, event):
        sel = event.GetSelection()
        if sel == 0:
            event.Veto()
            return
        else:
            page = self.notebook.GetPage(sel)
            if self.CheckAndAskSaving(page):
                page.Close()
                event.Skip()
            else:
                event.Veto()
    
    def OnClose(self, event):
        while self.notebook.GetPageCount() > 1:
            idx = 1
            self.notebook.SetSelection(idx)
            page = self.notebook.GetPage(idx)
            if self.CheckAndAskSaving(page):
                page.Close()
                self.notebook.DeletePage(idx)
            else:
                return
        event.Skip()

    def OnAbout(self, event):
        info = wx.AboutDialogInfo()
        info.Name = Settings.APP_NAME
        info.Version = Settings.APP_VERSION
        info.Copyright = u"(C) 2010 %s" % Settings.DEVELOPERS[0]
        info.Description = wordwrap(_("PhotoFilmStrip creates movies out of your pictures in just 3 steps. First select your photos, customize the motion path and render the video. There are several output possibilities for VCD, SVCD, DVD up to FULL-HD."), 
                                    350, 
                                    wx.ClientDC(self))
        info.WebSite = (Settings.APP_URL, "%s %s" % (Settings.APP_NAME, _(u"online")))
        info.Developers = Settings.DEVELOPERS + [
                                "",
                                _("Translators"),
                                "Teza Lprod - http://lprod.org"]

        info.License = wordwrap(licenseText, 500, wx.ClientDC(self))

        wx.AboutBox(info)
        
    def OnProjectNew(self, event):
        dlg = DlgProjectProps(self)
        if dlg.ShowModal() == wx.ID_OK:
            photoFilmStrip = dlg.GetPhotoFilmStrip()
            self.NewProject(photoFilmStrip)
        dlg.Destroy()
        
    def OnProjectLoad(self, event):
        dlg = wx.FileDialog(self, _(u"Select %s-Project") % Settings.APP_NAME, 
                            Settings().GetProjectPath(), "", 
                            Settings.APP_NAME + u'-' + _(u"Project") + " (*.pfs)|*.pfs", 
                            wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.LoadProject(dlg.GetPath())
            
    def OnProjectSave(self, event):
        pnlPfs = self.__GetCurrentPnlPfs()
        pfs = self.__GetCurrentPhotoFilmStrip()
        if pfs:
            if self.SaveProject(pfs.GetFilename(), False):
                pnlPfs.SetChanged(False)

    def OnProjectSaveAs(self, event):
        pfs = self.__GetCurrentPhotoFilmStrip()
        if pfs is None:
            return
        curFilePath = pfs.GetFilename()
        dlg = wx.FileDialog(self, _(u"Save %s-Project") % Settings.APP_NAME, 
                            Settings().GetProjectPath(), 
                            curFilePath, 
                            Settings.APP_NAME + u'-' + _(u"Project") + " (*.pfs)|*.pfs", 
                            wx.SAVE)
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
    
    def OnProjectExport(self, event):
        pfs = self.__GetCurrentPhotoFilmStrip()
        if pfs is None:
            return
        curFilePath = pfs.GetFilename()
        dlg = wx.FileDialog(self, _(u"Export %s-Project") % Settings.APP_NAME, 
                            Settings().GetProjectPath(), 
                            curFilePath, 
                            u"%s %s-%s %s" % (_(u"Portable"), Settings.APP_NAME, _(u"Project"), "(*.ppfs)|*.ppfs"), 
                            wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            filepath = dlg.GetPath()
            if os.path.splitext(filepath)[1].lower() != ".ppfs":
                filepath += ".ppfs"
            self.SaveProject(filepath, True)

    def OnProjectImport(self, event):
        dlg = wx.FileDialog(self, _(u"Import %s-Project") % Settings.APP_NAME, 
                            Settings().GetProjectPath(), "", 
                            u"%s %s-%s %s" % (_(u"Portable"), Settings.APP_NAME, _(u"Project"), "(*.ppfs)|*.ppfs"), 
                            wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.LoadProject(dlg.GetPath(), True)
            
    def OnProjectProps(self, event):
        pnlPfs = self.__GetCurrentPnlPfs()
        if pnlPfs is None:
            return
        
        dlg = DlgProjectProps(self, self.__GetCurrentPhotoFilmStrip())
        if dlg.ShowModal() == wx.ID_OK:
            dlg.GetPhotoFilmStrip()
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
    def OnImportPics(self, event):
        sel = self.notebook.GetSelection()
        if sel > 0:
            page = self.notebook.GetPage(sel)
            page.OnImportPics(event)

    def OnRenderFilmstrip(self, event):
        sel = self.notebook.GetSelection()
        if sel > 0:
            page = self.notebook.GetPage(sel)
            photoFilmStrip = page.GetPhotoFilmStrip()
            dlg = DlgRender(self, photoFilmStrip)
            dlg.ShowModal()
            dlg.Destroy()

    def AddFileToHistory(self, filename):
        fileList = Settings().GetFileHistory()
        if filename in fileList:
            fileList.remove(filename)
        fileList.insert(0, filename)
        Settings().SetFileHistory(fileList)
        
    def CheckAndAskSaving(self, pnlPfs):
        if pnlPfs.HasChanged():
            filepath = pnlPfs.GetPhotoFilmStrip().GetFilename()
                
            dlg = wx.MessageDialog(self,
                                   _(u"'%s' has been modified. Save changes?") % filepath, 
                                   _(u"Question"),
                                   wx.YES_NO | wx.CANCEL | wx.ICON_QUESTION)
            response = dlg.ShowModal()
            dlg.Destroy()
            
            if response == wx.ID_CANCEL:
                return False
            elif response == wx.ID_YES and not self.SaveProject(filepath, False):
                return False
        return True

    def UpdateStatusText(self, event):
        page = self.__GetCurrentPnlPfs()
        if page is None:
            self.statusBar.SetStatusText(Settings.APP_URL, 1)
            self.statusBar.SetStatusText("%s %s" % (Settings.APP_NAME, Settings.APP_VERSION), 2)
        else:
            photoFilmStrip = page.GetPhotoFilmStrip()

            pics = photoFilmStrip.GetPictures()
    
            imgCount = len(pics)
            self.statusBar.SetStatusText("%s: %d" % (_(u"Images"), imgCount), 1)
            
            totalTime = photoFilmStrip.GetDuration()
            minutes = totalTime / 60
            seconds = totalTime % 60
            self.statusBar.SetStatusText("%s: %02d:%02d" % (_(u"Duration"), 
                                                            minutes, 
                                                            seconds), 2)

    def NewProject(self, photoFilmStrip):
        pnl = PnlPfsProject(self.notebook, photoFilmStrip)
        pnl.Bind(EVT_UPDATE_STATUSBAR, self.UpdateStatusText)
        filepath = os.path.basename(photoFilmStrip.GetFilename())
        self.notebook.AddPage(pnl, os.path.basename(filepath), True)
        return pnl
#
    def LoadProject(self, filepath, skipHistory=False):
        for idx in range(1, self.notebook.GetPageCount()):
            page = self.notebook.GetPage(idx)
            if page.GetPhotoFilmStrip().GetFilename() == filepath:
                self.notebook.SetSelection(idx)
                return
        
        photoFilmStrip = PhotoFilmStrip(filepath)

        pnl = self.NewProject(photoFilmStrip)
        photoFilmStrip.SetUserInteractionHandler(pnl)
        
        if not photoFilmStrip.Load(filepath):
            dlg = wx.MessageDialog(self,
                                   _(u"Invalid %(app)s-Project: %(file)s") % {"app": Settings.APP_NAME,
                                                                              "file": filepath}, 
                                   _(u"Error"),
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        pics = photoFilmStrip.GetPictures()
        
        pnl.InsertPictures(pics)
        pnl.SetChanged(False)

        if not skipHistory:
            self.AddFileToHistory(filepath)
        
        Settings().SetProjectPath(os.path.dirname(filepath))
    
    def SaveProject(self, filepath, includePics):
        photoFilmStrip = self.__GetCurrentPhotoFilmStrip()
        try:
            photoFilmStrip.Save(filepath, includePics)
        except StandardError, err:
            dlg = wx.MessageDialog(self,
                                   _(u"Could not save the file '%(file)s': %(errMsg)s") % \
                                            {'file': filepath,
                                             'errMsg': unicode(err)}, 
                                   _(u"Question"),
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return False

        if not includePics:
            self.AddFileToHistory(filepath)
        
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


