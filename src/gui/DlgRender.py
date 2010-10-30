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
import stat
import sys
import threading

import wx
import wx.combo


from core.OutputProfile import OutputProfile, GetOutputProfiles
from core.ProgressHandler import ProgressHandler
from core.RenderEngine import RenderEngine
from core.renderer import RENDERERS

from lib.common.ObserverPattern import Observer
from lib.Settings import Settings
from lib.util import Encode

from gui.ctrls.PnlDlgHeader import PnlDlgHeader
from gui.HelpViewer import HelpViewer
from gui.DlgRendererProps import DlgRendererProps
from gui.DlgFinalize import DlgFinalize


[wxID_DLGRENDER, wxID_DLGRENDERCBDRAFT, wxID_DLGRENDERCHOICEFORMAT, 
 wxID_DLGRENDERCHOICEPROFILE, wxID_DLGRENDERCHOICETYPE, 
 wxID_DLGRENDERCMDBATCH, wxID_DLGRENDERCMDCLOSE, wxID_DLGRENDERCMDHELP, 
 wxID_DLGRENDERCMDRENDERERPROPS, wxID_DLGRENDERCMDSTART, 
 wxID_DLGRENDERGAUGEPROGRESS, wxID_DLGRENDERPNLHDR, wxID_DLGRENDERPNLSETTINGS, 
 wxID_DLGRENDERSTATICLINE1, wxID_DLGRENDERSTFORMAT, wxID_DLGRENDERSTPROFILE, 
 wxID_DLGRENDERSTPROGRESS, wxID_DLGRENDERSTTYPE, 
] = [wx.NewId() for _init_ctrls in range(18)]


class DlgRender(wx.Dialog, Observer):
    
    _custom_classes = {"wx.Choice": ["FormatComboBox"],
                       "wx.Panel": ["PnlDlgHeader"]}
    
    def _init_coll_sizerMain_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.pnlHdr, 0, border=0, flag=wx.EXPAND)
        parent.AddWindow(self.pnlSettings, 0, border=4, flag=wx.ALL)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddSizer(self.sizerCmd, 0, border=4, flag=wx.EXPAND | wx.ALL)
        parent.AddWindow(self.staticLine1, 0, border=4,
              flag=wx.BOTTOM | wx.TOP | wx.EXPAND | wx.ALIGN_CENTER_HORIZONTAL)
        parent.AddWindow(self.gaugeProgress, 0, border=4,
              flag=wx.ALL | wx.EXPAND)
        parent.AddWindow(self.stProgress, 0, border=4,
              flag=wx.ALIGN_CENTER_HORIZONTAL | wx.ALL)

    def _init_coll_sizerCmd_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.cmdHelp, 0, border=0, flag=0)
        parent.AddStretchSpacer(1)
        parent.AddWindow(self.cmdClose, 0, border=0, flag=0)
        parent.AddSpacer(wx.Size(32, 8), border=0, flag=0)
        parent.AddWindow(self.cmdBatch, 0, border=0, flag=0)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.cmdStart, 0, border=0, flag=0)

    def _init_coll_sizerSettings_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stProfile, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.choiceProfile, 0, border=0, flag=wx.EXPAND)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.stType, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.choiceType, 0, border=0, flag=wx.EXPAND)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.stFormat, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.choiceFormat, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.cmdRendererProps, 0, border=0, flag=0)
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

        self.pnlHdr = PnlDlgHeader(id=wxID_DLGRENDERPNLHDR, name=u'pnlHdr',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.TAB_TRAVERSAL)

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
        self.choiceProfile.SetMinSize(wx.Size(300, -1))

        self.stType = wx.StaticText(id=wxID_DLGRENDERSTTYPE, label=_(u'Type:'),
              name=u'stType', parent=self.pnlSettings, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.choiceType = wx.Choice(choices=[], id=wxID_DLGRENDERCHOICETYPE,
              name=u'choiceType', parent=self.pnlSettings, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)
        self.choiceType.SetMinSize(wx.Size(300, -1))

        self.stFormat = wx.StaticText(id=wxID_DLGRENDERSTFORMAT,
              label=_(u'Format:'), name=u'stFormat', parent=self.pnlSettings,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.choiceFormat = FormatComboBox(choices=[],
              id=wxID_DLGRENDERCHOICEFORMAT, name=u'choiceFormat',
              parent=self.pnlSettings, pos=wx.Point(-1, -1), size=wx.Size(-1,
              -1), style=wx.CB_READONLY)
        self.choiceFormat.SetMinSize(wx.Size(300, -1))

        self.cmdRendererProps = wx.BitmapButton(bitmap=wx.ArtProvider.GetBitmap('wxART_EXECUTABLE_FILE',
              wx.ART_TOOLBAR, wx.DefaultSize),
              id=wxID_DLGRENDERCMDRENDERERPROPS, name=u'cmdRendererProps',
              parent=self.pnlSettings, pos=wx.Point(-1, -1), size=wx.Size(-1,
              -1), style=wx.BU_AUTODRAW)
        self.cmdRendererProps.SetToolTipString(_("Properties"))
        self.cmdRendererProps.Bind(wx.EVT_BUTTON, self.OnCmdRendererPropsButton,
              id=wxID_DLGRENDERCMDRENDERERPROPS)

        self.cbDraft = wx.CheckBox(id=wxID_DLGRENDERCBDRAFT, label=_(u'Draft'),
              name=u'cbDraft', parent=self.pnlSettings, pos=wx.Point(-1, -1),
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
        
        self.pnlHdr.SetTitle(_('Configure output and start render process'))
        self.pnlHdr.SetBitmap(wx.ArtProvider.GetBitmap(wx.ART_TICK_MARK,
              wx.ART_TOOLBAR, (32, 32)))
        
        self.cbDraft.SetToolTipString(_(u"Activate this option to generate a preview of your PhotoFilmStrip. The rendering process will speed up dramatically, but results in lower quality."))

        self.__photoFilmStrip = photoFilmStrip
        self.__progressHandler = None
        self.__renderEngine = None
        
        for profile in GetOutputProfiles(photoFilmStrip.GetAspect()):
            self.choiceProfile.Append(profile.GetName(), profile)
        
        self.choiceType.Append("PAL", OutputProfile.PAL)
        self.choiceType.Append("NTSC", OutputProfile.NTSC)

        audioFile = self.__photoFilmStrip.GetAudioFile()
        if audioFile and not os.path.exists(audioFile):
            self.pnlHdr.SetErrorMessage(_(u"Audio file '%s' does not exist!") % audioFile)

        settings = Settings()
        self.choiceProfile.SetSelection(settings.GetLastProfile())
        self.choiceType.SetSelection(settings.GetVideoType())
        self.choiceFormat.SetSelection(settings.GetUsedRenderer())
        
        self.SetEscapeId(wxID_DLGRENDERCMDCLOSE)
        self.SetInitialSize(self.GetEffectiveMinSize())
        self.CentreOnParent()
        self.SetFocus()
        
    def __GetChoiceDataSelected(self, choice):
        return choice.GetClientData(choice.GetSelection())
    
    def __GetOutputPath(self):
        profile = self.__GetChoiceDataSelected(self.choiceProfile)
        outpath = os.path.dirname(self.__photoFilmStrip.GetFilename())
        outpath = os.path.join(outpath, profile.GetName())
        return outpath

    def OnCmdStartButton(self, event):
        audioFile = self.__photoFilmStrip.GetAudioFile()
        if audioFile and not os.path.exists(audioFile):
            dlg = wx.MessageDialog(self,
                                   _(u"Audio file '%s' does not exist! Continue anyway?") % audioFile, 
                                   _(u"Warning"),
                                   wx.YES_NO | wx.ICON_WARNING)
            modalResult = dlg.ShowModal()
            dlg.Destroy()
            
            if modalResult == wx.ID_NO:
                return
            audioFile = None
            
        profile = self.__GetChoiceDataSelected(self.choiceProfile)
        profile.SetVideoNorm(self.__GetChoiceDataSelected(self.choiceType))

        outpath = self.__GetOutputPath()
        if not os.path.exists(outpath):
            os.makedirs(outpath)
        
        rendererClass = self.__GetChoiceDataSelected(self.choiceFormat).PRendererClass

        settings = Settings()
        settings.SetLastProfile(self.choiceProfile.GetSelection())
        settings.SetVideoType(self.choiceType.GetSelection())
        settings.SetUsedRenderer(self.choiceFormat.GetSelection())
        
        self.cmdClose.SetLabel(_(u"&Cancel"))
        self.cmdStart.Enable(False)
        self.cmdBatch.Enable(False)
        self.pnlSettings.Enable(False)
        
        self.__progressHandler = ProgressHandler()
        self.__progressHandler.AddObserver(self)
        
        totalLength = self.__photoFilmStrip.GetDuration(False)
        
        renderer = rendererClass()
        renderer.Init(profile, 
                      self.__photoFilmStrip.GetAspect(),
                      Encode(outpath, sys.getfilesystemencoding()),
                      self.cbDraft.GetValue())
        
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

    def OnCmdRendererPropsButton(self, event):
        data = self.__GetChoiceDataSelected(self.choiceFormat)
        if data is None:
            return
        rendererClass = data.PRendererClass
        
        dlg = DlgRendererProps(self, rendererClass)
        dlg.ShowModal()
        dlg.Destroy()
        
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
        isAborted = self.__progressHandler.IsAborted()
        if isAborted:
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
        self.cmdBatch.Enable(True)
        self.pnlSettings.Enable(True)

        self.__progressHandler = None
        self.__renderEngine    = None
        self.Layout()
        
        dlg = DlgFinalize(self, 
                          self.__GetOutputPath(),
                          isAborted, 
                          errMsg=errMsg)
        dlg.ShowModal()
        dlg.Destroy()
        
        if not isAborted and errMsg is None:
            self.Destroy()
        
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
        outpath = os.path.join(outpath, profile.GetName())
        
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
