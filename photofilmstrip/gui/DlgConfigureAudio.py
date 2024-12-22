# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2018 Jens Goepfert
#

import os

import wx

from photofilmstrip.lib.Settings import Settings

from photofilmstrip.core.AudioPlayer import AudioPlayer

from photofilmstrip.gui.ctrls.PnlDlgHeader import PnlDlgHeader
from photofilmstrip.lib.util import FILE_EXTENSIONS_AUDIO, GetDataDir


class DlgConfigureAudio(wx.Dialog):

    def _InitSizers(self):
        szMain = wx.BoxSizer(orient=wx.VERTICAL)

        szAudioChoice = wx.BoxSizer(orient=wx.HORIZONTAL)
        szAudioList = wx.BoxSizer(orient=wx.HORIZONTAL)

        szAudioCmds = wx.BoxSizer(orient=wx.VERTICAL)

        szCmds = wx.BoxSizer(orient=wx.HORIZONTAL)

        szMain.Add(self.pnlHdr, 0, border=0, flag=wx.EXPAND)
        szMain.Add(self.szMsg, 0, border=self.FromDIP(8), flag=wx.ALL | wx.EXPAND)
        szMain.Add(szAudioChoice, 0, border=self.FromDIP(8), flag=wx.LEFT | wx.RIGHT | wx.EXPAND)
        szMain.Add(szAudioList, 1, border=self.FromDIP(8), flag=wx.ALL | wx.EXPAND)
        szMain.Add(self.cbAudio, 0, border=self.FromDIP(8), flag=wx.LEFT | wx.RIGHT | wx.EXPAND)
        szMain.Add(szCmds, 0, border=self.FromDIP(8), flag=wx.ALL | wx.ALIGN_RIGHT)

        szAudioChoice.Add(self.choiceAudioFiles, 1, flag=wx.ALIGN_CENTER_VERTICAL | wx.RIGHT, border=self.FromDIP(4))
        szAudioChoice.Add(self.cmdAddMusic)

        szAudioList.Add(self.lvAudio, 1, flag=wx.EXPAND | wx.RIGHT, border=self.FromDIP(4))
        szAudioList.Add(szAudioCmds)

        szAudioCmds.Add(self.cmdAudioPreview, border=self.FromDIP(2), flag=wx.BOTTOM)
        szAudioCmds.Add(self.cmdAudioMoveUp, border=self.FromDIP(2), flag=wx.BOTTOM)
        szAudioCmds.Add(self.cmdAudioMoveDown, border=self.FromDIP(2), flag=wx.BOTTOM)
        szAudioCmds.Add(self.cmdAudioDel, border=self.FromDIP(2), flag=wx.BOTTOM)

        szCmds.Add(self.cmdCancel, 0, border=0, flag=0)
        szCmds.AddSpacer(self.FromDIP(8))
        szCmds.Add(self.cmdOk, 0, border=0, flag=0)

        self.SetSizer(szMain)

    def _InitCtrls(self):
        self.pnlHdr = PnlDlgHeader(self)

        self.szMsg = self.CreateTextSizer(
            _("Configure your audio files that are used as a background music."))

        self.choiceAudioFiles = wx.Choice(self)

        self.lvAudio = wx.ListBox(self, style=wx.LB_SINGLE)
        self.lvAudio.Bind(wx.EVT_LISTBOX, self.OnControlStatusAudio)

        self.cmdAddMusic = wx.BitmapButton(self,
              bitmap=wx.ArtProvider.GetBitmap("PFS_ADD", wx.ART_TOOLBAR),
              name="cmdAddMusic", style=wx.BU_AUTODRAW)
        self.cmdAddMusic.Bind(wx.EVT_BUTTON, self.OnCmdAddMusicButton)

        self.cmdAudioPreview = wx.BitmapButton(self,
              bitmap=wx.ArtProvider.GetBitmap('PFS_PLAY_PAUSE', wx.ART_TOOLBAR),
              name="cmdAudioPreview", style=wx.BU_AUTODRAW)
        self.cmdAudioPreview.SetBitmapDisabled(wx.ArtProvider.GetBitmap('PFS_PLAY_PAUSE_D', wx.ART_TOOLBAR))
        self.cmdAudioPreview.Bind(wx.EVT_BUTTON, self.OnCmdAudioPreviewButton)

        self.cmdAudioMoveUp = wx.BitmapButton(self,
              bitmap=wx.ArtProvider.GetBitmap('PFS_ARROW_UP', wx.ART_TOOLBAR),
              name="cmdAudioMoveUp", style=wx.BU_AUTODRAW)
        self.cmdAudioMoveUp.SetBitmapDisabled(wx.ArtProvider.GetBitmap('PFS_ARROW_UP_D', wx.ART_TOOLBAR))
        self.cmdAudioMoveUp.Bind(wx.EVT_BUTTON, self.OnCmdAudioMove)

        self.cmdAudioMoveDown = wx.BitmapButton(self,
              bitmap=wx.ArtProvider.GetBitmap('PFS_ARROW_DOWN', wx.ART_TOOLBAR),
              name="cmdAudioMoveDown", style=wx.BU_AUTODRAW)
        self.cmdAudioMoveDown.SetBitmapDisabled(wx.ArtProvider.GetBitmap('PFS_ARROW_DOWN_D', wx.ART_TOOLBAR))
        self.cmdAudioMoveDown.Bind(wx.EVT_BUTTON, self.OnCmdAudioMove)

        self.cmdAudioDel = wx.BitmapButton(self,
              bitmap=wx.ArtProvider.GetBitmap('PFS_REMOVE', wx.ART_TOOLBAR),
              name="cmdAudioDel", style=wx.BU_AUTODRAW)
        self.cmdAudioDel.SetBitmapDisabled(wx.ArtProvider.GetBitmap('PFS_REMOVE_D', wx.ART_TOOLBAR))
        self.cmdAudioDel.Bind(wx.EVT_BUTTON, self.OnCmdAudioDel)

        self.cbAudio = wx.CheckBox(self, wx.ID_ANY,
              label=_("Set the duration of your slideshow to fit your audio files"))

        self.cmdCancel = wx.Button(self, id=wx.ID_CANCEL, label=_("&Cancel"),
              name="cmdCancel")
        self.cmdCancel.Bind(wx.EVT_BUTTON, self.OnCmdCancelButton,
              id=wx.ID_CANCEL)

        self.cmdOk = wx.Button(self, id=wx.ID_OK, label=_("&Ok"),
              name="cmdOk")
        self.cmdOk.Bind(wx.EVT_BUTTON, self.OnCmdOkButton, id=wx.ID_OK)

    def __init__(self, parent, project):
        wx.Dialog.__init__(self, parent, name="DlgConfigureAudio",
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
                           title=_("Configure music"))
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self._InitCtrls()

        self.pnlHdr.SetTitle(_("Configure music"))
        self.pnlHdr.SetBitmap(wx.ArtProvider.GetBitmap('PFS_MUSIC', wx.ART_MESSAGE_BOX))

        self.lvAudio.SetMinSize(wx.Size(300, -1))

        self.__project = project
        self.__mediaCtrl = None
        self.__musicMap = {}

        self.__idxSelectOption = self.choiceAudioFiles.Append("~ {} ~".format(_("Select an entry")))
        self.__idxBrowseAudio = self.choiceAudioFiles.Append("~ {} ~".format(_("Browse for audio files")))

        self.__CreateProvidedMusicEntries()

        self.cmdAddMusic.Enable(False)
        self.choiceAudioFiles.Select(self.__idxSelectOption)
        self.choiceAudioFiles.Bind(wx.EVT_CHOICE, self.OnChoiceAudio)

        if project.GetTimelapse():
            self.cbAudio.SetValue(False)
            self.cbAudio.Show(False)
        else:
            duration = project.GetDuration(False)
            self.cbAudio.SetValue(duration == -1)

        for audioFile in project.GetAudioFiles():
            self.__AddAudioItem(audioFile, select=True)

        self.__ControlStatusAudio()

        self._InitSizers()
        self.SetInitialSize(self.GetEffectiveMinSize())
        self.Fit()
        self.CenterOnParent()

    def OnControlStatusAudio(self, event):  # pylint: disable=unused-argument
        self.__ControlStatusAudio()

    def OnChoiceAudio(self, event):
        selIdx = event.GetInt()
        self.cmdAddMusic.Enable(selIdx not in (self.__idxBrowseAudio, self.__idxSelectOption))
        if selIdx == self.__idxBrowseAudio:
            self.OnCmdBrowseAudioButton(event)
            self.choiceAudioFiles.Select(self.__idxSelectOption)
        elif selIdx != self.__idxSelectOption:
            self.OnCmdAddMusicButton(event)
        else:
            pass

    def OnCmdAddMusicButton(self, event):  # pylint: disable=unused-argument
        selIdx = self.choiceAudioFiles.GetSelection()
        if selIdx == wx.NOT_FOUND:
            return

        audioFile = self.choiceAudioFiles.GetClientData(selIdx)
        if audioFile:
            self.__AddAudioItem(audioFile, select=True)

    def __CreateProvidedMusicEntries(self):
        audioDir = self.__GetAudioDir()
        for filename in os.listdir(audioDir):
            fname, fext = os.path.splitext(filename)
            if fext in FILE_EXTENSIONS_AUDIO:
                audioFile = os.path.join(audioDir, filename)

                self.choiceAudioFiles.Append(fname, audioFile)

    def OnCmdBrowseAudioButton(self, event):  # pylint: disable=unused-argument
        dlg = wx.FileDialog(self, _("Select music"),
                            Settings().GetAudioPath(), "",
                            _("Audio files") + " (*.*)|*.*",
                            wx.FD_OPEN | wx.FD_MULTIPLE)
        if dlg.ShowModal() == wx.ID_OK:
            for path in dlg.GetPaths():
                Settings().SetAudioPath(os.path.dirname(path))
                self.__AddAudioItem(path, select=True)

        dlg.Destroy()

    def OnCmdAudioPreviewButton(self, event):  # pylint: disable=unused-argument
        selIdx = self.lvAudio.GetSelection()
        if selIdx == wx.NOT_FOUND:
            return

        filename = self.lvAudio.GetClientData(selIdx)
        if self.__mediaCtrl and self.__mediaCtrl.GetFilename() == filename:
            if self.__mediaCtrl.IsPlaying():
                self.__mediaCtrl.Stop()
            else:
                self.__mediaCtrl.Play()
        else:
            self.__LoadAudioFile(filename)

    def OnCmdAudioMove(self, event):
        selIdx = self.lvAudio.GetSelection()
        if selIdx == wx.NOT_FOUND:
            return

        selAudio = self.lvAudio.GetClientData(selIdx)

        evtObj = event.GetEventObject()
        if evtObj is self.cmdAudioMoveUp:
            if selIdx > 0:
                prevAudio = self.lvAudio.GetClientData(selIdx - 1)
                self.__UpdateAudioItem(selIdx, prevAudio)
                self.__UpdateAudioItem(selIdx - 1, selAudio)
                self.lvAudio.SetSelection(selIdx - 1)
        elif evtObj is self.cmdAudioMoveDown:
            if selIdx < self.lvAudio.GetCount() - 1:
                nextAudio = self.lvAudio.GetClientData(selIdx + 1)
                self.__UpdateAudioItem(selIdx, nextAudio)
                self.__UpdateAudioItem(selIdx + 1, selAudio)
                self.lvAudio.SetSelection(selIdx + 1)

        self.__ControlStatusAudio()

    def OnCmdAudioDel(self, event):  # pylint: disable=unused-argument
        selIdx = self.lvAudio.GetSelection()
        if selIdx != wx.NOT_FOUND:
            self.lvAudio.Delete(selIdx)
        self.lvAudio.Select(min(selIdx, self.lvAudio.GetCount() - 1))

        self.__ControlStatusAudio()

    def OnClose(self, event):
        self.__CloseMediaCtrl()
        event.Skip()

    def OnCmdCancelButton(self, event):
        self.__CloseMediaCtrl()
        event.Skip()

    def OnCmdOkButton(self, event):
        self.__CloseMediaCtrl()
        if self.__ValidateAudioFile():
            self.__project.SetAudioFiles([ai[2] for ai in self.__IterAudioItems()])
            if self.cbAudio.GetValue():
                self.__project.SetDuration(-1)
            elif self.__project.GetDuration(False) == -1:
                # was previously set, so reset the duration
                self.__project.SetDuration(None)

            event.Skip()

    def __AddAudioItem(self, audioFile, select=False):
        idx = self.lvAudio.Append("")
        self.__UpdateAudioItem(idx, audioFile)
        if select:
            self.lvAudio.Select(idx)

            self.__ControlStatusAudio()
        return idx

    def __UpdateAudioItem(self, idx, audioFile):
        self.lvAudio.SetString(idx, os.path.basename(audioFile))
        self.lvAudio.SetClientData(idx, audioFile)

    def __IterAudioItems(self):
        for idx in range(self.lvAudio.GetCount()):
            yield idx, self.lvAudio.GetString(idx), self.lvAudio.GetClientData(idx)

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
                                   _("Audio file '%s' does not exist!") % path,
                                   _("Error"),
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

        mediaCtrl = AudioPlayer(path)
        if mediaCtrl.IsOk():
            self.__mediaCtrl = mediaCtrl
            self.__mediaCtrl.Play()
        else:
            dlg = wx.MessageDialog(self,
                                   _("Audio file not supported!"),
                                   _("Error"),
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

    def __ValidateAudioFile(self):
        for idx, basename, path in self.__IterAudioItems():
            if not os.path.exists(path):
                dlg = wx.MessageDialog(self,
                                       _("Audio file '%s' does not exist!") % path,
                                       _("Error"),
                                       wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        return True

    def __CloseMediaCtrl(self):
        if self.__mediaCtrl is not None:
            try:
                self.__mediaCtrl.Close()
            except:
                pass
        self.__mediaCtrl = None

    def __GetAudioDir(self):
        return GetDataDir("audio")
