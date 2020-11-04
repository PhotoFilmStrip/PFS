# Boa:FramePanel:PnlFloatSpinCtrl
# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2010 Jens Goepfert
#

import wx

from photofilmstrip.gui.util.FloatValidator import FloatValidator

[wxID_PNLFLOATSPINCTRL, wxID_PNLFLOATSPINCTRLSPINBUTTONVALUE,
 wxID_PNLFLOATSPINCTRLTCVALUE,
] = [wx.NewId() for _init_ctrls in range(3)]


class PnlFloatSpinCtrl(wx.Panel):

    def _init_coll_szMain_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.tcValue, 1, border=0, flag=0)
        parent.Add(self.spinButtonValue, 0, border=0, flag=0)

    def _init_sizers(self):
        # generated method, don't edit
        self.szMain = wx.BoxSizer(orient=wx.HORIZONTAL)

        self._init_coll_szMain_Items(self.szMain)

        self.SetSizer(self.szMain)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Panel.__init__(self, id=wxID_PNLFLOATSPINCTRL,
              name="PnlFloatSpinCtrl", parent=prnt, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.TAB_TRAVERSAL)
        self.SetClientSize(wx.Size(169, 31))

        self.tcValue = wx.TextCtrl(id=wxID_PNLFLOATSPINCTRLTCVALUE,
              name="tcValue", parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0, value="5.0")
        self.tcValue.Bind(wx.EVT_KILL_FOCUS, self.OnTextCtrlValueKillFocus,
              id=wxID_PNLFLOATSPINCTRLTCVALUE)
        self.tcValue.Bind(wx.EVT_TEXT, self.OnTextCtrlValueText,
              id=wxID_PNLFLOATSPINCTRLTCVALUE)

        self.spinButtonValue = wx.SpinButton(id=wxID_PNLFLOATSPINCTRLSPINBUTTONVALUE,
              name="spinButtonValue", parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.SP_VERTICAL)
        self.spinButtonValue.Bind(wx.EVT_SPIN, self.OnSpinButtonValueSpin,
              id=wxID_PNLFLOATSPINCTRLSPINBUTTONVALUE)

        self._init_sizers()

    def __init__(self, parent, id, pos, size, style, name):
        self._init_ctrls(parent)
        self.tcValue.SetValidator(FloatValidator())
        self.spinButtonValue.SetMinSize(wx.Size(-1, self.tcValue.GetSize()[1]))

    def __SendValueChangedEvent(self, value):
        evt = ValueChangedEvent(self.GetId(), value)
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)

    def SetRange(self, minVal, maxVal):
        self.spinButtonValue.SetRange(minVal, maxVal)

    def OnSpinButtonValueSpin(self, event):
        value = event.GetPosition() / 10.0
        self.tcValue.ChangeValue("%.1f" % value)
        self.__SendValueChangedEvent(value)
        event.Skip()

    def __GetValue(self):
        val = self.tcValue.GetValue()
        try:
            floatVal = max(float(val), 1.0)
        except ValueError:
            floatVal = 1.0
        return min(floatVal, 600.0)

    def SetValue(self, value):
        self.tcValue.ChangeValue("%.1f" % value)
        self.spinButtonValue.SetValue(int(value * 10))

    def OnTextCtrlValueKillFocus(self, event):
        value = self.__GetValue()
        self.spinButtonValue.SetValue(int(value * 10))
        self.tcValue.ChangeValue("%.1f" % value)
        self.__SendValueChangedEvent(value)
        event.Skip()

    def OnTextCtrlValueText(self, event):
        value = self.__GetValue()
        self.__SendValueChangedEvent(value)
        event.Skip()


_EVT_VALUE_CHANGED_TYPE = wx.NewEventType()
EVT_VALUE_CHANGED = wx.PyEventBinder(_EVT_VALUE_CHANGED_TYPE, 1)


class ValueChangedEvent(wx.PyCommandEvent):

    def __init__(self, wxId, value):
        wx.PyCommandEvent.__init__(self, _EVT_VALUE_CHANGED_TYPE, wxId)
        self.__value = value

    def GetValue(self):
        return self.__value

