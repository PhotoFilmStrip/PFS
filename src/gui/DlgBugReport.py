
import cStringIO
import sys
import traceback

import wx
from wx.lib.wordwrap import wordwrap

from lib.Settings import Settings


class DlgBugReport(wx.Dialog):
    
    PARENT = None
    
    @classmethod
    def Initialize(cls, parent):
        cls.PARENT = parent
        def excepthook(etype, value, tb):
            output = cStringIO.StringIO()
            traceback.print_exception(etype, value, tb, file=output)
            dlg = DlgBugReport(cls.PARENT, output.getvalue()) 
            dlg.ShowModal()
            dlg.Destroy()
        sys.excepthook = excepthook

    def __init__(self, parent, msg):
        wx.Dialog.__init__(self, parent, -1, 
                           _(u"An unexpected error occured"),
                           name=u'DlgBugReport')
        
        text = _(u"An unexpected error occured. Do you want to send this bug report to the developers of %s?") % Settings.APP_NAME
        
        stBmp = wx.StaticBitmap(self, -1, wx.ArtProvider_GetBitmap(wx.ART_ERROR, wx.ART_OTHER, (32, 32)))
        stMsg = wx.StaticText(self, -1, wordwrap(text, 300, wx.ClientDC(self)))
        
        szTop = wx.BoxSizer(wx.HORIZONTAL)
        szTop.Add(stBmp, 0, wx.ALIGN_CENTER_VERTICAL)
        szTop.AddSpacer(16)
        szTop.Add(stMsg, 0)
        
        tcMsg = wx.TextCtrl(self, -1, msg, style=wx.TE_MULTILINE | wx.TE_READONLY)
        
        szCmd = self.CreateSeparatedButtonSizer(wx.YES | wx.NO)

        szMain = wx.BoxSizer(wx.VERTICAL)
        szMain.Add(szTop, 0, wx.ALL, 8)
        szMain.Add(tcMsg, 1, wx.EXPAND | wx.ALL, 8)
        szMain.Add(szCmd, 0, wx.EXPAND)
        
        self.SetSizer(szMain)
        
        self.Bind(wx.EVT_BUTTON, self.OnYes, id=wx.ID_YES)

    def OnYes(self, event):
        event.Skip()
