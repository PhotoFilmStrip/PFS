#Boa:Dialog:DlgRender
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
import thread

import wx
import wx.media
import wx.lib.masked.timectrl


from core.OutputProfile import OutputProfile
from core.ProgressHandler import ProgressHandler
from core.RenderEngine import RenderEngine
from core.renderer import RENDERERS

from lib.common.ObserverPattern import Observer
from lib.Settings import Settings


[wxID_DLGRENDER, wxID_DLGRENDERCBTOTALLENGTH, wxID_DLGRENDERCHOICEFORMAT, 
 wxID_DLGRENDERCHOICEPROFILE, wxID_DLGRENDERCHOICETYPE, 
 wxID_DLGRENDERCMDAUDIOPREVIEW, wxID_DLGRENDERCMDBROWSEAUDIO, 
 wxID_DLGRENDERCMDBROWSEOUTPUTDIR, wxID_DLGRENDERCMDCLOSE, 
 wxID_DLGRENDERCMDSTART, wxID_DLGRENDERGAUGEPROGRESS, wxID_DLGRENDERLCPROPS, 
 wxID_DLGRENDERPNLOUTPUT, wxID_DLGRENDERPNLSETTINGS, wxID_DLGRENDERRBAUDIO, 
 wxID_DLGRENDERRBMANUAL, wxID_DLGRENDERSLOUTPUT, wxID_DLGRENDERSLSETTINGS, 
 wxID_DLGRENDERSPINBUTTONTRANSDUR, wxID_DLGRENDERSTATICLINE1, 
 wxID_DLGRENDERSTFORMAT, wxID_DLGRENDERSTOUTPUTDIR, 
 wxID_DLGRENDERSTOUTPUTHEADER, wxID_DLGRENDERSTPROFILE, 
 wxID_DLGRENDERSTPROGRESS, wxID_DLGRENDERSTSETTINGSHEADER, 
 wxID_DLGRENDERSTSIZEDESCR, wxID_DLGRENDERSTTRANSDUR, 
 wxID_DLGRENDERSTTRANSDURUNIT, wxID_DLGRENDERSTTYPE, 
 wxID_DLGRENDERSTTYPEDESCR, wxID_DLGRENDERTCAUDIOFILE, 
 wxID_DLGRENDERTCOUTPUTDIR, wxID_DLGRENDERTCTRANSDURATION, 
 wxID_DLGRENDERTIMECTRLTOTALLENGTH, 
] = [wx.NewId() for _init_ctrls in range(35)]


class DlgRender(wx.Dialog, Observer):
    def _init_coll_sizerSettingsCtrls_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stProfile, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.choiceProfile, 0, border=0, flag=wx.EXPAND)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.stType, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.choiceType, 0, border=0, flag=wx.EXPAND)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.stTransDur, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddSizer(self.sizerTransDuration, 0, border=0, flag=wx.EXPAND)
        parent.AddWindow(self.stTransDurUnit, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.cbTotalLength, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.rbManual, 0, border=20,
              flag=wx.LEFT | wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.timeCtrlTotalLength, 0, border=0, flag=wx.EXPAND)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.rbAudio, 0, border=20,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT)
        parent.AddWindow(self.tcAudiofile, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddSizer(self.sizerAudio, 0, border=0, flag=0)

    def _init_coll_sizerOutput_Items(self, parent):
        # generated method, don't edit

        parent.AddSpacer(wx.Size(16, 8), border=0, flag=0)
        parent.AddWindow(self.pnlOutput, 1, border=0, flag=0)

    def _init_coll_sizerMain_Items(self, parent):
        # generated method, don't edit

        parent.AddSizer(self.sizerSettingsHeader, 0, border=0, flag=wx.EXPAND)
        parent.AddSizer(self.sizerSettings, 0, border=4, flag=wx.EXPAND | wx.RIGHT)
        parent.AddSpacer(wx.Size(8, 16), border=0, flag=0)
        parent.AddSizer(self.sizerOutputHeader, 0, border=0, flag=wx.EXPAND)
        parent.AddSizer(self.sizerOutput, 0, border=4, flag=wx.EXPAND | wx.RIGHT)
        parent.AddSpacer(wx.Size(8, 16), border=0, flag=0)
        parent.AddSizer(self.sizerCmd, 0, border=4,
              flag=wx.ALL | wx.ALIGN_CENTER_HORIZONTAL)
        parent.AddWindow(self.staticLine1, 0, border=4,
              flag=wx.BOTTOM | wx.TOP | wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL)
        parent.AddWindow(self.gaugeProgress, 0, border=4,
              flag=wx.ALL | wx.EXPAND)
        parent.AddWindow(self.stProgress, 0, border=4,
              flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL)

    def _init_coll_sizerSettingsCtrls_Growables(self, parent):
        # generated method, don't edit

        parent.AddGrowableCol(2)

    def _init_coll_sizerOutputDir_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.tcOutputDir, 1, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.cmdBrowseOutputDir, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)

    def _init_coll_sizerOutputHeader_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stOutputHeader, 0, border=4, flag=wx.ALL)
        parent.AddWindow(self.slOutput, 1, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)

    def _init_coll_sizerCmd_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.cmdStart, 0, border=0, flag=0)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.cmdClose, 0, border=0, flag=0)

    def _init_coll_sizerOutputCtrls_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stFormat, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.choiceFormat, 0, border=0, flag=wx.EXPAND)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.lcProps, 0, border=0, flag=wx.EXPAND)
        parent.AddWindow(self.stOutputDir, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddSizer(self.sizerOutputDir, 0, border=0, flag=wx.EXPAND)

    def _init_coll_sizerOutputCtrls_Growables(self, parent):
        # generated method, don't edit

        parent.AddGrowableCol(1)

    def _init_coll_sizerAudio_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.cmdBrowseAudio, 0, border=0, flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.cmdAudioPreview, 0, border=0, flag=wx.ALIGN_CENTER_VERTICAL)

    def _init_coll_sizerSettings_Items(self, parent):
        # generated method, don't edit

        parent.AddSpacer(wx.Size(16, 8), border=0, flag=0)
        parent.AddWindow(self.pnlSettings, 1, border=0, flag=0)

    def _init_coll_sizerTransDuration_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.tcTransDuration, 1, border=0, flag=0)
        parent.AddWindow(self.spinButtonTransDur, 0, border=0, flag=0)

    def _init_coll_sizerSettingsHeader_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stSettingsHeader, 0, border=4, flag=wx.ALL)
        parent.AddWindow(self.slSettings, 1, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)

    def _init_coll_lcProps_Columns(self, parent):
        # generated method, don't edit

        parent.InsertColumn(col=0, format=wx.LIST_FORMAT_LEFT,
              heading=_(u'Property'), width=200)
        parent.InsertColumn(col=1, format=wx.LIST_FORMAT_LEFT,
              heading=_(u'Value'), width=200)

    def _init_sizers(self):
        # generated method, don't edit
        self.sizerMain = wx.BoxSizer(orient=wx.VERTICAL)

        self.sizerCmd = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.sizerSettingsCtrls = wx.FlexGridSizer(cols=3, hgap=8, rows=5,
              vgap=8)
        self.sizerSettingsCtrls.SetFlexibleDirection(wx.BOTH)

        self.sizerTransDuration = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.sizerSettingsHeader = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.sizerSettings = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.sizerOutputHeader = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.sizerOutput = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.sizerOutputCtrls = wx.FlexGridSizer(cols=2, hgap=8, rows=2, vgap=8)
        self.sizerOutputCtrls.SetFlexibleDirection(wx.BOTH)

        self.sizerOutputDir = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.sizerAudio = wx.BoxSizer(orient=wx.HORIZONTAL)

        self._init_coll_sizerMain_Items(self.sizerMain)
        self._init_coll_sizerCmd_Items(self.sizerCmd)
        self._init_coll_sizerSettingsCtrls_Items(self.sizerSettingsCtrls)
        self._init_coll_sizerSettingsCtrls_Growables(self.sizerSettingsCtrls)
        self._init_coll_sizerTransDuration_Items(self.sizerTransDuration)
        self._init_coll_sizerSettingsHeader_Items(self.sizerSettingsHeader)
        self._init_coll_sizerSettings_Items(self.sizerSettings)
        self._init_coll_sizerOutputHeader_Items(self.sizerOutputHeader)
        self._init_coll_sizerOutput_Items(self.sizerOutput)
        self._init_coll_sizerOutputCtrls_Items(self.sizerOutputCtrls)
        self._init_coll_sizerOutputCtrls_Growables(self.sizerOutputCtrls)
        self._init_coll_sizerOutputDir_Items(self.sizerOutputDir)
        self._init_coll_sizerAudio_Items(self.sizerAudio)

        self.SetSizer(self.sizerMain)
        self.pnlOutput.SetSizer(self.sizerOutputCtrls)
        self.pnlSettings.SetSizer(self.sizerSettingsCtrls)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_DLGRENDER, name=u'DlgRender',
              parent=prnt, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.DEFAULT_DIALOG_STYLE, title=_(u'Render filmstrip'))
        self.SetClientSize(wx.Size(400, 250))

        self.stSettingsHeader = wx.StaticText(id=wxID_DLGRENDERSTSETTINGSHEADER,
              label=_(u'Settings'), name=u'stSettingsHeader', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.slSettings = wx.StaticLine(id=wxID_DLGRENDERSLSETTINGS,
              name=u'slSettings', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.pnlSettings = wx.Panel(id=wxID_DLGRENDERPNLSETTINGS,
              name=u'pnlSettings', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.TAB_TRAVERSAL)

        self.stProfile = wx.StaticText(id=wxID_DLGRENDERSTPROFILE,
              label=_(u'Profile:'), name=u'stProfile', parent=self.pnlSettings,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.choiceProfile = wx.Choice(choices=[],
              id=wxID_DLGRENDERCHOICEPROFILE, name=u'choiceProfile',
              parent=self.pnlSettings, pos=wx.Point(-1, -1), size=wx.Size(-1,
              -1), style=0)

        self.stSizeDescr = wx.StaticText(id=wxID_DLGRENDERSTSIZEDESCR,
              label=u'', name=u'stSizeDescr', parent=self.pnlSettings,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.stType = wx.StaticText(id=wxID_DLGRENDERSTTYPE, label=_(u'Type:'),
              name=u'stType', parent=self.pnlSettings, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.choiceType = wx.Choice(choices=[], id=wxID_DLGRENDERCHOICETYPE,
              name=u'choiceType', parent=self.pnlSettings, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.stTypeDescr = wx.StaticText(id=wxID_DLGRENDERSTTYPEDESCR,
              label=u'', name=u'stTypeDescr', parent=self.pnlSettings,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.stTransDur = wx.StaticText(id=wxID_DLGRENDERSTTRANSDUR,
              label=_(u'Transition speed:'), name=u'stTransDur',
              parent=self.pnlSettings, pos=wx.Point(-1, -1), size=wx.Size(-1,
              -1), style=0)

        self.tcTransDuration = wx.TextCtrl(id=wxID_DLGRENDERTCTRANSDURATION,
              name=u'tcTransDuration', parent=self.pnlSettings, pos=wx.Point(-1,
              -1), size=wx.Size(-1, -1), style=0, value=u'1.0')

        self.spinButtonTransDur = wx.SpinButton(id=wxID_DLGRENDERSPINBUTTONTRANSDUR,
              name=u'spinButtonTransDur', parent=self.pnlSettings,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=wx.SP_VERTICAL)

        self.stTransDurUnit = wx.StaticText(id=wxID_DLGRENDERSTTRANSDURUNIT,
              label=_(u'Sec.'), name=u'stTransDurUnit', parent=self.pnlSettings,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.cbTotalLength = wx.CheckBox(id=wxID_DLGRENDERCBTOTALLENGTH,
              label=_(u'Total length:'), name=u'cbTotalLength',
              parent=self.pnlSettings, pos=wx.Point(-1, -1), size=wx.Size(-1,
              -1), style=0)
        self.cbTotalLength.SetValue(False)
        self.cbTotalLength.SetToolTipString(_(u'Overrides the duration of single pictures and gives the photo filmstrip this total length.'))
        self.cbTotalLength.Bind(wx.EVT_CHECKBOX,
              self.OnControlStatusTotalLength, id=wxID_DLGRENDERCBTOTALLENGTH)

        self.timeCtrlTotalLength = wx.lib.masked.timectrl.TimeCtrl(display_seconds=True,
              fmt24hr=True, id=wxID_DLGRENDERTIMECTRLTOTALLENGTH,
              name=u'timeCtrlTotalLength', oob_color=wx.NamedColour('Yellow'),
              parent=self.pnlSettings, pos=wx.Point(-1, -1), size=wx.Size(-1,
              -1), style=0, useFixedWidthFont=True, value='12:00:00 AM')
        self.timeCtrlTotalLength.Enable(False)

        self.rbManual = wx.RadioButton(id=wxID_DLGRENDERRBMANUAL,
              label=_(u'User defined:'), name=u'rbManual',
              parent=self.pnlSettings, pos=wx.Point(-1, -1), size=wx.Size(-1,
              -1), style=0)
        self.rbManual.SetValue(True)
        self.rbManual.Bind(wx.EVT_RADIOBUTTON, self.OnControlStatusTotalLength,
              id=wxID_DLGRENDERRBMANUAL)

        self.rbAudio = wx.RadioButton(id=wxID_DLGRENDERRBAUDIO,
              label=_(u'Audio file:'), name=u'rbAudio', parent=self.pnlSettings,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)
        self.rbAudio.Bind(wx.EVT_RADIOBUTTON, self.OnControlStatusTotalLength,
              id=wxID_DLGRENDERRBAUDIO)

        self.tcAudiofile = wx.TextCtrl(id=wxID_DLGRENDERTCAUDIOFILE,
              name=u'tcAudiofile', parent=self.pnlSettings, pos=wx.Point(-1,
              -1), size=wx.Size(-1, -1), style=wx.TE_READONLY, value=u'')

        self.cmdBrowseAudio = wx.BitmapButton(bitmap=wx.ArtProvider.GetBitmap('wxART_FOLDER_OPEN',
              wx.ART_TOOLBAR, wx.DefaultSize), id=wxID_DLGRENDERCMDBROWSEAUDIO,
              name=u'cmdBrowseAudio', parent=self.pnlSettings, pos=wx.Point(-1,
              -1), size=wx.Size(-1, -1), style=wx.BU_AUTODRAW)
        self.cmdBrowseAudio.Bind(wx.EVT_BUTTON, self.OnCmdBrowseAudioButton,
              id=wxID_DLGRENDERCMDBROWSEAUDIO)

        self.cmdAudioPreview = wx.BitmapButton(bitmap=wx.ArtProvider.GetBitmap('PFS_PLAY_PAUSE',
              wx.ART_TOOLBAR, wx.DefaultSize), id=wxID_DLGRENDERCMDAUDIOPREVIEW,
              name=u'cmdAudioPreview', parent=self.pnlSettings, pos=wx.Point(-1,
              -1), size=wx.Size(-1, -1), style=wx.BU_AUTODRAW)
        self.cmdAudioPreview.Bind(wx.EVT_BUTTON, self.OnCmdAudioPreviewButton,
              id=wxID_DLGRENDERCMDAUDIOPREVIEW)

        self.stOutputHeader = wx.StaticText(id=wxID_DLGRENDERSTOUTPUTHEADER,
              label=_(u'Output'), name=u'stOutputHeader', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.slOutput = wx.StaticLine(id=wxID_DLGRENDERSLOUTPUT,
              name=u'slOutput', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.pnlOutput = wx.Panel(id=wxID_DLGRENDERPNLOUTPUT, name=u'pnlOutput',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.TAB_TRAVERSAL)

        self.stFormat = wx.StaticText(id=wxID_DLGRENDERSTFORMAT,
              label=_(u'Format:'), name=u'stFormat', parent=self.pnlOutput,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.choiceFormat = wx.Choice(choices=[], id=wxID_DLGRENDERCHOICEFORMAT,
              name=u'choiceFormat', parent=self.pnlOutput, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)
        self.choiceFormat.Bind(wx.EVT_CHOICE, self.OnChoiceFormatChoice,
              id=wxID_DLGRENDERCHOICEFORMAT)

        self.lcProps = wx.ListCtrl(id=wxID_DLGRENDERLCPROPS, name=u'lcProps',
              parent=self.pnlOutput, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self._init_coll_lcProps_Columns(self.lcProps)
        self.lcProps.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnActivateProperty,
              id=wxID_DLGRENDERLCPROPS)

        self.stOutputDir = wx.StaticText(id=wxID_DLGRENDERSTOUTPUTDIR,
              label=_(u'Output directory:'), name=u'stOutputDir',
              parent=self.pnlOutput, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=0)

        self.tcOutputDir = wx.TextCtrl(id=wxID_DLGRENDERTCOUTPUTDIR,
              name=u'tcOutputDir', parent=self.pnlOutput, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0, value=u'')

        self.cmdBrowseOutputDir = wx.BitmapButton(bitmap=wx.ArtProvider.GetBitmap('wxART_FOLDER_OPEN',
              wx.ART_TOOLBAR, wx.DefaultSize),
              id=wxID_DLGRENDERCMDBROWSEOUTPUTDIR, name=u'cmdBrowseOutputDir',
              parent=self.pnlOutput, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.BU_AUTODRAW)
        self.cmdBrowseOutputDir.Bind(wx.EVT_BUTTON,
              self.OnCmdBrowseOutputDirButton,
              id=wxID_DLGRENDERCMDBROWSEOUTPUTDIR)

        self.cmdStart = wx.Button(id=wxID_DLGRENDERCMDSTART, label=_(u'&Start'),
              name=u'cmdStart', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)
        self.cmdStart.Bind(wx.EVT_BUTTON, self.OnCmdStartButton,
              id=wxID_DLGRENDERCMDSTART)

        self.cmdClose = wx.Button(id=wxID_DLGRENDERCMDCLOSE, label=_(u'&Close'),
              name=u'cmdClose', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)
        self.cmdClose.Bind(wx.EVT_BUTTON, self.OnCmdCancelButton,
              id=wxID_DLGRENDERCMDCLOSE)

        self.staticLine1 = wx.StaticLine(id=wxID_DLGRENDERSTATICLINE1,
              name='staticLine1', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.gaugeProgress = wx.Gauge(id=wxID_DLGRENDERGAUGEPROGRESS,
              name=u'gaugeProgress', parent=self, pos=wx.Point(-1, -1),
              range=100, size=wx.Size(-1, -1), style=wx.GA_HORIZONTAL)

        self.stProgress = wx.StaticText(id=wxID_DLGRENDERSTPROGRESS, label=u'',
              name=u'stProgress', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self._init_sizers()

    def __init__(self, parent, photoFilmStrip):
        self._init_ctrls(parent)
        self.tcOutputDir.SetMinSize(wx.Size(400, -1))
        self.tcAudiofile.SetMinSize(wx.Size(200, -1))
        self.Bind(wx.EVT_CLOSE, self.OnCmdCancelButton)
        self.spinButtonTransDur.SetMinSize(wx.Size(-1, self.tcTransDuration.GetSizeTuple()[1]))
        
        totalMinSecs = len(photoFilmStrip.GetPictures())
        minTime = wx.DateTime()
        minTime.SetHMS(0, totalMinSecs / 60, totalMinSecs % 60)
        maxTime = wx.DateTime()
        maxTime.SetHMS(1, 59, 59)
        self.timeCtrlTotalLength.SetValue(minTime)
        self.timeCtrlTotalLength.SetMin(minTime)
        self.timeCtrlTotalLength.SetMax(maxTime)
        self.timeCtrlTotalLength.SetLimited(True)

        font = self.stSettingsHeader.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.stSettingsHeader.SetFont(font)
        self.stOutputHeader.SetFont(font)

        self.__photoFilmStrip = photoFilmStrip
        self.__progressHandler = None
        self.__renderEngine = None
        
        self.stTransDur.Enable(False)
        self.tcTransDuration.Enable(False)
        self.stTransDurUnit.Enable(False)
        
        self.cbTotalLength.SetValue(False)
        self.mediaCtrl = wx.media.MediaCtrl(self.pnlSettings, style=wx.SIMPLE_BORDER)
        self.Bind(wx.media.EVT_MEDIA_LOADED, self.OnMediaLoaded)
        self.mediaLoaded = False

        self.__ControlStatusTotalLength()
        
        settings = Settings()
        
        for profile in settings.GetOutputProfiles():
            self.choiceProfile.Append(profile.PName, profile)
        self.choiceProfile.SetSelection(settings.GetLastProfile())
        
        self.choiceType.Append("PAL", OutputProfile.PAL)
        self.choiceType.Append("NTSC", OutputProfile.NTSC)
        self.choiceType.SetSelection(settings.GetVideoType())
        
        msgList = []
        for rend in RENDERERS:
            if rend.CheckDependencies(msgList):
                self.choiceFormat.Append(rend.GetName(), rend)
        print '\n'.join(msgList)
            
        self.choiceFormat.SetSelection(settings.GetUsedRenderer())
        self.OnChoiceFormatChoice(None)
        
        self.tcOutputDir.SetValue(settings.GetLastOutputPath())
        
        self.SetInitialSize(self.GetEffectiveMinSize())
        self.CentreOnParent()

    def __GetChoiceDataSelected(self, choice):
        return choice.GetClientData(choice.GetSelection())

    def __ValidateOutDir(self):
        path = self.tcOutputDir.GetValue()
        if not os.path.isdir(path):
            dlg = wx.MessageDialog(self,
                                   _(u"Output path does not exists! Do you want %s to create it?") % Settings.APP_NAME, 
                                   _(u"Question"),
                                   wx.YES_NO | wx.ICON_QUESTION)
            resp = dlg.ShowModal()
            dlg.Destroy()
            if resp == wx.ID_YES:
                try:
                    os.makedirs(path)
                except StandardError, err:
                    dlg = wx.MessageDialog(self,
                                           _(u"Cannot create direcotory: %s") % str(err),
                                           _(u"Error"),
                                           wx.OK | wx.ICON_ERROR)
                    dlg.ShowModal()
                    dlg.Destroy()
                    return False
            else:
                return False
        else:
            try:
                fd = open(os.path.join(path, 'test'), 'w')
                fd.write(" ")
                fd.close()
                os.remove(os.path.join(path, 'test'))
            except StandardError, err:
                dlg = wx.MessageDialog(self,
                                       _(u"Cannot write into direcotory: %s") % str(err),
                                       _(u"Error"),
                                       wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        if len(os.listdir(path)) > 2:
            dlg = wx.MessageDialog(self,
                                   _(u"Output path is not empty! Use it anyway?"), 
                                   _(u"Question"),
                                   wx.YES_NO | wx.ICON_QUESTION)
            resp = dlg.ShowModal()
            dlg.Destroy()
            if resp != wx.ID_YES:
                return False
        
        return True

    def __ValidateAudioFile(self):
        if self.cbTotalLength.GetValue() and self.rbAudio.GetValue():
            if not os.path.isfile(self.tcAudiofile.GetValue()):
                dlg = wx.MessageDialog(self,
                                       _(u"Audio file does not exist!"), 
                                       _(u"Error"),
                                       wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False
        return True
    
    def OnCmdStartButton(self, event):
        if not self.__ValidateOutDir():
            return
        if not self.__ValidateAudioFile():
            return
        
        profile = self.__GetChoiceDataSelected(self.choiceProfile)
        profile.SetVideoNorm(self.__GetChoiceDataSelected(self.choiceType))
        path = self.tcOutputDir.GetValue()

        rendererClass = self.__GetChoiceDataSelected(self.choiceFormat)

        propDict = {}
        for prop in rendererClass.GetProperties():
            if rendererClass.GetProperty(prop) != rendererClass.GetDefaultProperty(prop):
                propDict[prop] = rendererClass.GetProperty(prop)

        settings = Settings()
        settings.SetLastProfile(self.choiceProfile.GetSelection())
        settings.SetVideoType(self.choiceType.GetSelection())
        settings.SetUsedRenderer(self.choiceFormat.GetSelection())
        settings.SetLastOutputPath(self.tcOutputDir.GetValue())
        settings.SetRenderProperties(rendererClass.__name__, propDict)
        
        self.cmdClose.SetLabel(_(u"&Cancel"))
        self.cmdStart.Enable(False)
        self.pnlSettings.Enable(False)
        self.pnlOutput.Enable(False)
        
        self.__progressHandler = ProgressHandler()
        self.__progressHandler.AddObserver(self)
        
        totalLength = None
        if self.cbTotalLength.GetValue():
            if self.rbManual.GetValue():
                totalLength = 0
                dateTime = self.timeCtrlTotalLength.GetValue(as_wxDateTime=True)
                totalLength += dateTime.GetHour() * 3600
                totalLength += dateTime.GetMinute() * 60
                totalLength += dateTime.GetSecond()
            else:
                totalLength = self.mediaCtrl.Length() / 1000.0
        
        renderer = rendererClass()
        renderer.Init(profile, path)
        if self.cbTotalLength.GetValue() and self.rbAudio.GetValue():
            renderer.SetAudioFile(self.tcAudiofile.GetValue())
        self.__renderEngine = RenderEngine(renderer, self.__progressHandler)
        
        thread.start_new_thread(self.__renderEngine.Start, 
                                (self.__photoFilmStrip.GetPictures(), totalLength))

    def OnCmdCancelButton(self, event):
        if self.__progressHandler:
            dlg = wx.MessageDialog(self,
                                   _(u"Abort current process?"), 
                                   _(u"Question"),
                                   wx.YES_NO | wx.ICON_EXCLAMATION)
            resp = dlg.ShowModal()
            dlg.Destroy()
            if resp == wx.ID_YES:
                self.__progressHandler.Abort()
        else:
            self.Destroy()

    def OnActivateProperty(self, event):
        rendererClass = self.__GetChoiceDataSelected(self.choiceFormat)
        idx = event.GetIndex()
        prop = self.lcProps.GetItemText(idx)
        dlg = wx.TextEntryDialog(self, _(u"Edit property"), prop, unicode(rendererClass.GetProperty(prop)))
        if dlg.ShowModal() == wx.ID_OK:
            try:
                value = eval(dlg.GetValue())
            except NameError:
                value = dlg.GetValue()
            except:
                value = rendererClass.GetDefaultProperty(prop)
            rendererClass.SetProperty(prop, value)
            self.lcProps.SetStringItem(idx, 1, unicode(value))
        dlg.Destroy()
    
    def OnChoiceFormatChoice(self, event):
        data = self.__GetChoiceDataSelected(self.choiceFormat)
        self.lcProps.DeleteAllItems()
        if data is None:
            return
        savedProps = Settings().GetRenderProperties(data.__name__)
        for prop in data.GetProperties():
            value = savedProps.get(prop.lower(), data.GetProperty(prop))
            self.lcProps.Append([prop, value])
            
            data.SetProperty(prop, value)
        
    def ObservableUpdate(self, obj, arg):
        if isinstance(obj, ProgressHandler):
            if arg == 'maxProgress':
                wx.CallAfter(self.gaugeProgress.SetRange, obj.GetMaxProgress())
            elif arg == 'currentProgress':
                wx.CallAfter(self.gaugeProgress.SetValue, obj.GetCurrentProgress())
            elif arg == 'info':
                wx.CallAfter(self.__OnProgressInfo, obj.GetInfo())
            elif arg == 'done':
                wx.CallAfter(self.__OnDone)
            elif arg == 'aborting':
                wx.CallAfter(self.__OnProgressInfo, obj.GetInfo())

    def __OnDone(self):
        if self.__progressHandler.IsAborted():
            self.stProgress.SetLabel(_(u"...aborted!"))
        else:
            self.stProgress.SetLabel(_(u"all done"))

        if self.__renderEngine.GetErrorMessage():
            dlg = wx.MessageDialog(self,
                                   self.__renderEngine.GetErrorMessage(),
                                   _(u"Error"),
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

        self.cmdClose.SetLabel(_(u"&Close"))
        self.cmdStart.Enable(True)
        self.pnlSettings.Enable(True)
        self.pnlOutput.Enable(True)

        self.__progressHandler = None
        self.__renderEngine    = None
        self.Layout()
        
    def __OnProgressInfo(self, info):
        self.stProgress.SetLabel(info)
        self.Layout()

    def OnCmdBrowseOutputDirButton(self, event):
        dlg = wx.DirDialog(self, defaultPath=self.tcOutputDir.GetValue())
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.tcOutputDir.SetValue(path)
        dlg.Destroy()

    def __ControlStatusTotalLength(self):
        active = self.cbTotalLength.GetValue()
        manual = self.rbManual.GetValue()
        self.rbAudio.Enable(active)
        self.rbManual.Enable(active)
        self.timeCtrlTotalLength.Enable(active and manual)
        self.tcAudiofile.Enable(active and not manual)
        self.cmdBrowseAudio.Enable(active and not manual)
        self.cmdAudioPreview.Enable(active and not manual and self.mediaLoaded)
    
    def OnControlStatusTotalLength(self, event):
        self.__ControlStatusTotalLength()
        event.Skip()
        
    def OnCmdBrowseAudioButton(self, event):
        dlg = wx.FileDialog(self, _(u"Select music"), 
                            Settings().GetAudioPath(), "", 
#                            _(u"Audiofiles") + " (*.mp3, *.wav)|*.mp3; *.wav", 
                            _(u"Audiofiles") + " (*.mp3)|*.mp3", 
                            wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            Settings().SetAudioPath(os.path.dirname(path))
            
            if self.mediaCtrl.Load(path):
                self.mediaLoaded = True
                self.tcAudiofile.SetValue(path)
                self.__ControlStatusTotalLength()
            else:
                dlg2 = wx.MessageDialog(self,
                                        _(u"Invalid audio file!"), 
                                        _(u"Error"),
                                        wx.OK | wx.ICON_ERROR)
                dlg2.ShowModal()
                dlg2.Destroy()

        dlg.Destroy()

    def OnCmdAudioPreviewButton(self, event):
        if self.mediaCtrl.GetState() == wx.media.MEDIASTATE_PLAYING:
            self.mediaCtrl.Stop()
        else:
            self.mediaCtrl.Play()

    def OnMediaLoaded(self, event):
        millis = self.mediaCtrl.Length()
        dateTime = wx.DateTime()
        dateTime.SetHMS(0, int(millis / 60000.0), int(millis / 1000.0) % 60)
        try:
            self.timeCtrlTotalLength.SetValue(dateTime)
        except ValueError:
            print "invalid media length"

        event.Skip()
