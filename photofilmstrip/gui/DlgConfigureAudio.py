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
from photofilmstrip.gui.helper import CreateMenuItem
from photofilmstrip.lib.util import FILE_EXTENSIONS_AUDIO, GetDataDir


class DlgConfigureAudio(wx.Dialog):

    def _InitSizers(self):
        szMain = wx.BoxSizer(orient=wx.VERTICAL)

        szCtrls = wx.BoxSizer(orient=wx.HORIZONTAL)

        szAudioCmds = wx.BoxSizer(orient=wx.VERTICAL)

        szCmds = wx.BoxSizer(orient=wx.HORIZONTAL)

        szMain.Add(self.pnlHdr, 0, border=0, flag=wx.EXPAND)
        szMain.Add(self.szMsg, 0, border=8, flag=wx.ALL | wx.EXPAND)
        szMain.Add(szCtrls, 0, border=8, flag=wx.ALL | wx.EXPAND)
        szMain.Add(self.cbAudio, 0, border=8, flag=wx.ALL | wx.EXPAND)
        szMain.Add(szCmds, 0, border=8, flag=wx.ALL | wx.ALIGN_RIGHT)

        szCtrls.Add(self.lvAudio, 1, flag=wx.EXPAND | wx.RIGHT, border=4)
        szCtrls.Add(szAudioCmds)

        szAudioCmds.Add(self.cmdBrowseMusic, border=2, flag=wx.BOTTOM)
        szAudioCmds.Add(self.cmdBrowseAudio, border=2, flag=wx.BOTTOM)
        szAudioCmds.Add(self.cmdAudioPreview, border=2, flag=wx.BOTTOM)
        szAudioCmds.Add(self.cmdAudioMoveUp, border=2, flag=wx.BOTTOM)
        szAudioCmds.Add(self.cmdAudioMoveDown, border=2, flag=wx.BOTTOM)
        szAudioCmds.Add(self.cmdAudioDel, border=2, flag=wx.BOTTOM)

        szCmds.Add(self.cmdCancel, 0, border=0, flag=0)
        szCmds.AddSpacer(8)
        szCmds.Add(self.cmdOk, 0, border=0, flag=0)

        self.SetSizer(szMain)

    def _InitCtrls(self):
        self.pnlHdr = PnlDlgHeader(self)

        self.szMsg = self.CreateTextSizer(
            _("Configure your audio files that are used as a background music."))

        self.lvAudio = wx.ListBox(self, style=wx.LB_SINGLE)
        self.lvAudio.Bind(wx.EVT_LISTBOX, self.OnControlStatusAudio)

        self.cmdBrowseMusic = wx.BitmapButton(self,
              bitmap=wx.ArtProvider.GetBitmap('PFS_MUSIC_16'),
              name=u'cmdBrowseMusic', style=wx.BU_AUTODRAW)
        self.cmdBrowseMusic.Bind(wx.EVT_BUTTON, self.OnCmdBrowseMusicButton)

        self.cmdBrowseAudio = wx.BitmapButton(self,
              bitmap=wx.ArtProvider.GetBitmap('PFS_FOLDER_OPEN_16'),
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

        self.cbAudio = wx.CheckBox(self, wx.ID_ANY,
              label=_(u'Set the duration of your slideshow to fit your audio files'))

        self.cmdCancel = wx.Button(self, id=wx.ID_CANCEL, label=_(u'&Cancel'),
              name=u'cmdCancel')
        self.cmdCancel.Bind(wx.EVT_BUTTON, self.OnCmdCancelButton,
              id=wx.ID_CANCEL)

        self.cmdOk = wx.Button(self, id=wx.ID_OK, label=_(u'&Ok'),
              name=u'cmdOk')
        self.cmdOk.Bind(wx.EVT_BUTTON, self.OnCmdOkButton, id=wx.ID_OK)

    def __init__(self, parent, project):
        wx.Dialog.__init__(self, parent, name=u'DlgConfigureAudio',
                           style=wx.DEFAULT_DIALOG_STYLE,
                           title=_(u'Configure music'))
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self._InitCtrls()

        self.pnlHdr.SetTitle(_(u'Configure music'))
        self.pnlHdr.SetBitmap(wx.ArtProvider.GetBitmap('PFS_MUSIC_32'))

        self.lvAudio.SetMinSize(wx.Size(300, -1))

        self.__project = project
        self.__mediaCtrl = None
        self.__musicMap = {}

        self.cmdBrowseMusic.Show(self.__GetAudioDir() is not None)

        if project.GetTimelapse():
            self.cbAudio.SetValue(False)
            self.cbAudio.Show(False)
        else:
            duration = project.GetDuration(False)
            self.cbAudio.SetValue(duration == -1)

        for audioFile in project.GetAudioFiles():
            idx = self.lvAudio.Append(audioFile)
            self.lvAudio.Select(idx)

        self.__ControlStatusAudio()

        self._InitSizers()
        self.Fit()
        self.CenterOnParent()

    def OnControlStatusAudio(self, event):  # pylint: disable=unused-argument
        self.__ControlStatusAudio()

    def OnCmdBrowseMusicButton(self, event):  # pylint: disable=unused-argument
        menu = wx.Menu()

        audioDir = self.__GetAudioDir()
        for filename in os.listdir(audioDir):
            fname, fext = os.path.splitext(filename)
            if fext in FILE_EXTENSIONS_AUDIO:
                audioFile = os.path.join(audioDir, filename)

                ident = wx.NewId()
                CreateMenuItem(menu, ident, fname)

                self.__musicMap[ident] = audioFile

                self.Bind(wx.EVT_MENU, self.__AddMusic, id=ident)

        self.PopupMenu(menu, pos=self.cmdBrowseMusic.GetPosition(
            ) + (0, self.cmdBrowseMusic.GetSize()[1]))

    def OnCmdBrowseAudioButton(self, event):  # pylint: disable=unused-argument
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

    def OnCmdAudioPreviewButton(self, event):  # pylint: disable=unused-argument
        selIdx = self.lvAudio.GetSelection()
        if selIdx == wx.NOT_FOUND:
            return

        filename = self.lvAudio.GetString(selIdx)
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
            self.__project.SetAudioFiles(self.lvAudio.GetItems())
            if self.cbAudio.GetValue():
                self.__project.SetDuration(-1)
            elif self.__project.GetDuration(False) == -1:
                # was previously set, so reset the duration
                self.__project.SetDuration(None)

            event.Skip()

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
            self.__mediaCtrl = mediaCtrl
            self.__mediaCtrl.Play()
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
        if self.__mediaCtrl is not None:
            try:
                self.__mediaCtrl.Close()
            except:
                pass
        self.__mediaCtrl = None

    def __GetAudioDir(self):
        return GetDataDir("audio")

    def __AddMusic(self, event):
        self.lvAudio.Append(self.__musicMap.get(event.GetId()))
