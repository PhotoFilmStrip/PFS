# encoding: UTF-8
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
import wx.lib.wxpTag  # import needed to initialize html tag 'wxp'; pylint: disable=unused-import
import wx.adv

from photofilmstrip import Constants
from photofilmstrip.lib.Settings import Settings
from photofilmstrip.lib.UpdateChecker import UpdateChecker

from photofilmstrip.core.ProjectFile import ProjectFile
from photofilmstrip.core import PILBackend

from photofilmstrip.gui.ctrls.IconLabelLink import IconLabelLink


class PnlWelcome(wx.Panel):

    def __init__(self, parent, frmMain):
        wx.Panel.__init__(self, parent)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        self.title = _(u"Welcome to PhotoFilmStrip")

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.__frmMain = frmMain

        self.htmlTitle = _(u"Recent projects")
        self.htmlText = u""
        self.htmlRecentProjects = u""
        self.htmlUpdate = u""

        self.pnlHtmlBackground = wx.Panel(self)
        self.pnlHtmlBackground.SetBackgroundColour(wx.Colour(52, 73, 94))

        self.htmlWin = wx.html.HtmlWindow(self.pnlHtmlBackground, -1, style=wx.NO_BORDER)
        self.htmlWin.SetBackgroundStyle(wx.BG_STYLE_SYSTEM)
        self.htmlWin.Bind(EVT_LINK, self.OnLinkClicked)
        self.htmlWin.SetSizeHints(650, -1, 650, -1)

        sizerHtmlBackground = wx.BoxSizer(wx.HORIZONTAL)
        sizerHtmlBackground.Add(self.htmlWin, 1, wx.EXPAND | wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 8)

        self.bmpFilmstrip = wx.ArtProvider.GetBitmap('PFS_FILMSTRIP')

        self.cmdNew = wx.BitmapButton(self, -1,
                                      wx.ArtProvider.GetBitmap('PFS_PROJECT_NEW_64'))
        self.cmdNew.SetToolTip(_(u"Create new slideshow"))
        self.cmdNew.Bind(wx.EVT_BUTTON, self.__frmMain.OnSlideshow)

        self.cmdOpen = wx.BitmapButton(self, -1,
                                       wx.ArtProvider.GetBitmap('PFS_PROJECT_OPEN_64'))
        self.cmdOpen.SetToolTip(_(u"Open existing project"))
        self.cmdOpen.Bind(wx.EVT_BUTTON, self.__frmMain.OnProjectLoad)

        sizerCmd = wx.BoxSizer(wx.HORIZONTAL)
        sizerCmd.Add(self.cmdNew, 0, wx.ALL, 30)
        sizerCmd.AddStretchSpacer(1)
        sizerCmd.Add(self.cmdOpen, 0, wx.ALL, 30)

        sizerMain = wx.BoxSizer(wx.VERTICAL)
        sizerMain.AddStretchSpacer(1)
        sizerMain.Add(sizerCmd, 0, wx.ALIGN_CENTER_HORIZONTAL, 8)
        sizerMain.Add(self.pnlHtmlBackground, 3, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 8)
        sizerMain.AddStretchSpacer(1)

        self.pnlHtmlBackground.SetSizer(sizerHtmlBackground)
        self.SetSizer(sizerMain)
        self.Layout()

        self.RefreshPage()

        self.__updateChecker = UpdateChecker()
        wx.CallLater(500, self.__NotifyUpdate)

    def RefreshPage(self, withHistory=True):
        if withHistory:
            htmlParts = []
            fileHistory = Settings().GetFileHistory()
            for recentFile in fileHistory:
                if ProjectFile(filename=recentFile).IsOk():
                    htmlPart = """<td align="center" valign="bottom">
                        <wxp module="photofilmstrip.gui.PnlWelcome" class="LinkOpenPfs">
                            <param name="filename" value="%s">
                        </wxp>
                    </td>""" % recentFile
                    htmlParts.append(htmlPart)

            breakAt = 4
            for idx in range((len(htmlParts) - 1) // breakAt):
                htmlParts.insert(idx + ((idx + 1) * breakAt), "</tr><tr>")

            if htmlParts:
                self.htmlTitle = _(u"Recent projects")
                self.htmlText = ""
            else:
                self.htmlTitle = _(u"How to start...")
                self.htmlText = _(u"Create a new project or load an existing one.")

            self.htmlRecentProjects = "".join(htmlParts)

        html = HTML_TEMPLATE % {'title': self.htmlTitle,
                                 'text': self.htmlText,
                                 'htmlRecentProjects': self.htmlRecentProjects,
                                 'htmlUpdate': self.htmlUpdate}

        self.htmlWin.SetPage(html)

    def __NotifyUpdate(self):
        if not self.__updateChecker.IsDone():
            wx.CallLater(100, self.__NotifyUpdate)
            return
        if not self.__updateChecker.IsOk():
            return
#        if not self.__updateChecker.IsNewer(Settings().GetLastKnownVersion()):
#            return
        if not self.__updateChecker.IsNewer(Constants.APP_VERSION):
            return

        Settings().SetLastKnownVersion(self.__updateChecker.GetVersion())

        html = """<h3 align="center">%(title)s</h3>
  <center>
    <wxp module="photofilmstrip.gui.PnlWelcome" class="PfsHyperlink">
        <param name="label" value="Download %(appname)s %(version)s">
    </wxp>
  </center>
  <p>%(msg)s</p>
  <pre>%(changes)s</pre>""" % {"title": _("Update available"),
                               "appname": Constants.APP_NAME,
                               "version": self.__updateChecker.GetVersion(),
                               "msg": _(u'The following changes has been made:'),
                               "changes": self.__updateChecker.GetChanges(),
                               "url": Constants.APP_URL}

        self.htmlUpdate = html
        self.RefreshPage(withHistory=False)

    def OnSize(self, event):
        self.Refresh()
        event.Skip()

    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self)
        sz = self.GetSize()
        dc.SetBackground(wx.Brush(wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE)))
        dc.Clear()

        rect = wx.Rect(0, 180, sz[0], sz[1])
        dc.GradientFillLinear(rect,
                              wx.SystemSettings.GetColour(wx.SYS_COLOUR_BTNFACE),
                              wx.Colour(52, 73, 94),
                              wx.SOUTH)

        font = wx.Font(28, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, 'Tahoma')
        dc.SetFont(font)
        dc.SetTextForeground(wx.Colour(99, 102, 106))
        dc.DrawLabel(self.title, wx.Rect(0, 10, sz[0], 75), wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_CENTER_VERTICAL)

        dc.DrawBitmap(self.bmpFilmstrip, 10, sz[1] - self.bmpFilmstrip.GetSize()[1] - 30)

    def OnLinkClicked(self, event):
        filename = event.GetFilename()
        self.__frmMain.LoadProject(filename)


class LinkOpenPfs(IconLabelLink):

    BMP_MAP = {}

    def __init__(self, parent, size=wx.DefaultSize, filename=None):
        self.filename = filename

        if filename not in LinkOpenPfs.BMP_MAP:
            prjFile = ProjectFile(filename=filename)
            imgCount = prjFile.GetPicCount()
            img = prjFile.GetPreviewThumb()
            if img is not None:
                wxImg = wx.Image(PILBackend.ImageToStream(img), wx.BITMAP_TYPE_JPEG)
                bmp = wxImg.ConvertToBitmap()
            else:
                bmp = wx.ArtProvider.GetBitmap("PFS_ICON_48", wx.ART_OTHER)
            descr = "%d images" % imgCount
            LinkOpenPfs.BMP_MAP[filename] = (bmp, descr)

        bmp, descr = LinkOpenPfs.BMP_MAP[filename]

        IconLabelLink.__init__(self, parent, size,
                               os.path.splitext(os.path.basename(filename))[0],
                               bmp,
                               descr)

    def OnClick(self):
        evt = LinkClickedEvent(self.GetParent().GetId(), self.filename)
        self.GetEventHandler().ProcessEvent(evt)


EVT_LINK_TYPE = wx.NewEventType()
EVT_LINK = wx.PyEventBinder(EVT_LINK_TYPE, 1)


class LinkClickedEvent(wx.PyCommandEvent):

    def __init__(self, wxId, filename):
        wx.PyCommandEvent.__init__(self, EVT_LINK_TYPE, wxId)
        self._filename = filename

    def GetFilename(self):
        return self._filename


class PfsHyperlink(wx.adv.HyperlinkCtrl):

    def __init__(self, parent, size=wx.DefaultSize, label=""):
        wx.adv.HyperlinkCtrl.__init__(self, parent, -1, label, size=size)
        self.SetBackgroundColour(parent.GetBackgroundColour())
        self.SetURL(Constants.APP_URL)


HTML_TEMPLATE = """<html>
  <body bgcolor="#EBEBEB" witdth="650px">
  <font color="#63666A" face="Tahoma">
    <h3 align="center">%(title)s</h3>

    <center>
        <table border="0" cellspacing="0" cellpadding="0">
            <tr>%(htmlRecentProjects)s</tr>
        </table>
    </center>

    <h5 align="center">%(text)s</h5>
    %(htmlUpdate)s
  </font>
  </body>
</html>"""
