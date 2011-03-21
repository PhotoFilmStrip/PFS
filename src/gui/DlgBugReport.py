# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

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
            if getattr(sys, 'frozen', False):
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
        szTop.Add(stBmp, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 8)
        szTop.Add(stMsg, 0, wx.ALL, 8)
        
        self.tcMsg = wx.TextCtrl(self, -1, msg, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_DONTWRAP)
        
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

    def OnYes(self, event):
        info = "\n".join([sys.platform, 
                          sys.getdefaultencoding(), 
                          sys.getfilesystemencoding(),
                          str(getattr(sys, 'frozen', False))])
        params = urllib.urlencode({'bugreport': "%s-%s\n\n%s\n%s\n" % (Settings.APP_NAME, 
                                                                       Settings.APP_VERSION_EX,
                                                                       Encode(self.tcMsg.GetValue()),
                                                                       info)})
        try:
            fd = urllib.urlopen("http://www.photofilmstrip.org/bugreport.php", params)
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
