#Boa:Dialog:DlgRender
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

import os

import wx
import wx.combo


from photofilmstrip.core.OutputProfile import (
        OutputProfile, GetOutputProfiles, GetMPEGProfiles)
from photofilmstrip.core.Renderer import RENDERERS

from photofilmstrip.lib.Settings import Settings
from photofilmstrip.lib.jobimpl.JobManager import JobManager

from photofilmstrip.gui.ctrls.PnlDlgHeader import PnlDlgHeader
from photofilmstrip.gui.HelpViewer import HelpViewer
from photofilmstrip.gui.DlgRendererProps import DlgRendererProps
from photofilmstrip.action.ActionRender import ActionRender


[wxID_DLGRENDER, wxID_DLGRENDERCBDRAFT, wxID_DLGRENDERCHOICEFORMAT, 
 wxID_DLGRENDERCHOICEPROFILE, wxID_DLGRENDERCHOICETYPE, 
 wxID_DLGRENDERCMDCANCEL, wxID_DLGRENDERCMDHELP, 
 wxID_DLGRENDERCMDRENDERERPROPS, wxID_DLGRENDERCMDSTART, wxID_DLGRENDERPNLHDR, 
 wxID_DLGRENDERPNLSETTINGS, wxID_DLGRENDERSTFORMAT, wxID_DLGRENDERSTPROFILE, 
 wxID_DLGRENDERSTTYPE, 
] = [wx.NewId() for _init_ctrls in range(14)]


class DlgRender(wx.Dialog):
    
    _custom_classes = {"wx.Choice": ["FormatComboBox"],
                       "wx.Panel": ["PnlDlgHeader"]}
    
    def _init_coll_sizerMain_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.pnlHdr, 0, border=0, flag=wx.EXPAND)
        parent.AddWindow(self.pnlSettings, 0, border=4, flag=wx.ALL)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddSizer(self.sizerCmd, 0, border=4, flag=wx.EXPAND | wx.ALL)

    def _init_coll_sizerCmd_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.cmdHelp, 0, border=0, flag=0)
        parent.AddStretchSpacer(1)
        parent.AddWindow(self.cmdCancel, 0, border=0, flag=0)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.cmdStart, 0, border=0, flag=0)

    def _init_coll_sizerSettings_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stFormat, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.choiceFormat, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.cmdRendererProps, 0, border=0, flag=0)
        parent.AddWindow(self.stProfile, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.choiceProfile, 0, border=0, flag=wx.EXPAND)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.stType, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.choiceType, 0, border=0, flag=wx.EXPAND)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.cbDraft, 0, border=0, flag=0)

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
              style=wx.DEFAULT_DIALOG_STYLE, title=_(u'Render filmstrip'))
        self.SetClientSize(wx.Size(400, 250))

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
              parent=self.pnlSettings, pos=wx.Point(-1, -1), size=wx.Size(-1,
              -1), style=wx.CB_READONLY)
        self.choiceFormat.SetMinSize(wx.Size(300, -1))
        self.choiceFormat.Bind(wx.EVT_COMBOBOX, self.OnChoiceFormat,
              id=wxID_DLGRENDERCHOICEFORMAT)

        self.cmdRendererProps = wx.BitmapButton(bitmap=wx.ArtProvider.GetBitmap('wxART_EXECUTABLE_FILE',
              wx.ART_TOOLBAR, (16, 16)),
              id=wxID_DLGRENDERCMDRENDERERPROPS, name=u'cmdRendererProps',
              parent=self.pnlSettings, pos=wx.Point(-1, -1), size=wx.Size(-1,
              -1), style=wx.BU_AUTODRAW)
        self.cmdRendererProps.SetToolTipString(_("Properties"))
        self.cmdRendererProps.Bind(wx.EVT_BUTTON, self.OnCmdRendererPropsButton,
              id=wxID_DLGRENDERCMDRENDERERPROPS)

        self.stProfile = wx.StaticText(id=wxID_DLGRENDERSTPROFILE,
              label=_(u'Resolution:'), name=u'stProfile', parent=self.pnlSettings,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.choiceProfile = wx.Choice(choices=[],
              id=wxID_DLGRENDERCHOICEPROFILE, name=u'choiceProfile',
              parent=self.pnlSettings, pos=wx.Point(-1, -1), size=wx.Size(-1,
              -1), style=0)
        self.choiceProfile.SetMinSize(wx.Size(300, -1))

        self.stType = wx.StaticText(id=wxID_DLGRENDERSTTYPE, label=_(u'Type:'),
              name=u'stType', parent=self.pnlSettings, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.choiceType = wx.Choice(choices=[], id=wxID_DLGRENDERCHOICETYPE,
              name=u'choiceType', parent=self.pnlSettings, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)
        self.choiceType.SetMinSize(wx.Size(300, -1))

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

    def __init__(self, parent, photoFilmStrip):
        self._init_ctrls(parent)
        self.Bind(wx.EVT_CLOSE, self.OnCmdCancelButton)
        
        self.pnlHdr.SetTitle(_('Configure output and start render process'))
        self.pnlHdr.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_TICK_MARK,
              wx.ART_TOOLBAR, (32, 32)))
        
        self.cbDraft.SetToolTipString(_(u"Activate this option to generate a preview of your PhotoFilmStrip. The rendering process will speed up dramatically, but results in lower quality."))

        self.__photoFilmStrip = photoFilmStrip
        self.__renderEngine = None
        
        for profile in GetOutputProfiles(photoFilmStrip.GetAspect()):
            self.choiceProfile.Append(u"%s (%sx%s)" % (profile.GetName(),
                                                       profile.GetResolution()[0],
                                                       profile.GetResolution()[1]), 
                                      profile)
        
        self.choiceType.Append("PAL", OutputProfile.PAL)
        self.choiceType.Append("NTSC", OutputProfile.NTSC)
        self.choiceType.SetSelection(0)

        audioFile = self.__photoFilmStrip.GetAudioFile()
        if audioFile and not os.path.exists(audioFile):
            self.pnlHdr.SetErrorMessage(_(u"Audio file '%s' does not exist!") % audioFile)

        settings = Settings()
        self.choiceProfile.SetSelection(settings.GetLastProfile())
        
        self.__SetChoiceSelectionByData(self.choiceType, settings.GetVideoType())
        self.choiceFormat.SetSelection(settings.GetUsedRenderer())
        self.OnChoiceFormat(None)
        
        self.SetEscapeId(wxID_DLGRENDERCMDCANCEL)
        self.SetInitialSize(self.GetEffectiveMinSize())
        self.CentreOnParent()
        self.SetFocus()
        
    def __GetChoiceDataSelected(self, choice):
        return choice.GetClientData(choice.GetSelection())
    
    def __SetChoiceSelectionByData(self, choice, data):
        for idx in range(choice.GetCount()):
            if choice.GetClientData(idx) == data:
                choice.Select(idx)
                return

    def __GetOutputPath(self):
        profile = self.__GetChoiceDataSelected(self.choiceProfile)
        outpath = os.path.dirname(self.__photoFilmStrip.GetFilename())
        outpath = os.path.join(outpath, profile.GetName())
        return outpath
    
    def OnChoiceFormat(self, event):
        if event is None:
            formatData = self.__GetChoiceDataSelected(self.choiceFormat)
        else:
            formatData = event.GetClientData()
        
        strAuto = _(u"Automatic")
        idxAuto = self.choiceProfile.FindString(strAuto)
        if idxAuto != wx.NOT_FOUND:
            self.choiceProfile.Delete(idxAuto)
            
        if isinstance(formatData, FormatData):
            self.cmdStart.Enable(formatData.IsOk())
            if formatData.IsMPEG():
                self.choiceProfile.Append(strAuto)
                self.choiceProfile.SetStringSelection(strAuto)
                self.choiceProfile.Enable(False)
            else:
                self.choiceProfile.Enable(True)
                self.choiceProfile.Select(0)

    def OnCmdStartButton(self, event):
        formatData = self.__GetChoiceDataSelected(self.choiceFormat)
        rendererClass = formatData.PRendererClass

        profile = GetMPEGProfiles().get(rendererClass.GetName())
        if profile is None:
            profile = self.__GetChoiceDataSelected(self.choiceProfile)
        if profile is None:
            return
            
        ar = ActionRender(self.__photoFilmStrip, 
                          profile, 
                          self.__GetChoiceDataSelected(self.choiceType), 
                          rendererClass, 
                          self.cbDraft.GetValue())
        
        audioFile = self.__photoFilmStrip.GetAudioFile()
        if not ar.CheckFile(audioFile):
            dlg = wx.MessageDialog(self,
                                   _(u"Audio file '%s' does not exist! Continue anyway?") % audioFile, 
                                   _(u"Warning"),
                                   wx.YES_NO | wx.ICON_WARNING)
            try:
                if dlg.ShowModal() == wx.ID_NO:
                    return
            finally:
                dlg.Destroy()
            
        ar.Execute()
        renderJob = ar.GetRenderJob()
        JobManager().EnqueueContext(renderJob)
        self.EndModal(wx.ID_OK)

    def OnCmdCancelButton(self, event):
        self.EndModal(wx.ID_CANCEL)

    def OnCmdRendererPropsButton(self, event):
        data = self.__GetChoiceDataSelected(self.choiceFormat)
        if data is None:
            return
        rendererClass = data.PRendererClass
        
        dlg = DlgRendererProps(self, rendererClass)
        dlg.ShowModal()
        dlg.Destroy()
        
    def OnCmdHelpButton(self, event):
        HelpViewer().DisplayID(HelpViewer.ID_RENDER)
        event.Skip()


class FormatComboBox(wx.combo.OwnerDrawnComboBox):
    
    def __init__(self, *args, **kwargs):
        wx.combo.OwnerDrawnComboBox.__init__(self, *args, **kwargs)

        for rend in RENDERERS:
            if rend.GetName() in FormatData.MPEG_PROFILES:
                continue
            
            self.AddRenderer(rend)
            
    def AddRenderer(self, rend, altName=None):
        msgList = []
        rend.CheckDependencies(msgList)
        self.Append(altName or rend.GetName(), 
                    FormatData(rend, msgList))
    
    def SetSelection(self, index):
        if index >= self.GetCount():
            index = 0
        wx.combo.OwnerDrawnComboBox.SetSelection(self, index)

    def OnDrawItem(self, dc, rect, item, flags):
        if item == wx.NOT_FOUND:
            return

        data = self.GetClientData(item)
        
        rect2 = wx.Rect(*rect)
        rect2.Deflate(5, 0)

        if data.PMessages:
            bmp = wx.ArtProvider_GetBitmap(wx.ART_ERROR, wx.ART_OTHER, (16, 16))
            dc.SetTextForeground(wx.SystemSettings_GetColour(wx.SYS_COLOUR_GRAYTEXT))
        else:
            bmp = wx.NullBitmap
            if flags & wx.combo.ODCB_PAINTING_SELECTED:
                dc.SetTextForeground(wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHTTEXT))
            else:
                dc.SetTextForeground(wx.SystemSettings_GetColour(wx.SYS_COLOUR_WINDOWTEXT))

        if flags & wx.combo.ODCB_PAINTING_CONTROL:
            dc.DrawLabel(self.GetString(item), rect2, wx.ALIGN_CENTER_VERTICAL) 
        
        else:
            dc.DrawImageLabel("\n".join([self.GetString(item)] + data.PMessages), 
                              bmp, rect2, 
                              wx.ALIGN_CENTER_VERTICAL) 

    def OnMeasureItem(self, item):
        data = self.GetClientData(item)
        height = self.GetTextExtent(self.GetString(item))[1] * (len(data.PMessages) + 1)
        return height + 8


class FormatData(object):
    
    MPEG_PROFILES = ("VCD", "SVCD", "DVD")
    
    def __init__(self, rendClass, msgList):
        self.PRendererClass = rendClass
        self.PMessages = msgList

    def IsOk(self):
        return len(self.PMessages) == 0
    
    def IsMPEG(self):
        for mpegProf in FormatData.MPEG_PROFILES:
            if self.PRendererClass.GetName().startswith(mpegProf):
                return True
        return False 
