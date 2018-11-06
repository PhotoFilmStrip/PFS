# Boa:Dialog:DlgRender
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

import wx
import wx.adv

from photofilmstrip.core.OutputProfile import (
        GetOutputProfiles, GetMPEGProfiles)
from photofilmstrip.core.Renderer import RENDERERS

from photofilmstrip.lib.Settings import Settings

from photofilmstrip.gui.ctrls.PnlDlgHeader import PnlDlgHeader
from photofilmstrip.gui.HelpViewer import HelpViewer
from photofilmstrip.gui.DlgRendererProps import DlgRendererProps

[wxID_DLGRENDER, wxID_DLGRENDERCBDRAFT, wxID_DLGRENDERCHOICEFORMAT,
 wxID_DLGRENDERCHOICEPROFILE,
 wxID_DLGRENDERCMDCANCEL, wxID_DLGRENDERCMDHELP,
 wxID_DLGRENDERCMDRENDERERPROPS, wxID_DLGRENDERCMDSTART, wxID_DLGRENDERPNLHDR,
 wxID_DLGRENDERPNLSETTINGS, wxID_DLGRENDERSTFORMAT, wxID_DLGRENDERSTPROFILE,
] = [wx.NewId() for _init_ctrls in range(12)]


class DlgRender(wx.Dialog):

    _custom_classes = {"wx.Choice": ["FormatComboBox"],
                       "wx.Panel": ["PnlDlgHeader"]}

    DEFAULT_FORMAT = u"x264/AC3 (MKV)"
    DEFAULT_PROFILE = u"HD 720p@25.00 fps"

    def _init_coll_sizerMain_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.pnlHdr, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.pnlSettings, 0, border=4, flag=wx.ALL)
        parent.AddSpacer(8)
        parent.Add(self.sizerCmd, 0, border=4, flag=wx.EXPAND | wx.ALL)

    def _init_coll_sizerCmd_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.cmdHelp, 0, border=0, flag=0)
        parent.AddStretchSpacer(1)
        parent.Add(self.cmdCancel, 0, border=0, flag=0)
        parent.AddSpacer(8)
        parent.Add(self.cmdStart, 0, border=0, flag=0)

    def _init_coll_sizerSettings_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.stFormat, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.Add(self.choiceFormat, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.Add(self.cmdRendererProps, 0, border=0, flag=0)
        parent.Add(self.stProfile, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.Add(self.choiceProfile, 0, border=0, flag=wx.EXPAND)
        parent.AddSpacer(8)
        parent.AddSpacer(8)
        parent.Add(self.cbDraft, 0, border=0, flag=0)

    def _init_coll_sizerSettings_Growables(self, parent):
        # generated method, don't edit

        parent.AddGrowableCol(2)

    def _init_sizers(self):
        # generated method, don't edit
        self.sizerMain = wx.BoxSizer(orient=wx.VERTICAL)

        self.sizerCmd = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.sizerSettings = wx.FlexGridSizer(cols=3, hgap=8, rows=5, vgap=8)
        self.sizerSettings.SetFlexibleDirection(wx.BOTH)

        self._init_coll_sizerMain_Items(self.sizerMain)
        self._init_coll_sizerCmd_Items(self.sizerCmd)
        self._init_coll_sizerSettings_Items(self.sizerSettings)
        self._init_coll_sizerSettings_Growables(self.sizerSettings)

        self.SetSizer(self.sizerMain)
        self.pnlSettings.SetSizer(self.sizerSettings)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_DLGRENDER, name=u'DlgRender',
            parent=prnt, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
            style=wx.DEFAULT_DIALOG_STYLE, title=_(u'Render project'))

        self.pnlHdr = PnlDlgHeader(id=wxID_DLGRENDERPNLHDR, name=u'pnlHdr',
            parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
            style=wx.TAB_TRAVERSAL)

        self.pnlSettings = wx.Panel(id=wxID_DLGRENDERPNLSETTINGS,
            name=u'pnlSettings', parent=self, pos=wx.Point(-1, -1),
            size=wx.Size(-1, -1), style=wx.TAB_TRAVERSAL)

        self.stFormat = wx.StaticText(id=wxID_DLGRENDERSTFORMAT,
            label=_(u'Format:'), name=u'stFormat', parent=self.pnlSettings,
            pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.choiceFormat = FormatComboBox(choices=[],
            id=wxID_DLGRENDERCHOICEFORMAT, name=u'choiceFormat',
            parent=self.pnlSettings, pos=wx.Point(-1, -1),
            size=wx.Size(-1, -1), style=wx.CB_READONLY)
        self.choiceFormat.SetSizeHints(400, -1)
        self.choiceFormat.Bind(wx.EVT_COMBOBOX, self.OnChoiceFormat,
            id=wxID_DLGRENDERCHOICEFORMAT)

        self.cmdRendererProps = wx.BitmapButton(bitmap=wx.ArtProvider.GetBitmap('PFS_VIDEO_FORMAT_16'),
              id=wxID_DLGRENDERCMDRENDERERPROPS, name=u'cmdRendererProps',
              parent=self.pnlSettings, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.BU_AUTODRAW)
        self.cmdRendererProps.SetToolTip(_(u"Properties"))
        self.cmdRendererProps.Bind(wx.EVT_BUTTON, self.OnCmdRendererPropsButton,
            id=wxID_DLGRENDERCMDRENDERERPROPS)

        self.stProfile = wx.StaticText(id=wxID_DLGRENDERSTPROFILE,
            label=_(u'Profile:'), name=u'stProfile', parent=self.pnlSettings,
            pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.choiceProfile = wx.Choice(choices=[],
            id=wxID_DLGRENDERCHOICEPROFILE, name=u'choiceProfile',
            parent=self.pnlSettings, pos=wx.Point(-1, -1), size=wx.Size(-1,
            -1), style=0)
        self.choiceProfile.SetSizeHints(400, -1)

        self.cbDraft = wx.CheckBox(id=wxID_DLGRENDERCBDRAFT, label=_(u'Draft'),
            name=u'cbDraft', parent=self.pnlSettings, pos=wx.Point(-1, -1),
            size=wx.Size(-1, -1), style=0)
        self.cbDraft.SetValue(False)

        self.cmdHelp = wx.Button(id=wx.ID_HELP, label=_(u'&Help'),
            name=u'cmdHelp', parent=self, pos=wx.Point(-1, -1),
            size=wx.Size(-1, -1), style=0)
        self.cmdHelp.Bind(wx.EVT_BUTTON, self.OnCmdHelpButton, id=wx.ID_HELP)

        self.cmdCancel = wx.Button(id=wxID_DLGRENDERCMDCANCEL,
            label=_(u'&Cancel'), name=u'cmdCancel', parent=self,
            pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)
        self.cmdCancel.Bind(wx.EVT_BUTTON, self.OnCmdCancelButton,
            id=wxID_DLGRENDERCMDCANCEL)

        self.cmdStart = wx.Button(id=wxID_DLGRENDERCMDSTART, label=_(u'&Start'),
            name=u'cmdStart', parent=self, pos=wx.Point(-1, -1),
            size=wx.Size(-1, -1), style=0)
        self.cmdStart.Bind(wx.EVT_BUTTON, self.OnCmdStartButton,
            id=wxID_DLGRENDERCMDSTART)

        self._init_sizers()

    def __init__(self, parent, aspectRatio):
        self._init_ctrls(parent)
        self.Bind(wx.EVT_CLOSE, self.OnCmdCancelButton)

        self.pnlHdr.SetTitle(_('Configure output and start render process'))
        self.pnlHdr.SetBitmap(wx.ArtProvider.GetBitmap('PFS_RENDER_32'))

        self.cbDraft.SetToolTip(_(u"Activate this option to generate a preview of your PhotoFilmStrip. The rendering process will speed up dramatically, but results in lower quality."))

        self.aspectRatio = aspectRatio
        self.__InitProfiles()

        settings = Settings()
        if settings.GetUsedRenderer() is None:
            self.choiceFormat.SetStringSelection(self.DEFAULT_FORMAT)
        else:
            self.choiceFormat.SetSelection(settings.GetUsedRenderer())
        self.OnChoiceFormat(None)

        self.__SelectProfileByName(settings.GetLastProfile())

        self.SetEscapeId(wxID_DLGRENDERCMDCANCEL)
        self.Fit()
        self.CentreOnParent()
        self.SetFocus()

        self.profile = None
        self.draftMode = False
        self.rendererClass = None

    def __GetChoiceDataSelected(self, choice):
        return choice.GetClientData(choice.GetSelection())

    def __SelectProfileByName(self, profName):
        if profName is None:
            profName = self.DEFAULT_PROFILE
        choice = self.choiceProfile
        for idx in range(choice.GetCount()):
            prof = choice.GetClientData(idx)
            if prof and prof.GetName() == profName:
                choice.Select(idx)
                return

        choice.Select(0)

    def __InitProfiles(self, filtr=None, profiles=None):
        if profiles is None:
            profiles = []
            profs = GetOutputProfiles(self.aspectRatio)
            for prof in profs:
                if prof.GetFriendlyName():
                    profiles.append(prof)
            profiles.append("-")
            profiles.extend(profs)

        selection = self.choiceFormat.GetStringSelection()
        self.choiceProfile.Clear()

        useFriendlyName = True
        for profile in profiles:
            if profile == "-":
                self.choiceProfile.Append(u"----------")
                useFriendlyName = False
                continue

            if filtr and not profile.GetName().startswith(filtr):
                continue

            if useFriendlyName:
                profName = profile.GetFriendlyName()
            else:
                profName = profile.GetName()

            self.choiceProfile.Append(u"%s (%sx%s)" % (profName,
                                                       profile.GetResolution()[0],
                                                       profile.GetResolution()[1]),
                                      profile)

        self.choiceProfile.SetStringSelection(selection)

    def OnChoiceFormat(self, event):
        if event is None:
            formatData = self.__GetChoiceDataSelected(self.choiceFormat)
        else:
            formatData = event.GetClientData()

        if isinstance(formatData, FormatData):
            self.cmdStart.Enable(formatData.IsOk())
            if formatData.IsMPEG():
                self.__InitProfiles(formatData.GetRendererClass().GetName().split(" ")[0],
                                    GetMPEGProfiles())
            else:
                self.__InitProfiles()

        self.__SelectProfileByName(Settings().GetLastProfile())

    def OnCmdStartButton(self, event):
        formatData = self.__GetChoiceDataSelected(self.choiceFormat)
        self.rendererClass = formatData.GetRendererClass()

        profile = self.__GetChoiceDataSelected(self.choiceProfile)
        if profile is None:
            return

        self.profile = profile
        self.draftMode = self.cbDraft.GetValue()

        self.EndModal(wx.ID_OK)

    def OnCmdCancelButton(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnCmdRendererPropsButton(self, event):
        data = self.__GetChoiceDataSelected(self.choiceFormat)
        if data is None:
            return
        rendererClass = data.GetRendererClass()

        dlg = DlgRendererProps(self, rendererClass)
        dlg.ShowModal()
        dlg.Destroy()

    def OnCmdHelpButton(self, event):
        HelpViewer().DisplayID(HelpViewer.ID_RENDER)
        event.Skip()

    def GetProfile(self):
        return self.profile

    def GetDraftMode(self):
        return self.draftMode

    def GetRendererClass(self):
        return self.rendererClass


class FormatComboBox(wx.adv.OwnerDrawnComboBox):

    def __init__(self, *args, **kwargs):
        wx.adv.OwnerDrawnComboBox.__init__(self, *args, **kwargs)

        for rend in RENDERERS:
            self.AddRenderer(rend)

    def AddRenderer(self, rend, altName=None):
        msgList = []
        rend.CheckDependencies(msgList)
        self.Append(altName or rend.GetName(),
                    FormatData(rend, msgList))

    def SetSelection(self, index):
        if index >= self.GetCount():
            index = 0
        wx.adv.OwnerDrawnComboBox.SetSelection(self, index)

    def OnDrawItem(self, dc, rect, item, flags):
        if item == wx.NOT_FOUND:
            return

        data = self.GetClientData(item)

        rect2 = wx.Rect(*rect)
        rect2.Deflate(5, 0)

        if data.GetMessages():
            bmp = wx.ArtProvider.GetBitmap('PFS_ALERT_16')
            dc.SetTextForeground(wx.SystemSettings.GetColour(wx.SYS_COLOUR_GRAYTEXT))
        else:
            bmp = wx.NullBitmap
            if flags & wx.adv.ODCB_PAINTING_SELECTED:
                dc.SetTextForeground(wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT))
            else:
                dc.SetTextForeground(wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOWTEXT))

        if flags & wx.adv.ODCB_PAINTING_CONTROL:
            dc.DrawLabel(self.GetString(item), rect2, wx.ALIGN_CENTER_VERTICAL)
        else:
            dc.DrawLabel("\n".join([self.GetString(item)] + data.GetMessages()),
                         bmp, rect2,
                         wx.ALIGN_CENTER_VERTICAL)

    def OnMeasureItem(self, item):
        data = self.GetClientData(item)
        height = self.GetTextExtent(self.GetString(item))[1] * (len(data.GetMessages()) + 1)
        return height + 8


class FormatData:

    MPEG_PROFILES = ("VCD", "SVCD", "DVD")

    def __init__(self, rendClass, msgList):
        self._rendererClass = rendClass
        self._msgList = msgList

    def IsOk(self):
        return len(self._msgList) == 0

    def IsMPEG(self):
        for mpegProf in FormatData.MPEG_PROFILES:
            if self._rendererClass.GetName().startswith(mpegProf):
                return True
        return False

    def GetRendererClass(self):
        return self._rendererClass

    def GetMessages(self):
        return self._msgList
