# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2010 Jens Goepfert
#

import wx
import wx.lib.masked.timectrl

from photofilmstrip.gui.ctrls.PnlDlgHeader import PnlDlgHeader


class DlgDuration(wx.Dialog):

    def _InitSizers(self):

        szManual = wx.BoxSizer(wx.HORIZONTAL)
        szManual.Add(self.rbManual, flag=wx.ALIGN_CENTER_VERTICAL)
        szManual.AddSpacer(8)
        szManual.Add(self.timeCtrlTotalLength, 1)

        szCtrls = wx.BoxSizer(orient=wx.VERTICAL)
        szCtrls.AddSpacer(8)
        szCtrls.Add(self.cbTotalLength, border=8, flag=wx.LEFT)
        szCtrls.AddSpacer(8)
        szCtrls.Add(self.rbAudio, border=32, flag=wx.LEFT | wx.EXPAND)
        szCtrls.AddSpacer(8)
        szCtrls.Add(szManual, border=32, flag=wx.LEFT | wx.EXPAND)

        szCmds = wx.BoxSizer(orient=wx.HORIZONTAL)
        szCmds.Add(self.cmdCancel, 0, border=0, flag=0)
        szCmds.AddSpacer(8)
        szCmds.Add(self.cmdOk, 0, border=0, flag=0)

        szMain = wx.BoxSizer(orient=wx.VERTICAL)
        szMain.Add(self.pnlHdr, 0, border=0, flag=wx.EXPAND)
        szMain.Add(szCtrls, 0, border=8, flag=wx.ALL | wx.EXPAND)
        szMain.Add(self.staticLine, 0, border=0, flag=wx.EXPAND)
        szMain.Add(szCmds, 0, border=8, flag=wx.ALL | wx.ALIGN_RIGHT)

        self.SetSizer(szMain)

    def _InitCtrls(self):
        self.pnlHdr = PnlDlgHeader(self)

        self.cbTotalLength = wx.CheckBox(self,
              label=_("Total length:"), name="cbTotalLength")
        self.cbTotalLength.SetValue(False)
        self.cbTotalLength.SetToolTip(_("Overrides the duration of single pictures and gives the project this total length."))
        self.cbTotalLength.Bind(wx.EVT_CHECKBOX, self.OnControlStatusTotalLength)

        self.rbManual = wx.RadioButton(self,
              label=_("User defined:"), name="rbManual")
        self.rbManual.Bind(wx.EVT_RADIOBUTTON, self.OnControlStatusTotalLength)

        self.timeCtrlTotalLength = wx.lib.masked.timectrl.TimeCtrl(self,
              display_seconds=True, fmt24hr=True,
              name="timeCtrlTotalLength", oob_color=wx.YELLOW,
              style=0, useFixedWidthFont=True, value='12:00:00 AM',
              size=wx.Size(300, -1))
        self.timeCtrlTotalLength.Enable(False)

        self.rbAudio = wx.RadioButton(self,
              label=_("Fit to audio files"), name="rbAudio")
        self.rbAudio.Bind(wx.EVT_RADIOBUTTON, self.OnControlStatusTotalLength)

        self.staticLine = wx.StaticLine(self)

        self.cmdCancel = wx.Button(self, id=wx.ID_CANCEL, label=_("&Cancel"),
              name="cmdCancel")
        self.cmdOk = wx.Button(self, id=wx.ID_OK, label=_("&Ok"),
              name="cmdOk")
        self.cmdOk.Bind(wx.EVT_BUTTON, self.OnCmdOkButton, id=wx.ID_OK)
        self.cmdOk.SetDefault()

    def __init__(self, parent, project=None):
        wx.Dialog.__init__(self, parent, name="DlgDuration",
                           style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER,
                           title=_("Slideshow duration"))

        self._InitCtrls()

        self.pnlHdr.SetTitle(_("Configure duration of slideshow"))
        self.pnlHdr.SetBitmap(wx.ArtProvider.GetBitmap('PFS_MUSIC_DURATION', wx.ART_MESSAGE_BOX))

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

        self.__project = project

        pfsDur = project.GetDuration(calc=True)
        duration = project.GetDuration(calc=False)
        if duration is None:
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
        dur.SetHMS(pfsDur // 3600, (pfsDur % 3600) // 60, pfsDur % 60)
        try:
            self.timeCtrlTotalLength.SetWxDateTime(dur)
        except ValueError:
            # duration is invalid if there are no photos
            pass

        self.__ControlStatusTotalLength()

        self._InitSizers()
        self.SetInitialSize(self.GetEffectiveMinSize())
        self.Fit()
        self.CenterOnParent()
        self.SetFocus()

    def OnControlStatusTotalLength(self, event):
        self.__ControlStatusTotalLength()
        event.Skip()

    def OnCmdOkButton(self, event):
        self.__project.SetDuration(self.__GetTotalLength())
        event.Skip()

    def __ControlStatusTotalLength(self):
        active = self.cbTotalLength.GetValue()
        manual = self.rbManual.GetValue()

        self.rbAudio.Enable(active)
        self.rbManual.Enable(active)
        self.timeCtrlTotalLength.Enable(active and manual)

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

        return totalLength
