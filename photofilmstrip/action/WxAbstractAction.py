# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2011 Jens Goepfert
#

import wx

from photofilmstrip.action.IAction import IAction


class WxAbstractAction(IAction):

    def __init__(self):
        pass

    def GetBitmap(self, art=None):
        raise NotImplementedError()

    def ToMenu(self, evtHandler, menu, ident=None):
        if ident is None:
            ident = wx.NewId()
        mitm = wx.MenuItem(menu, ident, self.GetName())

        try:
            bmp = self.GetBitmap(wx.ART_MENU)
        except NotImplementedError:
            bmp = None

        if bmp:
            mitm.SetBitmap(bmp)

        menu.Append(mitm)
        evtHandler.Bind(wx.EVT_MENU, self.__OnExecute, id=ident)
        return mitm

    def Bind(self, evtHandler, evt):
        evtHandler.Bind(evt, self.__OnExecute)

    def __OnExecute(self, event):
        self.Execute()
        event.Skip()
