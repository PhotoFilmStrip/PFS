# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2018 Jens Goepfert
#

import wx

from photofilmstrip.core.GPlayer import GPlayer
from photofilmstrip.gui.ctrls.PnlDlgHeader import PnlDlgHeader


class DlgPicDurationByAudio(wx.Dialog):

    def __init__(self, parent, audioFile, expectedSteps):
        '''
        :type parent: wx.Window
        :type audioFile: str
        :type expectedSteps: int
        '''
        wx.Dialog.__init__(self, parent, style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        self.SetTitle(_(u'Adjust picture durations'))

        self.pnlHdr = PnlDlgHeader(self)
        self.pnlHdr.SetTitle(_(u'Adjust picture durations to audio file'))
        self.pnlHdr.SetBitmap(wx.ArtProvider.GetBitmap('PFS_MUSIC_DURATION_32'))

        szMsg = self.CreateTextSizer(
            _("Find your picture duration by playing the audio file of your project and\n"
              "pressing the hit button to apply the current playing time."))

        self.stAudio = wx.StaticText(self, wx.ID_ANY, style=wx.ST_NO_AUTORESIZE)
        font = self.stAudio.GetFont()
        font.SetPointSize(16)
        self.stAudio.SetFont(font)

        self.listbox = wx.ListBox(self, wx.ID_ANY)
        self.listbox.SetSizeHints(wx.Size(-1, 200))
        self.listbox.Bind(wx.EVT_KEY_DOWN, self.__OnStepListKeyDown)
        self.listbox.Bind(wx.EVT_LISTBOX_DCLICK, self.__OnStepListDClickDown)

        self.btnPlay = wx.Button(self, wx.ID_ANY, _("Play"))
        self.btnPlay.Bind(wx.EVT_BUTTON, self.__OnPlay)

        self.btnHit = wx.Button(self, wx.ID_ANY, _("Hit"))
        self.btnHit.Disable()
        self.btnHit.Bind(wx.EVT_BUTTON, self.__OnHit)

        self.btnCancel = wx.Button(self, wx.ID_CANCEL, _('&Cancel'))
        self.btnOk = wx.Button(self, wx.ID_OK, _('&Ok'))

        szButtons = wx.BoxSizer(wx.HORIZONTAL)
        szButtons.Add(self.btnPlay, flag=wx.RIGHT, border=8)
        szButtons.Add(self.btnHit, flag=wx.RIGHT, border=8)
        szButtons.AddStretchSpacer()
        szButtons.Add(self.btnCancel, flag=wx.RIGHT, border=8)
        szButtons.Add(self.btnOk)

        sz = wx.BoxSizer(wx.VERTICAL)
        sz.Add(self.pnlHdr, flag=wx.EXPAND)
        sz.Add(szMsg, flag=wx.EXPAND | wx.ALL, border=8)
        sz.Add(self.stAudio, flag=wx.EXPAND | wx.ALL, border=8)
        sz.Add(self.listbox, 1, wx.EXPAND | wx.ALL, border=8)
        sz.Add(szButtons, flag=wx.ALL | wx.ALIGN_RIGHT, border=8)

        self.SetSizerAndFit(sz)

        self.__audioFile = audioFile
        self.__player = None

        self.__timer = None
        self.__duration = None
        self.__expectedSteps = expectedSteps
        self.__stepIdx = 0
        self.__lastTime = None

        self.__InitStepList()
        self.stAudio.SetLabel(self.__CreateAudioInfoText(None))

        self.SetEscapeId(wx.ID_CANCEL)

        self.Bind(wx.EVT_TIMER, self.__OnTimer)
        self.Bind(wx.EVT_CLOSE, self.__OnClose)
        self.Bind(wx.EVT_BUTTON, self.__OnClose, id=wx.ID_OK)
        self.Bind(wx.EVT_BUTTON, self.__OnClose, id=wx.ID_CANCEL)

    def __OnTimer(self, event):  # pylint: disable=unused-argument
        if self.__player:
            if self.__player.IsPlaying():
                posMiliSecs = self.__player.GetPosition()
                if posMiliSecs:
                    self.stAudio.SetLabel(
                        self.__CreateAudioInfoText(posMiliSecs))
            else:
                self.__ProcessStop()

    def __OnPlay(self, event):  # pylint: disable=unused-argument
        if self.__player is None or not self.__player.IsPlaying():
            self.btnPlay.SetLabel(_("Stop"))
            self.btnHit.Enable()
            self.__InitStepList()

            self.__timer = wx.Timer(self)
            self.__timer.Start(50)

            self.__player = GPlayer(self.__audioFile)
            self.__lastTime = 0
            self.__duration = self.__player.GetLength()
            self.__player.Play()
#             self.__player.SetPosition(5000)

            self.btnHit.SetFocus()
        else:
            self.__ProcessStop()

    def __OnHit(self, event):  # pylint: disable=unused-argument
        milliSecs = self.__player.GetPosition()
        if self.__stepIdx < self.__expectedSteps - 1:
            milliSecs -= 50  # time to react
            self.__NextStepDuration(milliSecs - self.__lastTime)
            self.__lastTime = milliSecs

        if self.__stepIdx >= self.__expectedSteps - 1:
            self.__NextStepDuration(self.__duration - self.__lastTime)
            self.__ProcessStop()

    def __OnClose(self, event):
        if self.__timer:
            self.__timer.Stop()
        if self.__player and self.__player.IsPlaying():
            self.__player.Stop()
        event.Skip()

    def __OnStepListKeyDown(self, event):
        if event.GetKeyCode() == wx.WXK_DELETE:
            sel = self.listbox.GetSelection()
            if sel != wx.NOT_FOUND:
                self.listbox.SetString(self.__CreateDurationText(sel, None))
                self.listbox.Delete(sel)

    def __OnStepListDClickDown(self, event):
        event.Skip()

    def __InitStepList(self):
        self.__stepIdx = 0
        self.listbox.Clear()
        for ctr in range(self.__expectedSteps):
            self.listbox.Append(self.__CreateDurationText(ctr, None))
        self.listbox.Select(0)

    def __ProcessStop(self):
        self.btnPlay.SetLabel(_("Play"))
        self.btnHit.Disable()
        self.__timer.Stop()
        self.__player.Stop()
        self.__player = None

    def __NextStepDuration(self, duration):
        value = self.__CreateDurationText(self.__stepIdx, duration)
        self.listbox.SetString(self.__stepIdx, value)
        self.listbox.SetClientData(self.__stepIdx, duration)
        self.__stepIdx += 1
        if self.__stepIdx < self.listbox.GetCount():
            self.listbox.Select(self.__stepIdx)

    def __TimeToStr(self, milliSecs):
        if milliSecs is None:
            return "--:--:--,--"
        else:
            secs = milliSecs // 1000.0
            hours = int(secs / 3600.0)
            minutes = int(secs / 60.0) % 60
            seconds = int(secs) % 60
            frac = ((milliSecs / 1000.0) % 1) * 1000
            return "%02d:%02d:%02d,%03d" % (hours, minutes, seconds, frac)

    def __CreateAudioInfoText(self, posMiliSecs):
        return "{}: {}".format(_("Playing time"), self.__TimeToStr(posMiliSecs))

    def __CreateDurationText(self, idx, value):
        return "{}: {}".format(idx + 1, self.__TimeToStr(value))

    def GetDurations(self):
        result = []
        if self.listbox.HasClientData():
            for idx in range(self.__expectedSteps):
                duration = self.listbox.GetClientData(idx)
                if duration is not None:
                    result.append(duration)
                else:
                    break

        return result

    @staticmethod
    def Interact(parent, project):
        '''
        :type parent: wx.Window
        :type project: photofilmstrip.core.Project.Project
        '''
        pics = project.GetPictures()
        if len(pics) == 0:
            return
        if len(project.GetAudioFiles()) == 0:
            dlg = wx.MessageDialog(parent,
                                   _(u"Your project does not have an audio file configured."),
                                   _(u"Error"),
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return
        if len(project.GetAudioFiles()) > 1:
            dlg = wx.MessageDialog(parent,
                                   _(u"Your project uses more than one audio file. Currently the durations can be adjusted only for one audio file."),
                                   _(u"Error"),
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        dlg = DlgPicDurationByAudio(parent, project.GetAudioFile(), len(pics))
        if dlg.ShowModal() == wx.ID_OK:
            for idx, duration in enumerate(dlg.GetDurations()):
                try:
                    pics[idx].SetDuration(duration / 1000.0)
                except IndexError:
                    break
        dlg.Destroy()
