# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2010 Jens Goepfert
#

import os

import wx

from photofilmstrip import Constants
from photofilmstrip.lib.Settings import Settings
from photofilmstrip.lib.util import IsPathWritable

from photofilmstrip.core.Aspect import Aspect
from photofilmstrip.core.Project import Project

from photofilmstrip.gui.Art import Art
from photofilmstrip.gui.ctrls.PnlDlgHeader import PnlDlgHeader


class DlgNewProject(wx.Dialog):

    def _InitSizers(self):
        szMain = wx.BoxSizer(orient=wx.VERTICAL)

        szCtrls = wx.GridBagSizer(hgap=self.FromDIP(8), vgap=self.FromDIP(8))

        szCmds = wx.BoxSizer(orient=wx.HORIZONTAL)

        szMain.Add(self.pnlHdr, 0, border=0, flag=wx.EXPAND)
        szMain.Add(szCtrls, 0, border=self.FromDIP(8), flag=wx.ALL | wx.EXPAND)
        szMain.Add(self.staticLine, 0, border=0, flag=wx.EXPAND)
        szMain.Add(szCmds, 0, border=self.FromDIP(8), flag=wx.ALL | wx.ALIGN_RIGHT)

        szCtrls.Add(self.stProject, (0, 0), border=0,
              flag=wx.ALIGN_CENTER_VERTICAL, span=(1, 1))
        szCtrls.Add(self.tcProject, (0, 1), border=0, flag=wx.EXPAND, span=(1, 1))
        szCtrls.Add(self.stFolder, (1, 0), border=0,
              flag=wx.ALIGN_CENTER_VERTICAL, span=(1, 1))
        szCtrls.Add(self.tcFolder, (1, 1), border=0,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, span=(1, 1))
        szCtrls.Add(self.cmdBrowseFolder, (1, 2), border=0, flag=0,
              span=(1, 1))
        szCtrls.Add(self.stAspect, (2, 0), border=0,
              flag=wx.ALIGN_CENTER_VERTICAL, span=(1, 1))
        szCtrls.Add(self.choiceAspect, (2, 1), border=0, flag=wx.EXPAND, span=(1,
              1))
        szCtrls.Add(self.cbPortraitMode, (3, 1), border=0, flag=wx.EXPAND, span=(1,
              1))
        szCtrls.AddGrowableCol(1)

        szCmds.Add(self.cmdCancel, 0, border=0, flag=0)
        szCmds.AddSpacer(self.FromDIP(8))
        szCmds.Add(self.cmdOk, 0, border=0, flag=0)

        self.SetSizer(szMain)

    def _InitCtrls(self):
        self.pnlHdr = PnlDlgHeader(self)

        self.stProject = wx.StaticText(self,
              label=_("Project name:"), name="stProject")

        self.tcProject = wx.TextCtrl(self, name="tcProject", value="")

        self.stFolder = wx.StaticText(self,
              label=_("Folder:"), name="stFolder")

        self.tcFolder = wx.TextCtrl(self,
              name="tcFolder", style=wx.TE_READONLY, value="")

        self.cmdBrowseFolder = wx.BitmapButton(self,
              bitmap=Art.GetBitmapBundle('PFS_FOLDER_OPEN', wx.ART_TOOLBAR),
              name="cmdBrowseFolder",
              style=wx.BU_AUTODRAW)
        self.cmdBrowseFolder.Bind(wx.EVT_BUTTON, self.OnCmdBrowseFolderButton)

        self.stAspect = wx.StaticText(self,
              label=_("Aspect ratio:"), name="stAspect")

        self.choiceAspect = wx.Choice(self, choices=[], name="choiceAspect")

        self.cbPortraitMode = wx.CheckBox(self, label=_("Portrait mode"), name="cbPortraitMode")

        self.staticLine = wx.StaticLine(self)

        self.cmdCancel = wx.Button(self, id=wx.ID_CANCEL, label=_("&Cancel"),
              name="cmdCancel")
        self.cmdOk = wx.Button(self, id=wx.ID_OK, label=_("&Ok"),
              name="cmdOk")
        self.cmdOk.Bind(wx.EVT_BUTTON, self.OnCmdOkButton, id=wx.ID_OK)

    def __init__(self, parent, title):
        wx.Dialog.__init__(self, parent, name="DlgNewProject",
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
                           title=title)

        self._InitCtrls()
        self._InitSizers()

        self.pnlHdr.SetTitle(title)
        self.pnlHdr.SetBitmap(Art.GetBitmapBundle('PFS_ICON', wx.ART_MESSAGE_BOX))

        self.choiceAspect.Append(Aspect.ASPECT_16_9)
        self.choiceAspect.Append(Aspect.ASPECT_16_10)
        self.choiceAspect.Append(Aspect.ASPECT_4_3)
        self.choiceAspect.Append(Aspect.ASPECT_3_2)

        self.choiceAspect.Select(0)

        self.tcProject.SetMinSize(self.FromDIP(wx.Size(300, -1)))
        self.tcFolder.SetMinSize(self.FromDIP(wx.Size(300, -1)))
        self.choiceAspect.SetMinSize(self.FromDIP(wx.Size(300, -1)))

        self.tcProject.SetValue(_("Unnamed project"))
        self.tcProject.SelectAll()
        self.tcProject.SetFocus()

        projPath = Settings().GetProjectPath()
        if not projPath:
            projPath = os.path.join(wx.GetHomeDir(), _("My PhotoFilmStrips"))
            Settings().SetProjectPath(projPath)
        self.tcFolder.SetValue(projPath)

        self.SetInitialSize(self.GetEffectiveMinSize())
        self.Fit()
        self.CenterOnParent()
        self.SetFocus()

    def OnCmdBrowseFolderButton(self, event):
        dlg = wx.DirDialog(self,
                           _("Browse for folder"),
                           defaultPath=self.tcFolder.GetValue())
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if self.__ValidateOutDir(path):
                self.tcFolder.SetValue(path)
                Settings().SetProjectPath(path)
        dlg.Destroy()

    def OnCmdOkButton(self, event):
        if self.__ValidateOutDir() and self.__ValidateProjName():
            event.Skip()

    def __ValidateOutDir(self, path=None):
        if path is None:
            path = self.tcFolder.GetValue().strip()

        if not os.path.isdir(path):
            dlg = wx.MessageDialog(self,
                                   _("Folder does not exists! Do you want %s to create it?") % Constants.APP_NAME,
                                   _("Question"),
                                   wx.YES_NO | wx.ICON_QUESTION)
            resp = dlg.ShowModal()
            dlg.Destroy()
            if resp == wx.ID_YES:
                try:
                    os.makedirs(path)
                except Exception as err:
                    dlg = wx.MessageDialog(self,
                                           _("Cannot create folder: %s") % str(err),
                                           _("Error"),
                                           wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
            else:
                return False
        else:
            if not IsPathWritable(path):
                dlg = wx.MessageDialog(self,
                                       _("Cannot write into folder!"),
                                       _("Error"),
                                       wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        return True

    def __ValidateProjName(self):
        projName = self.tcProject.GetValue().strip()
        projName = projName.strip(".")
        projPath = os.path.join(self.tcFolder.GetValue().strip(), projName)
        if not projName:
            self.pnlHdr.SetErrorMessage(_("The project name must be filled."))
            return False
        elif not os.path.exists(projPath):
            try:
                os.makedirs(projPath)
            except Exception:
                self.pnlHdr.SetErrorMessage(_("The project name contains invalid characters."))
                return False
            os.removedirs(projPath)
            return True
        else:
            self.pnlHdr.SetErrorMessage("")
            return True

    def __GetProjectPath(self):
        projName = self.tcProject.GetValue().strip()
        projName = projName.strip(".")
        filepath = os.path.join(self.tcFolder.GetValue().strip(),
                                projName,
                                "%s.pfs" % projName)
        return filepath

    def GetProject(self):
        project = Project(self.__GetProjectPath())
        project.SetTimelapse(False)
        aspect = self.choiceAspect.GetStringSelection()
        if self.cbPortraitMode.GetValue():
            aspect = Aspect.ToPortraitMode(aspect)
        project.SetAspect(aspect)
        return project
