# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#

import io
import sys
import traceback
import urllib.parse
import urllib.request

import wx
from wx.lib.wordwrap import wordwrap

from photofilmstrip import Constants


class DlgBugReport(wx.Dialog):

    PARENT = None

    @classmethod
    def Initialize(cls, parent):
        cls.PARENT = parent

        def excepthook(etype, value, tb):
            if not getattr(sys, 'frozen', False):
                traceback.print_exception(etype, value, tb)
            output = io.StringIO()
            traceback.print_exception(etype, value, tb, file=output)
            dlg = DlgBugReport(cls.PARENT, output.getvalue())
            dlg.ShowModal()
            dlg.Destroy()

        sys.excepthook = excepthook

    def __init__(self, parent, msg):
        wx.Dialog.__init__(self, parent, -1,
                           _("An unexpected error occured"),
                           name="DlgBugReport")

        text = _("An unexpected error occured. Do you want to send this bug report to the developers of %s?") % Constants.APP_NAME

        stBmp = wx.StaticBitmap(
            self, -1,
            wx.ArtProvider.GetBitmap(wx.ART_ERROR, size=wx.Size(32, 32)))
        stMsg = wx.StaticText(self, -1, wordwrap(text, 300, wx.ClientDC(self)))

        szTop = wx.BoxSizer(wx.HORIZONTAL)
        szTop.Add(stBmp, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 8)
        szTop.Add(stMsg, 0, wx.ALL, 8)

        self.tcMsg = wx.TextCtrl(
            self, -1, msg,
            style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP)

        szCmd = self.CreateSeparatedButtonSizer(wx.YES | wx.NO)

        szMain = wx.BoxSizer(wx.VERTICAL)
        szMain.Add(szTop, 0)
        szMain.Add(self.tcMsg, 1, wx.EXPAND | wx.ALL, 4)
        szMain.Add(szCmd, 0, wx.EXPAND | wx.ALL, 4)

        self.SetSizer(szMain)

        self.Bind(wx.EVT_BUTTON, self.OnNo, id=wx.ID_NO)
        self.Bind(wx.EVT_BUTTON, self.OnYes, id=wx.ID_YES)

        self.SetAffirmativeId(wx.ID_YES)
        self.SetEscapeId(wx.ID_NO)
        self.SetInitialSize(self.GetEffectiveMinSize())
        self.CenterOnParent()
        self.SetFocus()

    def OnYes(self, event):  # pylint: disable=unused-argument
        info = "\n".join([sys.platform,
                          sys.getdefaultencoding(),
                          sys.getfilesystemencoding(),
                          str(getattr(sys, 'frozen', False))])
        params = urllib.parse.urlencode(
            {'bugreport': "%s-%s\n\n%s\n%s\n" % (Constants.APP_NAME,
                                                 Constants.APP_VERSION_FULL,
                                                 self.tcMsg.GetValue(),
                                                 info)})
        params = params.encode('utf_8')
        try:
            fd = urllib.request.urlopen(
                "http://www.photofilmstrip.org/bugreport.php", params)
            result = fd.read()
            result = result.decode("utf-8")
        except IOError:
            result = None

        if result and result.find("Result 1") != -1:
            dlg = wx.MessageDialog(
                self,
                _("Bug-Report send. Thank you for your support."),
                _("Information"),
                wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            dlg = wx.MessageDialog(self,
                                   _("Sorry, this function is temporary not available.."),
                                   _("Error"),
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

        self.EndModal(wx.ID_YES)

    def OnNo(self, event):
        self.EndModal(wx.ID_NO)
        event.Skip()
