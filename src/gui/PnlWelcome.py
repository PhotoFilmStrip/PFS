#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2010 Jens Goepfert
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

import os
import wx
import wx.html
import wx.lib.wxpTag
import wx.lib.hyperlink

from lib.Settings import Settings
from lib.UpdateChecker import UpdateChecker

from core.PhotoFilmStrip import PhotoFilmStrip
from core.util import ImageToStream

from gui.ctrls.BitmapButton import BitmapButton
from gui.ctrls.IconLabelLink import IconLabelLink


class PnlWelcome(wx.Panel):

    def __init__(self, parent, frmMain):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        
        self.title = _(u"Welcome to PhotoFilmStrip")
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        
        self.__frmMain = frmMain

        htmlParts = []
        fileHistory = Settings().GetFileHistory()
        for recentFile in fileHistory:
            if PhotoFilmStrip.IsOk(recentFile):
                htmlPart = """<td align="center" valign="bottom">
                    <wxp module="gui.PnlWelcome" class="LinkOpenPfs">
                        <param name="filename" value="%s">
                    </wxp>
                </td>""" % recentFile
                htmlParts.append(htmlPart)
        
        if htmlParts:
            self.htmlTitle = _(u"Recent projects")
            self.htmlText  = ""
        else:
            self.htmlTitle = _(u"How to start...")
            self.htmlText  = _(u"Create a new project or load an existing one.")
            
        self.htmlRecentProjects = "".join(htmlParts)

        self.htmlWin = wx.html.HtmlWindow(self, -1, style=wx.SIMPLE_BORDER)
        self.htmlWin.Bind(EVT_LINK, self.OnLinkClicked)
        self.htmlWin.SetPage(self.__GenerateHtml())
        self.htmlWin.SetSizeHints(650, -1, 650, -1)

        self.cmdNew = BitmapButton(self, wx.NewId(),
                                   wx.ArtProvider_GetBitmap(wx.ART_NEW, wx.ART_OTHER, (64, 64)))
        self.cmdNew.SetBitmapHover(wx.ArtProvider_GetBitmap(wx.ART_NEW, wx.ART_OTHER, (64, 64)))
        self.cmdNew.SetToolTipString(_(u"Create new project"))
        self.cmdNew.Bind(wx.EVT_BUTTON, self.__frmMain.OnProjectNew)
        
        self.cmdOpen = BitmapButton(self, wx.NewId(),
                                   wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, (64, 64)))
        self.cmdOpen.SetBitmapHover(wx.ArtProvider_GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, (64, 64)))
        self.cmdOpen.SetToolTipString(_(u"Open existing project"))
        self.cmdOpen.Bind(wx.EVT_BUTTON, self.__frmMain.OnProjectLoad)
        
        sizerCmd = wx.BoxSizer(wx.HORIZONTAL)
        sizerCmd.Add(self.cmdNew, 0, wx.ALL, 30)
        sizerCmd.AddStretchSpacer(1)
        sizerCmd.Add(self.cmdOpen, 0, wx.ALL, 30)

        sizerMain = wx.BoxSizer(wx.VERTICAL)
        sizerMain.AddStretchSpacer(1)
        sizerMain.Add(sizerCmd, 0, wx.ALIGN_CENTER_HORIZONTAL, 8)
        sizerMain.Add(self.htmlWin, 3, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 8) 
        sizerMain.AddStretchSpacer(2)
        
        self.SetSizer(sizerMain)
        self.Layout()
        
        self.__updateChecker = UpdateChecker()
        wx.CallLater(500, self.__NotifyUpdate)
        
    def __GenerateHtml(self, htmlUpdate=""):
        return HTML_TEMPLATE  % {'title': self.htmlTitle,
                                 'text': self.htmlText,
                                 'htmlRecentProjects': self.htmlRecentProjects,
                                 'htmlUpdate': htmlUpdate}

        
    def __NotifyUpdate(self):
        if not self.__updateChecker.IsDone():
            wx.CallLater(100, self.__NotifyUpdate)
            return
        if not self.__updateChecker.IsOk():
            return
        if not self.__updateChecker.IsNewer(Settings.APP_VERSION):
            return

        html = """<h3 align="center">%(title)s</h3>
  <center>
    <wxp module="gui.PnlWelcome" class="PfsHyperlink">
        <param name="label" value="Download %(appname)s %(version)s">
    </wxp>
  </center>
  <p>%(msg)s</p>
  <pre>%(changes)s</pre>""" % {"title": _("Update available"),
                               "appname": Settings.APP_NAME,
                               "version": self.__updateChecker.GetVersion(),
                               "msg": _(u'The following changes has been made:'),
                               "changes": self.__updateChecker.GetChanges(),
                               "url": Settings.APP_URL}
        
        self.htmlWin.SetPage(self.__GenerateHtml(html))

    def OnSize(self, event):
        self.Refresh()
        event.Skip()

    def OnPaint(self, event):
        dc = wx.AutoBufferedPaintDC(self)
        sz = self.GetSize()
        dc.SetBackground(wx.Brush(wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNFACE)))
        dc.Clear()
        
        rect = wx.RectPS(wx.Point(0, 180), sz) 
        dc.GradientFillLinear(rect, 
                              wx.SystemSettings_GetColour(wx.SYS_COLOUR_BTNFACE), 
                              wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT), 
                              wx.SOUTH)
        
        font = wx.Font(14, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        dc.SetFont(font)
        dc.SetTextForeground(wx.Color(127, 127, 127))
        dc.DrawLabel(self.title, wx.Rect(0, 10, sz[0], 50), wx.ALIGN_CENTER_HORIZONTAL)
        
    def OnLinkClicked(self, event):
        filename = event.GetFilename()
        self.__frmMain.LoadProject(filename, True)


class LinkOpenPfs(IconLabelLink):
    
    BMP_MAP = {}
    
    def __init__(self, parent, size=wx.DefaultSize, filename=None):
        self.filename = filename
        
        if not LinkOpenPfs.BMP_MAP.has_key(filename):
            imgCount, img = PhotoFilmStrip.QuickInfo(filename)
            if img is not None:
                wxImg = wx.ImageFromStream(ImageToStream(img), wx.BITMAP_TYPE_JPEG)
                bmp = wxImg.ConvertToBitmap()
            else:
                bmp = wx.ArtProvider_GetBitmap("PFS_ICON_48", wx.ART_OTHER)
            descr = "%d images" % imgCount
            LinkOpenPfs.BMP_MAP[filename] = (bmp, descr)
        
        bmp, descr = LinkOpenPfs.BMP_MAP[filename]
        
        IconLabelLink.__init__(self, parent, size,
                               os.path.basename(filename),
                               bmp,
                               descr)
        
    def OnClick(self):
        evt = LinkClickedEvent(self.GetParent().GetId(), self.filename)
        self.GetEventHandler().ProcessEvent(evt)
        

EVT_LINK_TYPE  = wx.NewEventType()
EVT_LINK       = wx.PyEventBinder(EVT_LINK_TYPE, 1)


class LinkClickedEvent(wx.PyCommandEvent):
    def __init__(self, wxId, filename):
        wx.PyCommandEvent.__init__(self, EVT_LINK_TYPE, wxId)
        self._filename = filename

    def GetFilename(self):
        return self._filename


class PfsHyperlink(wx.lib.hyperlink.HyperLinkCtrl):
    
    def __init__(self, parent, size=wx.DefaultSize, label=""):
        wx.lib.hyperlink.HyperLinkCtrl.__init__(self, parent, -1, 
                                                label, 
                                                wx.DefaultPosition, size)
        self.SetBackgroundColour(parent.GetBackgroundColour())
        self.SetURL(Settings.APP_URL)


HTML_TEMPLATE = """<html>
  <body bgcolor="#FFFFFF" witdth="650px">
  <font color="#0000" face="Verdana">
    <h3 align="center">%(title)s</h3>

    <center>
        <table border="0" cellspacing="0" cellpadding="0">
            <tr>%(htmlRecentProjects)s</tr>
        </table>
    </center>

    <p>%(text)s</p>
    %(htmlUpdate)s
  </font>
  </body>
</html>"""
