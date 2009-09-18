
import cStringIO
import sys
import traceback
import urllib

import wx
from wx.lib.wordwrap import wordwrap

from lib.Settings import Settings
from lib.util import Encode


class DlgBugReport(wx.Dialog):
    
    PARENT = None
    
    @classmethod
    def Initialize(cls, parent):
        cls.PARENT = parent
        def excepthook(etype, value, tb):
            traceback.print_exception(etype, value, tb)
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
        
        self.tcMsg = wx.TextCtrl(self, -1, msg, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP)
        
        szCmd = self.CreateSeparatedButtonSizer(wx.YES | wx.NO)

        szMain = wx.BoxSizer(wx.VERTICAL)
        szMain.Add(szTop, 0, wx.ALL, 8)
        szMain.Add(self.tcMsg, 1, wx.EXPAND | wx.ALL, 8)
        szMain.Add(szCmd, 0, wx.EXPAND)
        
        self.SetSizer(szMain)
        
        self.Bind(wx.EVT_BUTTON, self.OnNo, id=wx.ID_NO)
        self.Bind(wx.EVT_BUTTON, self.OnYes, id=wx.ID_YES)
        
        self.SetAffirmativeId(wx.ID_YES)
        self.SetEscapeId(wx.ID_NO)

    def OnYes(self, event):
        info = "\n".join([sys.platform, 
                          sys.getdefaultencoding(), 
                          sys.getfilesystemencoding()])
        params = urllib.urlencode({'bugreport': "%s-%s\n\n%s\n%s\n" % (Settings.APP_NAME, 
                                                                       Settings.APP_VERSION,
                                                                       Encode(self.tcMsg.GetValue()),
                                                                       info)})
        try:
            fd = urllib.urlopen("http://www.sg-dev.de/bugreport.php", params)
            result = fd.read()
        except IOError:
            result = None
        
        if result and result.find("Result 1") != -1:
            dlg = wx.MessageDialog(self,
                                   _(u"Bug-Report send. Thank you for your support."), 
                                   _(u"Information"),
                                   wx.OK | wx.ICON_INFORMATION)
            dlg.ShowModal()
            dlg.Destroy()
        else:
            dlg = wx.MessageDialog(self,
                                   _(u"Sorry, this function is temporary not available.."), 
                                   _(u"Error"),
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
        
        self.EndModal(wx.ID_YES)

    def OnNo(self, event):
        self.EndModal(wx.ID_NO)
        event.Skip()
