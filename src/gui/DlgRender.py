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
import stat
import sys
import threading

import wx
import wx.lib.masked.textctrl
import wx.combo
import wx.lib.masked.timectrl


from core.OutputProfile import OutputProfile
from core.ProgressHandler import ProgressHandler
from core.RenderEngine import RenderEngine
from core.renderer import RENDERERS

from lib.common.ObserverPattern import Observer
from lib.Settings import Settings
from lib.util import Encode

from gui.HelpViewer import HelpViewer


[wxID_DLGRENDER, wxID_DLGRENDERCBDRAFT, wxID_DLGRENDERCHOICEFORMAT, 
 wxID_DLGRENDERCHOICEMODE, wxID_DLGRENDERCHOICEPROFILE, 
 wxID_DLGRENDERCHOICETYPE, wxID_DLGRENDERCMDBATCH, wxID_DLGRENDERCMDCLOSE, 
 wxID_DLGRENDERCMDHELP, wxID_DLGRENDERCMDSTART, wxID_DLGRENDERGAUGEPROGRESS, 
 wxID_DLGRENDERLCPROPS, wxID_DLGRENDERPNLOUTPUT, wxID_DLGRENDERPNLSETTINGS, 
 wxID_DLGRENDERPNLSTANDARD, wxID_DLGRENDERSLOUTPUT, wxID_DLGRENDERSLSETTINGS, 
 wxID_DLGRENDERSTATICLINE1, wxID_DLGRENDERSTFORMAT, wxID_DLGRENDERSTMODE, 
 wxID_DLGRENDERSTOUTPUTHEADER, wxID_DLGRENDERSTPROFILE, 
 wxID_DLGRENDERSTPROGRESS, wxID_DLGRENDERSTSETTINGSHEADER, 
 wxID_DLGRENDERSTTYPE, 
] = [wx.NewId() for _init_ctrls in range(25)]


class DlgRender(wx.Dialog, Observer):
    
    _custom_classes = {"wx.Choice": ["FormatComboBox"]}
    
    def _init_coll_szDraft_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.cbDraft, 0, border=0, flag=0)

    def _init_coll_sizerSettingsCtrls_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stProfile, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.choiceProfile, 0, border=0, flag=wx.EXPAND)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.stType, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.choiceType, 0, border=0, flag=wx.EXPAND)

    def _init_coll_sizerOutput_Items(self, parent):
        # generated method, don't edit

        parent.AddSpacer(wx.Size(16, 8), border=0, flag=0)
        parent.AddWindow(self.pnlOutput, 1, border=0, flag=0)

    def _init_coll_sizerMain_Items(self, parent):
        # generated method, don't edit

        parent.AddSizer(self.sizerSettingsHeader, 0, border=0, flag=wx.EXPAND)
        parent.AddSizer(self.sizerSettings, 0, border=4,
              flag=wx.EXPAND | wx.RIGHT)
        parent.AddSpacer(wx.Size(8, 16), border=0, flag=0)
        parent.AddSizer(self.sizerOutputHeader, 0, border=0, flag=wx.EXPAND)
        parent.AddSizer(self.sizerOutput, 0, border=4,
              flag=wx.EXPAND | wx.RIGHT)
        parent.AddSpacer(wx.Size(8, 16), border=0, flag=0)
        parent.AddSizer(self.sizerCmd, 0, border=4, flag=wx.EXPAND | wx.ALL)
        parent.AddWindow(self.staticLine1, 0, border=4,
              flag=wx.BOTTOM | wx.TOP | wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL)
        parent.AddWindow(self.gaugeProgress, 0, border=4,
              flag=wx.ALL | wx.EXPAND)
        parent.AddWindow(self.stProgress, 0, border=4,
              flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL)

    def _init_coll_sizerSettingsCtrls_Growables(self, parent):
        # generated method, don't edit

        parent.AddGrowableCol(2)

    def _init_coll_sizerOutputHeader_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stOutputHeader, 0, border=4, flag=wx.ALL)
        parent.AddWindow(self.slOutput, 1, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)

    def _init_coll_sizerCmd_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.cmdHelp, 0, border=0, flag=0)
        parent.AddStretchSpacer(1)
        parent.AddWindow(self.cmdClose, 0, border=0, flag=0)
        parent.AddSpacer(wx.Size(32, 8), border=0, flag=0)
        parent.AddWindow(self.cmdBatch, 0, border=0, flag=0)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.cmdStart, 0, border=0, flag=0)

    def _init_coll_sizerOutputCtrls_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stFormat, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.choiceFormat, 0, border=0, flag=wx.EXPAND)
        parent.AddWindow(self.stMode, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.choiceMode, 0, border=0, flag=wx.EXPAND)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)

    def _init_coll_sizerOutputCtrls_Growables(self, parent):
        # generated method, don't edit

        parent.AddGrowableCol(1)

    def _init_coll_sizerSettings_Items(self, parent):
        # generated method, don't edit

        parent.AddSpacer(wx.Size(16, 8), border=0, flag=0)
        parent.AddWindow(self.pnlSettings, 1, border=0, flag=0)

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

        self.sizerSettingsHeader = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.sizerSettings = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.sizerOutputHeader = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.sizerOutput = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.sizerOutputCtrls = wx.FlexGridSizer(cols=2, hgap=8, rows=2, vgap=8)
        self.sizerOutputCtrls.SetFlexibleDirection(wx.BOTH)

        self.szDraft = wx.BoxSizer(orient=wx.HORIZONTAL)

        self._init_coll_sizerMain_Items(self.sizerMain)
        self._init_coll_sizerCmd_Items(self.sizerCmd)
        self._init_coll_sizerSettingsCtrls_Items(self.sizerSettingsCtrls)
        self._init_coll_sizerSettingsCtrls_Growables(self.sizerSettingsCtrls)
        self._init_coll_sizerSettingsHeader_Items(self.sizerSettingsHeader)
        self._init_coll_sizerSettings_Items(self.sizerSettings)
        self._init_coll_sizerOutputHeader_Items(self.sizerOutputHeader)
        self._init_coll_sizerOutput_Items(self.sizerOutput)
        self._init_coll_sizerOutputCtrls_Items(self.sizerOutputCtrls)
        self._init_coll_sizerOutputCtrls_Growables(self.sizerOutputCtrls)
        self._init_coll_szDraft_Items(self.szDraft)

        self.SetSizer(self.sizerMain)
        self.pnlSettings.SetSizer(self.sizerSettingsCtrls)
        self.pnlStandard.SetSizer(self.szDraft)
        self.pnlOutput.SetSizer(self.sizerOutputCtrls)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_DLGRENDER, name=u'DlgRender',
              parent=prnt, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER, title=_(u'Render filmstrip'))
        self.SetClientSize(wx.Size(804, 580))

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

        self.stType = wx.StaticText(id=wxID_DLGRENDERSTTYPE, label=_(u'Type:'),
              name=u'stType', parent=self.pnlSettings, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.choiceType = wx.Choice(choices=[], id=wxID_DLGRENDERCHOICETYPE,
              name=u'choiceType', parent=self.pnlSettings, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

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

        self.choiceFormat = FormatComboBox(choices=[],
              id=wxID_DLGRENDERCHOICEFORMAT, name=u'choiceFormat',
              parent=self.pnlOutput, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.CB_READONLY)
        self.choiceFormat.Bind(wx.EVT_COMBOBOX, self.OnChoiceFormatChoice,
              id=wxID_DLGRENDERCHOICEFORMAT)

        self.stMode = wx.StaticText(id=wxID_DLGRENDERSTMODE, label=u'Mode:',
              name=u'stMode', parent=self.pnlOutput, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.choiceMode = wx.Choice(choices=[], id=wxID_DLGRENDERCHOICEMODE,
              name=u'choiceMode', parent=self.pnlOutput, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)
        self.choiceMode.Bind(wx.EVT_CHOICE, self.OnChoiceModeChoice,
              id=wxID_DLGRENDERCHOICEMODE)

        self.lcProps = wx.ListCtrl(id=wxID_DLGRENDERLCPROPS, name=u'lcProps',
              parent=self.pnlOutput, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.LC_REPORT | wx.SUNKEN_BORDER)
        self._init_coll_lcProps_Columns(self.lcProps)
        self.lcProps.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnActivateProperty,
              id=wxID_DLGRENDERLCPROPS)

        self.pnlStandard = wx.Panel(id=wxID_DLGRENDERPNLSTANDARD,
              name=u'pnlStandard', parent=self.pnlOutput, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.TAB_TRAVERSAL)

        self.cbDraft = wx.CheckBox(id=wxID_DLGRENDERCBDRAFT, label=u'Draft',
              name=u'cbDraft', parent=self.pnlStandard, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)
        self.cbDraft.SetValue(False)

        self.cmdHelp = wx.Button(id=wx.ID_HELP, label=_(u'&Help'),
              name=u'cmdHelp', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)
        self.cmdHelp.Bind(wx.EVT_BUTTON, self.OnCmdHelpButton, id=wx.ID_HELP)

        self.cmdClose = wx.Button(id=wxID_DLGRENDERCMDCLOSE, label=_(u'&Close'),
              name=u'cmdClose', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)
        self.cmdClose.Bind(wx.EVT_BUTTON, self.OnCmdCancelButton,
              id=wxID_DLGRENDERCMDCLOSE)

        self.cmdBatch = wx.Button(id=wxID_DLGRENDERCMDBATCH,
              label=_(u'&Batch Job'), name=u'cmdBatch', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)
        self.cmdBatch.Bind(wx.EVT_BUTTON, self.OnCmdBatchButton,
              id=wxID_DLGRENDERCMDBATCH)

        self.cmdStart = wx.Button(id=wxID_DLGRENDERCMDSTART, label=_(u'&Start'),
              name=u'cmdStart', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)
        self.cmdStart.Bind(wx.EVT_BUTTON, self.OnCmdStartButton,
              id=wxID_DLGRENDERCMDSTART)

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
        self.Bind(wx.EVT_CLOSE, self.OnCmdCancelButton)
        
        font = self.stSettingsHeader.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.stSettingsHeader.SetFont(font)
        self.stOutputHeader.SetFont(font)
        
        self.lcProps.SetSizeHints(-1, 120, -1, -1)
        
        self.cbDraft.SetToolTipString(_(u"Activate this option to generate a preview of your PhotoFilmStrip. The rendering process will speed up dramatically, but results in lower quality."))

        self.__photoFilmStrip = photoFilmStrip
        self.__progressHandler = None
        self.__renderEngine = None
        
        settings = Settings()
        
        for profile in settings.GetOutputProfiles():
            self.choiceProfile.Append(profile.PName, profile)
        self.choiceProfile.SetSelection(settings.GetLastProfile())
        
        self.choiceType.Append("PAL", OutputProfile.PAL)
        self.choiceType.Append("NTSC", OutputProfile.NTSC)
        self.choiceType.SetSelection(settings.GetVideoType())
        
        self.choiceFormat.SetSelection(settings.GetUsedRenderer())
        self.OnChoiceFormatChoice(None)
        
        self.choiceMode.Append(_(u"Standard"), self.pnlStandard)
        self.choiceMode.Append(_(u"Advanced"), self.lcProps)
        self.choiceMode.Select(0)
        self.__OnMode(0)

        self.CentreOnParent()
        
    def __GetChoiceDataSelected(self, choice):
        return choice.GetClientData(choice.GetSelection())

    def OnCmdStartButton(self, event):
        profile = self.__GetChoiceDataSelected(self.choiceProfile)
        profile.SetVideoNorm(self.__GetChoiceDataSelected(self.choiceType))

        outpath = os.path.dirname(self.__photoFilmStrip.GetFilename())
        outpath = os.path.join(outpath, profile.PName)
        if not os.path.exists(outpath):
            os.makedirs(outpath)
        
        rendererClass = self.__GetChoiceDataSelected(self.choiceFormat).PRendererClass

        propDict = {}
        for prop in rendererClass.GetProperties():
            if rendererClass.GetProperty(prop) != rendererClass.GetDefaultProperty(prop):
                propDict[prop] = rendererClass.GetProperty(prop)

        settings = Settings()
        settings.SetLastProfile(self.choiceProfile.GetSelection())
        settings.SetVideoType(self.choiceType.GetSelection())
        settings.SetUsedRenderer(self.choiceFormat.GetSelection())
#        settings.SetLastOutputPath(self.tcOutputDir.GetValue())
        settings.SetRenderProperties(rendererClass.__name__, propDict)
        
        self.cmdClose.SetLabel(_(u"&Cancel"))
        self.cmdStart.Enable(False)
        self.pnlSettings.Enable(False)
        self.pnlOutput.Enable(False)
        
        self.__progressHandler = ProgressHandler()
        self.__progressHandler.AddObserver(self)
        
        totalLength = self.__photoFilmStrip.GetDuration()
        
        renderer = rendererClass()
        renderer.Init(profile, Encode(outpath, sys.getfilesystemencoding()))
        
        audioFile = self.__photoFilmStrip.GetAudioFile()
        if audioFile:
            renderer.SetAudioFile(Encode(audioFile, sys.getfilesystemencoding()))

        self.__renderEngine = RenderEngine(renderer, self.__progressHandler)
        
        renderThread = threading.Thread(target=self.__renderEngine.Start,
                                        args=(self.__photoFilmStrip.GetPictures(), totalLength),
                                        name="RenderThread")
        renderThread.start()

    def OnCmdCancelButton(self, event):
        if self.__progressHandler:
            dlg = wx.MessageDialog(self,
                                   _(u"Abort current process?"), 
                                   _(u"Question"),
                                   wx.YES_NO | wx.ICON_EXCLAMATION)
            resp = dlg.ShowModal()
            dlg.Destroy()
            if resp == wx.ID_YES:
                if self.__progressHandler:
                    # maybe processing is done while showing this question
                    self.__progressHandler.Abort()
        else:
            self.Destroy()

    def OnActivateProperty(self, event):
        rendererClass = self.__GetChoiceDataSelected(self.choiceFormat).PRendererClass
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
        rendererClass = data.PRendererClass
        self.lcProps.DeleteAllItems()
        if data is None:
            return
        savedProps = Settings().GetRenderProperties(rendererClass.__name__)
        for prop in rendererClass.GetProperties():
            value = savedProps.get(prop.lower(), rendererClass.GetProperty(prop))
            self.lcProps.Append([prop, value])
            
            rendererClass.SetProperty(prop, value)
            
        self.cmdStart.Enable(data.IsOk())
        
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

        errMsg = self.__renderEngine.GetErrorMessage() 
        if errMsg:
            dlg = wx.MessageDialog(self,
                                   errMsg,
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
        
        if errMsg:
            raise RuntimeError(errMsg)
        
    def __OnProgressInfo(self, info):
        self.stProgress.SetLabel(info)
        self.Layout()

    def OnCmdHelpButton(self, event):
        HelpViewer().DisplayID(HelpViewer.ID_RENDER)
        event.Skip()

    def OnCmdBatchButton(self, event):
        if self.__photoFilmStrip.GetFilename() is None:
            dlg = wx.MessageDialog(self,
                                   _(u"Project not saved yet. Please save the project first to create a batch job!"), 
                                   _(u"Error"),
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            return

        profile = self.__GetChoiceDataSelected(self.choiceProfile)
        outpath = os.path.dirname(self.__photoFilmStrip.GetFilename())
        outpath = os.path.join(outpath, profile.PName)
        
        if sys.platform == 'win32':
            batchFileMask = _(u"Batch file") + " (*.bat)|*.bat"
            coding = sys.getfilesystemencoding()
            header = "@echo off\n" \
                     "chcp 1252\n\n" \
                     "SET PFS_CLI=%s-cli" % Encode(os.path.splitext(sys.argv[0])[0], coding)
            pfsCliCmd = "%PFS_CLI%"
        else:
            batchFileMask = _(u"Shell script") + " (*.sh)|*.sh"
            coding = "utf-8"
            header = "#!/bin/sh\n\n" \
                     "export PFS_CLI=/usr/bin/photofilmstrip-cli"
            pfsCliCmd = "$PFS_CLI"

        dlg = wx.FileDialog(self, _(u"Select batch file"), 
                            "" , "", 
                            batchFileMask, 
                            wx.SAVE)
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            
            if os.path.isfile(path):
                fd = open(path, 'a')
            else:
                fd = open(path, 'w')
                fd.write(header)
                fd.write("\n\n")

            cli = []
            cli.append(pfsCliCmd)
            cli.append("-p")
            cli.append("\"" + Encode(self.__photoFilmStrip.GetFilename(), coding) + "\"")
            cli.append("-o")
            cli.append("\"" + Encode(outpath, coding) + "\"")
            cli.append("-t")
            cli.append(str(self.choiceProfile.GetSelection()))
            cli.append("-n")
            cli.append("p" if self.__GetChoiceDataSelected(self.choiceType) == OutputProfile.PAL else "n")
            cli.append("-f")
            cli.append(str(self.choiceFormat.GetSelection()))
            
            cli.append("-l")
            cli.append(str(self.__photoFilmStrip.GetDuration()))
                
            if self.__photoFilmStrip.GetAudioFile() is not None:
                cli.append("-a")
                cli.append("\"" + Encode(self.__photoFilmStrip.GetAudioFile(), coding) + "\"")
                    
            fd.write(" ".join(cli))
            fd.write("\n")
            
            fd.close()
            
            try:
                os.chmod(path, stat.S_IREAD | stat.S_IEXEC | stat.S_IWUSR | stat.S_IRGRP | stat.S_IROTH)
            except OSError:
                pass

        dlg.Destroy()

    def __OnMode(self, mode):
        self.SetSizeHints(-1, -1, -1, -1)

        self.sizerOutputCtrls.Remove(5)
        if mode == 0:
            ctrl = self.pnlStandard
        else:
            ctrl = self.lcProps  
        self.sizerOutputCtrls.AddWindow(ctrl, 0, border=0, flag=wx.EXPAND)

        self.pnlStandard.Show(mode == 0)
        self.lcProps.Show(mode == 1)
        self.Layout()
        
        szMin = self.GetEffectiveMinSize()
        self.SetSizeHints(500, szMin.GetHeight(), 500, szMin.GetHeight())
    
    def OnChoiceModeChoice(self, event):
        self.__OnMode(event.GetSelection())
        event.Skip()


class FormatComboBox(wx.combo.OwnerDrawnComboBox):
    
    def __init__(self, *args, **kwargs):
        wx.combo.OwnerDrawnComboBox.__init__(self, *args, **kwargs)

        for rend in RENDERERS:
            msgList = []
            rend.CheckDependencies(msgList)

            self.Append(rend.GetName(), FormatData(rend, msgList))
    
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
    
    def __init__(self, rendClass, msgList):
        self.PRendererClass = rendClass
        self.PMessages = msgList

    def IsOk(self):
        return len(self.PMessages) == 0
