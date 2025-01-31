# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#

import wx
import string


class FloatValidator(wx.Validator):

    def __init__(self):
        wx.Validator.__init__(self)
        self.Bind(wx.EVT_CHAR, self.OnChar)

    def Clone(self):
        return self

    def Validate(self, win):
        tc = self.GetWindow()
        val = tc.GetValue()
        for x in val:
            if x not in (string.digits + ".-"):
                return False
        return True

    def OnChar(self, event):
        key = event.GetKeyCode()

        if key < wx.WXK_SPACE or key == wx.WXK_DELETE or key > 255:
            event.Skip()
            return

        if chr(key) in string.digits:
            event.Skip()
            return

        if chr(key) == '-' and '-' not in self.GetWindow().GetValue():
            self.GetWindow().SetInsertionPoint(0)
            self.GetWindow().WriteText("-")
            self.GetWindow().SetInsertionPointEnd()
            return

        if chr(key) in [',', '.'] and "." not in self.GetWindow().GetValue():
            self.GetWindow().WriteText(".")
            return

        if not wx.Validator.IsSilent():
            wx.Bell()

        # Returning without calling even.Skip eats the event before it
        # gets to the text control
        return

