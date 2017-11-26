# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2010 Jens Goepfert
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
import wx.lib.masked.timectrl

from photofilmstrip import Constants
from photofilmstrip.lib.Settings import Settings
from photofilmstrip.lib.util import IsPathWritable

from photofilmstrip.core.Aspect import Aspect
from photofilmstrip.core.Project import Project
from photofilmstrip.core.AudioPlayer import AudioPlayer

from photofilmstrip.gui.ctrls.PnlDlgHeader import PnlDlgHeader


class DlgProjectProps(wx.Dialog):

    def _InitSizers(self):
        self.szMain = wx.BoxSizer(orient=wx.VERTICAL)

        self.szCtrls = wx.GridBagSizer(hgap=8, vgap=8)

        self.szCmds = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.szAudioCmds = wx.BoxSizer(orient=wx.VERTICAL)

        self.szMain.AddWindow(self.pnlHdr, 0, border=0, flag=wx.EXPAND)
        self.szMain.AddSizer(self.szCtrls, 0, border=8, flag=wx.ALL | wx.EXPAND)
        self.szMain.AddWindow(self.staticLine1, 0, border=0, flag=wx.EXPAND)
        self.szMain.AddSizer(self.szCmds, 0, border=8, flag=wx.ALL | wx.ALIGN_RIGHT)

        self.szCtrls.AddWindow(self.stProject, (0, 0), border=0,
              flag=wx.ALIGN_CENTER_VERTICAL, span=(1, 1))
        self.szCtrls.AddWindow(self.tcProject, (0, 1), border=0, flag=wx.EXPAND, span=(1, 1))
        self.szCtrls.AddWindow(self.stFolder, (1, 0), border=0,
              flag=wx.ALIGN_CENTER_VERTICAL, span=(1, 1))
        self.szCtrls.AddWindow(self.tcFolder, (1, 1), border=0,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND, span=(1, 1))
        self.szCtrls.AddWindow(self.cmdBrowseFolder, (1, 2), border=0, flag=0,
              span=(1, 1))
        self.szCtrls.AddWindow(self.staticLine, (2, 0), border=0, flag=0, span=(1, 4))
        self.szCtrls.AddWindow(self.stAspect, (3, 0), border=0,
              flag=wx.ALIGN_CENTER_VERTICAL, span=(1, 1))
        self.szCtrls.AddWindow(self.choiceAspect, (3, 1), border=0, flag=wx.EXPAND, span=(1,
              1))

        self.szCtrls.AddWindow(self.stAudio, (4, 0), border=0,
              flag=wx.ALIGN_TOP, span=(1, 1))
        self.szCtrls.AddWindow(self.lvAudio, (4, 1), border=0,
              flag=wx.EXPAND, span=(1, 1))
        self.szCtrls.AddSizer(self.szAudioCmds, (4, 2), border=0,
              flag=0, span=(1, 1))

        self.szCtrls.AddWindow(self.cbTotalLength, (5, 0), border=0, flag=0, span=(1,
              1))
        self.szCtrls.AddWindow(self.rbAudio, (6, 0), border=32,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, span=(1, 1))
        self.szCtrls.AddWindow(self.rbTimelapse, (7, 0), border=32,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, span=(1, 1))
        self.szCtrls.AddWindow(self.rbManual, (8, 0), border=32,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, span=(1, 1))
        self.szCtrls.AddWindow(self.timeCtrlTotalLength, (8, 1), border=0, flag=0,
              span=(1, 1))

        self.szAudioCmds.AddWindow(self.cmdBrowseAudio,
                                   border=2, flag=wx.BOTTOM)
        self.szAudioCmds.AddWindow(self.cmdAudioPreview,
                                   border=2, flag=wx.BOTTOM)
        self.szAudioCmds.AddWindow(self.cmdAudioMoveUp,
                                   border=2, flag=wx.BOTTOM)
        self.szAudioCmds.AddWindow(self.cmdAudioMoveDown,
                                   border=2, flag=wx.BOTTOM)
        self.szAudioCmds.AddWindow(self.cmdAudioDel,
                                   border=2, flag=wx.BOTTOM)

        self.szCmds.AddWindow(self.cmdCancel, 0, border=0, flag=0)
        self.szCmds.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        self.szCmds.AddWindow(self.cmdOk, 0, border=0, flag=0)

        self.SetSizer(self.szMain)

    def _InitCtrls(self, prnt):
        self.pnlHdr = PnlDlgHeader(self)

        self.stProject = wx.StaticText(self,
              label=_(u'Project name:'), name=u'stProject')

        self.tcProject = wx.TextCtrl(self, name=u'tcProject', value=u'')

        self.staticLine2 = wx.StaticLine(self)

        self.stFolder = wx.StaticText(self,
              label=_(u'Folder:'), name=u'stFolder')

        self.tcFolder = wx.TextCtrl(self,
              name=u'tcFolder', style=wx.TE_READONLY, value=u'')

        self.cmdBrowseFolder = wx.BitmapButton(self,
              bitmap=wx.ArtProvider.GetBitmap('PFS_FOLDER_OPEN_16'),
              name=u'cmdBrowseFolder',
              style=wx.BU_AUTODRAW)
        self.cmdBrowseFolder.Bind(wx.EVT_BUTTON, self.OnCmdBrowseFolderButton)

        self.stAspect = wx.StaticText(self,
              label=_(u'Aspect ratio:'), name=u'stAspect')

        self.choiceAspect = wx.Choice(self, choices=[], name=u'choiceAspect')

        self.stAudio = wx.StaticText(self,
              label=_(u'Audio files:'), name=u'stAudio')

        self.lvAudio = wx.ListBox(self, style=wx.LB_SINGLE)
        self.lvAudio.Bind(wx.EVT_LISTBOX, self.OnControlStatusAudio)

        self.cmdBrowseAudio = wx.BitmapButton(self,
              bitmap=wx.ArtProvider.GetBitmap('PFS_MUSIC_16'),
              name=u'cmdBrowseAudio', style=wx.BU_AUTODRAW)
        self.cmdBrowseAudio.Bind(wx.EVT_BUTTON, self.OnCmdBrowseAudioButton)

        self.cmdAudioPreview = wx.BitmapButton(self,
              bitmap=wx.ArtProvider.GetBitmap('PFS_PLAY_PAUSE_16'),
              name=u'cmdAudioPreview', style=wx.BU_AUTODRAW)
        self.cmdAudioPreview.SetBitmapDisabled(wx.ArtProvider.GetBitmap('PFS_PLAY_PAUSE_D_16'))
        self.cmdAudioPreview.Bind(wx.EVT_BUTTON, self.OnCmdAudioPreviewButton)

        self.cmdAudioMoveUp = wx.BitmapButton(self,
              bitmap=wx.ArtProvider.GetBitmap('PFS_ARROW_UP_16'),
              name=u'cmdAudioMoveUp', style=wx.BU_AUTODRAW)
        self.cmdAudioMoveUp.SetBitmapDisabled(wx.ArtProvider.GetBitmap('PFS_ARROW_UP_D_16'))
        self.cmdAudioMoveUp.Bind(wx.EVT_BUTTON, self.OnCmdAudioMove)

        self.cmdAudioMoveDown = wx.BitmapButton(self,
              bitmap=wx.ArtProvider.GetBitmap('PFS_ARROW_DOWN_16'),
              name=u'cmdAudioMoveDown', style=wx.BU_AUTODRAW)
        self.cmdAudioMoveDown.SetBitmapDisabled(wx.ArtProvider.GetBitmap('PFS_ARROW_DOWN_D_16'))
        self.cmdAudioMoveDown.Bind(wx.EVT_BUTTON, self.OnCmdAudioMove)

        self.cmdAudioDel = wx.BitmapButton(self,
              bitmap=wx.ArtProvider.GetBitmap('PFS_REMOVE_16'),
              name=u'cmdAudioDel', style=wx.BU_AUTODRAW)
        self.cmdAudioDel.SetBitmapDisabled(wx.ArtProvider.GetBitmap('PFS_REMOVE_D_16'))
        self.cmdAudioDel.Bind(wx.EVT_BUTTON, self.OnCmdAudioDel)

        self.cbTotalLength = wx.CheckBox(self,
              label=_(u'Total length:'), name=u'cbTotalLength')
        self.cbTotalLength.SetValue(False)
        self.cbTotalLength.SetToolTipString(_(u'Overrides the duration of single pictures and gives the project this total length.'))
        self.cbTotalLength.Bind(wx.EVT_CHECKBOX, self.OnControlStatusTotalLength)

        self.rbManual = wx.RadioButton(self,
              label=_(u'User defined:'), name=u'rbManual')
        self.rbManual.Bind(wx.EVT_RADIOBUTTON, self.OnControlStatusTotalLength)

        self.timeCtrlTotalLength = wx.lib.masked.timectrl.TimeCtrl(self,
              display_seconds=True, fmt24hr=True,
              name=u'timeCtrlTotalLength', oob_color=wx.YELLOW,
              style=0, useFixedWidthFont=True, value='12:00:00 AM')
        self.timeCtrlTotalLength.Enable(False)

        self.rbAudio = wx.RadioButton(self,
              label=_(u'Fit to audio files'), name=u'rbAudio')
        self.rbAudio.Bind(wx.EVT_RADIOBUTTON, self.OnControlStatusTotalLength)

        self.rbTimelapse = wx.RadioButton(self,
              label=_(u'Timelapse'), name=u'rbTimelapse')
        self.rbTimelapse.Bind(wx.EVT_RADIOBUTTON, self.OnControlStatusTotalLength)

        self.staticLine = wx.StaticLine(self)

        self.staticLine1 = wx.StaticLine(self)

        self.cmdCancel = wx.Button(self, id=wx.ID_CANCEL, label=_(u'&Cancel'),
              name=u'cmdCancel')
        self.cmdCancel.Bind(wx.EVT_BUTTON, self.OnCmdCancelButton,
              id=wx.ID_CANCEL)

        self.cmdOk = wx.Button(self, id=wx.ID_OK, label=_(u'&Ok'),
              name=u'cmdOk')
        self.cmdOk.Bind(wx.EVT_BUTTON, self.OnCmdOkButton, id=wx.ID_OK)

        self._InitSizers()

    def __init__(self, parent, project=None):
        wx.Dialog.__init__(self, parent, name=u'DlgProjectProps',
                           style=wx.DEFAULT_DIALOG_STYLE,
                           title=_(u'Project properties'))
        self.Bind(wx.EVT_CLOSE, self.OnDlgProjectPropsClose)

        self._InitCtrls(parent)

        self.SetSizeHints(700, 250)
        self.szCtrls.AddGrowableCol(1)

        self.pnlHdr.SetTitle(_(u'PhotoFilmStrip project'))
        self.pnlHdr.SetBitmap(wx.ArtProvider.GetBitmap('PFS_ICON_48',
              wx.ART_TOOLBAR, (32, 32)))

        self.choiceAspect.Append(Aspect.ASPECT_16_9)
        self.choiceAspect.Append(Aspect.ASPECT_4_3)
        self.choiceAspect.Append(Aspect.ASPECT_3_2)
        self.choiceAspect.Select(0)

        self.tcProject.SetMinSize(wx.Size(300, -1))
        self.tcFolder.SetMinSize(wx.Size(300, -1))
        self.choiceAspect.SetMinSize(wx.Size(300, -1))
        self.timeCtrlTotalLength.SetMinSize(wx.Size(300, -1))
        self.lvAudio.SetMinSize(wx.Size(300, -1))

        defTime = wx.DateTime.Now()
        defTime.SetHMS(0, 0, 30)
        minTime = wx.DateTime.Now()
        minTime.SetHMS(0, 0, 1)
        maxTime = wx.DateTime.Now()
        maxTime.SetHMS(1, 59, 59)
        self.timeCtrlTotalLength.SetValue(defTime)
        self.timeCtrlTotalLength.SetMin(minTime)
        self.timeCtrlTotalLength.SetMax(maxTime)
        self.timeCtrlTotalLength.SetLimited(True)

        self.mediaCtrl = None

        self.__project = project

        if project is None:
            projName = _(u"Unnamed PhotoFilmStrip")
            self.tcProject.SetValue(projName)
            self.tcProject.SelectAll()
            self.tcProject.SetFocus()

            projPath = Settings().GetProjectPath()
            if not projPath:
                projPath = os.path.join(wx.GetHomeDir(), _(u"My PhotoFilmStrips"))
                Settings().SetProjectPath(projPath)
            self.tcFolder.SetValue(projPath)

            self.cbTotalLength.SetValue(False)
            self.rbManual.SetValue(True)
        else:
            projName = os.path.splitext(os.path.basename(project.GetFilename()))[0]
            self.tcProject.SetValue(projName)
            self.tcProject.Enable(False)

            self.tcFolder.SetValue(os.path.dirname(project.GetFilename()))
            self.tcFolder.Enable(False)
            self.cmdBrowseFolder.Enable(False)

            self.choiceAspect.SetStringSelection(project.GetAspect())
            self.choiceAspect.Enable(False)

            pfsDur = project.GetDuration(calc=True)
            duration = project.GetDuration(calc=False)
            if project.GetTimelapse():
                self.cbTotalLength.SetValue(True)
                self.rbTimelapse.SetValue(True)
            elif duration is None:
                self.cbTotalLength.SetValue(False)
            elif duration <= 0:
                self.cbTotalLength.SetValue(True)
                self.rbAudio.SetValue(True)
            else:
                self.cbTotalLength.SetValue(True)
                self.rbManual.SetValue(True)
                pfsDur = duration

            pfsDur = int(round(pfsDur))

            dur = wx.DateTime.Now()
            dur.SetHMS(0, pfsDur / 60, pfsDur % 60)
            try:
                self.timeCtrlTotalLength.SetWxDateTime(dur)
            except ValueError:
                # duration is invalid if there are no photos
                pass

            for audioFile in project.GetAudioFiles():
                idx = self.lvAudio.Append(audioFile)
                self.lvAudio.Select(idx)

        self.__ControlStatusTotalLength()
        self.__ControlStatusAudio()

        self.Fit()
        self.CenterOnParent()
        self.SetFocus()

    def OnCmdBrowseFolderButton(self, event):
        dlg = wx.DirDialog(self,
                           _(u"Browse for folder"),
                           defaultPath=self.tcFolder.GetValue())
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            if self.__ValidateOutDir(path):
                self.tcFolder.SetValue(path)
                Settings().SetProjectPath(path)
        dlg.Destroy()

    def OnControlStatusTotalLength(self, event):
        self.__ControlStatusTotalLength()
        event.Skip()

    def OnControlStatusAudio(self, event):
        self.__ControlStatusAudio()

    def OnCmdBrowseAudioButton(self, event):
        dlg = wx.FileDialog(self, _(u"Select music"),
                            Settings().GetAudioPath(), "",
                            _(u"Audio files") + " (*.*)|*.*",
                            wx.FD_OPEN | wx.FD_MULTIPLE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            Settings().SetAudioPath(os.path.dirname(path))

            for path in dlg.GetPaths():
                self.lvAudio.Append(path)

        dlg.Destroy()

    def OnCmdAudioPreviewButton(self, event):
        selIdx = self.lvAudio.GetSelection()
        if selIdx == wx.NOT_FOUND:
            return

        filename = self.lvAudio.GetString(selIdx)
        if self.mediaCtrl and self.mediaCtrl.GetFilename() == filename:
            if self.mediaCtrl.IsPlaying():
                self.mediaCtrl.Stop()
            else:
                self.mediaCtrl.Play()
        else:
            self.__LoadAudioFile(filename)

    def OnCmdAudioMove(self, event):
        selIdx = self.lvAudio.GetSelection()
        if selIdx == wx.NOT_FOUND:
            return

        selAudio = self.lvAudio.GetString(selIdx)

        evtObj = event.GetEventObject()
        if evtObj is self.cmdAudioMoveUp:
            if selIdx > 0:
                prevAudio = self.lvAudio.GetString(selIdx - 1)

                self.lvAudio.SetString(selIdx, prevAudio)
                self.lvAudio.SetString(selIdx - 1, selAudio)
                self.lvAudio.SetSelection(selIdx - 1)
        elif evtObj is self.cmdAudioMoveDown:
            if selIdx < self.lvAudio.GetCount() - 1:
                nextAudio = self.lvAudio.GetString(selIdx + 1)

                self.lvAudio.SetString(selIdx, nextAudio)
                self.lvAudio.SetString(selIdx + 1, selAudio)
                self.lvAudio.SetSelection(selIdx + 1)

        self.__ControlStatusAudio()

    def OnCmdAudioDel(self, event):
        selIdx = self.lvAudio.GetSelection()
        if selIdx != wx.NOT_FOUND:
            self.lvAudio.Delete(selIdx)
        self.lvAudio.Select(min(selIdx, self.lvAudio.GetCount() - 1))

        self.__ControlStatusAudio()

    def OnDlgProjectPropsClose(self, event):
        self.__CloseMediaCtrl()
        event.Skip()

    def OnCmdCancelButton(self, event):
        self.__CloseMediaCtrl()
        event.Skip()

    def OnCmdOkButton(self, event):
        if self.__ValidateAudioFile() and self.__ValidateOutDir() and self.__ValidateProjName():
            event.Skip()

#    def __GetChoiceDataSelected(self, choice):
#        return choice.GetClientData(choice.GetSelection())
#
#    def __SetChoiceSelectionByData(self, choice, data):
#        for idx in range(choice.GetCount()):
#            if choice.GetClientData(idx) == data:
#                choice.Select(idx)
#                return

    def __ControlStatusTotalLength(self):
        active = self.cbTotalLength.GetValue()
        manual = self.rbManual.GetValue()

        self.rbAudio.Enable(active)
        self.rbManual.Enable(active)
        self.rbTimelapse.Enable(active)
        self.timeCtrlTotalLength.Enable(active and manual)

    def __ControlStatusAudio(self):
        selected = self.lvAudio.GetSelection()

        self.cmdAudioPreview.Enable(selected != wx.NOT_FOUND)
        self.cmdAudioDel.Enable(selected != wx.NOT_FOUND)
        self.cmdAudioMoveUp.Enable(selected > 0)
        self.cmdAudioMoveDown.Enable(selected < (self.lvAudio.GetCount() - 1))

    def __LoadAudioFile(self, path):
        self.__CloseMediaCtrl()

        if not os.path.exists(path):
            dlg = wx.MessageDialog(self,
                                   _(u"Audio file '%s' does not exist!") % path,
                                   _(u"Error"),
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

        mediaCtrl = AudioPlayer(path)
        if mediaCtrl.IsOk():
            self.mediaCtrl = mediaCtrl
            self.mediaCtrl.Play()
        else:
            dlg = wx.MessageDialog(self,
                                   _(u"Audio file not supported!"),
                                   _(u"Error"),
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

    def __ValidateAudioFile(self):
        for path in self.lvAudio.GetItems():
            if not os.path.exists(path):
                dlg = wx.MessageDialog(self,
                                       _(u"Audio file '%s' does not exist!") % path,
                                       _(u"Error"),
                                       wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        return True

    def __CloseMediaCtrl(self):
        if self.mediaCtrl is not None:
            try:
                self.mediaCtrl.Close()
            except:
                pass
        self.mediaCtrl = None

    def __GetTotalLength(self):
        totalLength = None

        if self.cbTotalLength.GetValue():
            if self.rbManual.GetValue():
                totalLength = 0
                dateTime = self.timeCtrlTotalLength.GetValue(as_wxDateTime=True)
                totalLength += dateTime.GetHour() * 3600
                totalLength += dateTime.GetMinute() * 60
                totalLength += dateTime.GetSecond()
            elif self.rbAudio.GetValue():
                totalLength = -1
            elif self.rbTimelapse.GetValue():
                totalLength = None

        return totalLength

    def __ValidateOutDir(self, path=None):
        if path is None:
            path = self.tcFolder.GetValue().strip()

        if not os.path.isdir(path):
            dlg = wx.MessageDialog(self,
                                   _(u"Folder does not exists! Do you want %s to create it?") % Constants.APP_NAME,
                                   _(u"Question"),
                                   wx.YES_NO | wx.ICON_QUESTION)
            resp = dlg.ShowModal()
            dlg.Destroy()
            if resp == wx.ID_YES:
                try:
                    os.makedirs(path)
                except StandardError, err:
                    dlg = wx.MessageDialog(self,
                                           _(u"Cannot create folder: %s") % unicode(err),
                                           _(u"Error"),
                                           wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
            else:
                return False
        else:
            if not IsPathWritable(path):
                dlg = wx.MessageDialog(self,
                                       _(u"Cannot write into folder!"),
                                       _(u"Error"),
                                       wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        return True

    def __ValidateProjName(self):
        projName = self.tcProject.GetValue().strip()
        projName = projName.strip(u".")
        projPath = os.path.join(self.tcFolder.GetValue().strip(), projName)
        if not projName:
            self.pnlHdr.SetErrorMessage(_(u"The project name must be filled."))
            return False
        elif not os.path.exists(projPath):
            try:
                os.makedirs(projPath)
            except StandardError:
                self.pnlHdr.SetErrorMessage(_(u"The project name contains invalid characters."))
                return False
            os.removedirs(projPath)
            return True
        else:
            self.pnlHdr.SetErrorMessage(u"")
            return True

    def __GetProjectPath(self):
        projName = self.tcProject.GetValue().strip()
        projName = projName.strip(u".")
        filepath = os.path.join(self.tcFolder.GetValue().strip(),
                                projName,
                                "%s.pfs" % projName)
        return filepath

    def Destroy(self):
        self.__CloseMediaCtrl()
        wx.Dialog.Destroy(self)

    def GetProject(self):
        if self.__project is None:
            self.__project = Project(self.__GetProjectPath())
        self.__project.SetAudioFiles(self.lvAudio.GetItems())

        if self.cbTotalLength.GetValue() and self.rbTimelapse.GetValue():
            self.__project.SetTimelapse(True)
        else:
            self.__project.SetTimelapse(False)

        self.__project.SetDuration(self.__GetTotalLength())
        self.__project.SetAspect(self.choiceAspect.GetStringSelection())
        return self.__project
