#Boa:Dialog:DlgProjectProps
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
import wx.media
import wx.lib.masked.timectrl
import wx.lib.masked.textctrl

from lib.Settings import Settings

from core.PhotoFilmStrip import PhotoFilmStrip


[wxID_DLGPROJECTPROPS, wxID_DLGPROJECTPROPSBMPLOGO, 
 wxID_DLGPROJECTPROPSCBTOTALLENGTH, wxID_DLGPROJECTPROPSCHOICEASPECT, 
 wxID_DLGPROJECTPROPSCMDAUDIOPREVIEW, wxID_DLGPROJECTPROPSCMDBROWSEAUDIO, 
 wxID_DLGPROJECTPROPSCMDBROWSEFOLDER, wxID_DLGPROJECTPROPSCMDCANCEL, 
 wxID_DLGPROJECTPROPSCMDOK, wxID_DLGPROJECTPROPSPNLHEADER, 
 wxID_DLGPROJECTPROPSRBAUDIO, wxID_DLGPROJECTPROPSRBMANUAL, 
 wxID_DLGPROJECTPROPSSTASPECT, wxID_DLGPROJECTPROPSSTATICLINE, 
 wxID_DLGPROJECTPROPSSTATICLINE1, wxID_DLGPROJECTPROPSSTATICLINE2, 
 wxID_DLGPROJECTPROPSSTFOLDER, wxID_DLGPROJECTPROPSSTHEADER, 
 wxID_DLGPROJECTPROPSSTPROJECT, wxID_DLGPROJECTPROPSTCAUDIOFILE, 
 wxID_DLGPROJECTPROPSTCFOLDER, wxID_DLGPROJECTPROPSTCPROJECT, 
 wxID_DLGPROJECTPROPSTIMECTRLTOTALLENGTH, 
] = [wx.NewId() for _init_ctrls in range(23)]


class DlgProjectProps(wx.Dialog):
    def _init_coll_szMain_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.pnlHeader, 0, border=0, flag=wx.EXPAND)
        parent.AddWindow(self.staticLine2, 0, border=0, flag=wx.EXPAND)
        parent.AddSizer(self.szCtrls, 0, border=8, flag=wx.ALL | wx.EXPAND)
        parent.AddWindow(self.staticLine1, 0, border=0, flag=wx.EXPAND)
        parent.AddSizer(self.szCmds, 0, border=8, flag=wx.ALL | wx.ALIGN_RIGHT)

    def _init_coll_szCmds_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.cmdCancel, 0, border=0, flag=0)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.cmdOk, 0, border=0, flag=0)

    def _init_coll_szCtrls_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stProject, (0, 0), border=0,
              flag=wx.ALIGN_CENTER_VERTICAL, span=(1, 1))
        parent.AddWindow(self.tcProject, (0, 1), border=0, flag=wx.EXPAND,
              span=(1, 1))
        parent.AddWindow(self.stFolder, (1, 0), border=0,
              flag=wx.ALIGN_CENTER_VERTICAL, span=(1, 1))
        parent.AddWindow(self.tcFolder, (1, 1), border=0,
              flag=wx.EXPAND | wx.ALIGN_CENTER_VERTICAL, span=(1, 1))
        parent.AddWindow(self.cmdBrowseFolder, (1, 2), border=0, flag=0,
              span=(1, 1))
        parent.AddWindow(self.staticLine, (2, 0), border=0, flag=wx.EXPAND,
              span=(1, 4))
        parent.AddWindow(self.stAspect, (3, 0), border=0,
              flag=wx.ALIGN_CENTER_VERTICAL, span=(1, 1))
        parent.AddWindow(self.choiceAspect, (3, 1), border=0, flag=wx.EXPAND,
              span=(1, 1))
        parent.AddWindow(self.cbTotalLength, (4, 0), border=0, flag=0, span=(1,
              1))
        parent.AddWindow(self.rbManual, (5, 0), border=32,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, span=(1, 1))
        parent.AddWindow(self.timeCtrlTotalLength, (5, 1), border=0,
              flag=wx.EXPAND, span=(1, 1))
        parent.AddWindow(self.rbAudio, (6, 0), border=32,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.LEFT, span=(1, 1))
        parent.AddWindow(self.tcAudiofile, (6, 1), border=0, flag=wx.EXPAND,
              span=(1, 1))
        parent.AddWindow(self.cmdBrowseAudio, (6, 2), border=0, flag=0, span=(1,
              1))
        parent.AddWindow(self.cmdAudioPreview, (6, 3), border=0, flag=0,
              span=(1, 1))

    def _init_coll_szHeader_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stHeader, 0, border=8,
              flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)
        parent.AddStretchSpacer(1)
        parent.AddWindow(self.bmpLogo, 0, border=8,
              flag=wx.ALL | wx.ALIGN_CENTER_VERTICAL)

    def _init_coll_szCtrls_Growables(self, parent):
        # generated method, don't edit

        parent.AddGrowableCol(1)

    def _init_sizers(self):
        # generated method, don't edit
        self.szMain = wx.BoxSizer(orient=wx.VERTICAL)

        self.szHeader = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.szCtrls = wx.GridBagSizer(hgap=8, vgap=8)

        self.szCmds = wx.BoxSizer(orient=wx.HORIZONTAL)

        self._init_coll_szMain_Items(self.szMain)
        self._init_coll_szHeader_Items(self.szHeader)
        self._init_coll_szCtrls_Items(self.szCtrls)
        self._init_coll_szCtrls_Growables(self.szCtrls)
        self._init_coll_szCmds_Items(self.szCmds)

        self.SetSizer(self.szMain)
        self.pnlHeader.SetSizer(self.szHeader)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_DLGPROJECTPROPS,
              name=u'DlgProjectProps', parent=prnt, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.DEFAULT_DIALOG_STYLE,
              title=u'Project properties')
        self.SetClientSize(wx.Size(653, 437))

        self.stProject = wx.StaticText(id=wxID_DLGPROJECTPROPSSTPROJECT,
              label=u'Project name:', name=u'stProject', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.tcProject = wx.TextCtrl(id=wxID_DLGPROJECTPROPSTCPROJECT,
              name=u'tcProject', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0, value=u'')

        self.pnlHeader = wx.Panel(id=wxID_DLGPROJECTPROPSPNLHEADER,
              name=u'pnlHeader', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.TAB_TRAVERSAL)
        self.pnlHeader.SetBackgroundColour(wx.Colour(255, 255, 255))

        self.stHeader = wx.StaticText(id=wxID_DLGPROJECTPROPSSTHEADER,
              label=u'PhotoFilmStrip project', name=u'stHeader',
              parent=self.pnlHeader, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=0)

        self.bmpLogo = wx.StaticBitmap(bitmap=wx.ArtProvider.GetBitmap('PFS_ICON_48',
              wx.ART_TOOLBAR, wx.DefaultSize), id=wxID_DLGPROJECTPROPSBMPLOGO,
              name=u'bmpLogo', parent=self.pnlHeader, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.staticLine2 = wx.StaticLine(id=wxID_DLGPROJECTPROPSSTATICLINE2,
              name='staticLine2', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.stFolder = wx.StaticText(id=wxID_DLGPROJECTPROPSSTFOLDER,
              label=u'Directory:', name=u'stFolder', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.tcFolder = wx.TextCtrl(id=wxID_DLGPROJECTPROPSTCFOLDER,
              name=u'tcFolder', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0, value=u'')

        self.cmdBrowseFolder = wx.BitmapButton(bitmap=wx.ArtProvider.GetBitmap('wxART_FOLDER_OPEN',
              wx.ART_TOOLBAR, wx.DefaultSize),
              id=wxID_DLGPROJECTPROPSCMDBROWSEFOLDER, name=u'cmdBrowseFolder',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.BU_AUTODRAW)
        self.cmdBrowseFolder.Bind(wx.EVT_BUTTON,
              self.OnCmdBrowseFolderButton,
              id=wxID_DLGPROJECTPROPSCMDBROWSEFOLDER)

        self.stAspect = wx.StaticText(id=wxID_DLGPROJECTPROPSSTASPECT,
              label=u'Aspect ratio:', name=u'stAspect', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.choiceAspect = wx.Choice(choices=[],
              id=wxID_DLGPROJECTPROPSCHOICEASPECT, name=u'choiceAspect',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.cbTotalLength = wx.CheckBox(id=wxID_DLGPROJECTPROPSCBTOTALLENGTH,
              label=_(u'Total length:'), name=u'cbTotalLength', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)
        self.cbTotalLength.SetValue(False)
        self.cbTotalLength.SetToolTipString(_(u'Overrides the duration of single pictures and gives the photo filmstrip this total length.'))
        self.cbTotalLength.Bind(wx.EVT_CHECKBOX,
              self.OnControlStatusTotalLength,
              id=wxID_DLGPROJECTPROPSCBTOTALLENGTH)

        self.rbManual = wx.RadioButton(id=wxID_DLGPROJECTPROPSRBMANUAL,
              label=_(u'User defined:'), name=u'rbManual', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)
        self.rbManual.SetValue(True)
        self.rbManual.Bind(wx.EVT_RADIOBUTTON, self.OnControlStatusTotalLength,
              id=wxID_DLGPROJECTPROPSRBMANUAL)

        self.timeCtrlTotalLength = wx.lib.masked.timectrl.TimeCtrl(display_seconds=True,
              fmt24hr=True, id=wxID_DLGPROJECTPROPSTIMECTRLTOTALLENGTH,
              name=u'timeCtrlTotalLength', oob_color=wx.NamedColour('Yellow'),
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0,
              useFixedWidthFont=True, value='12:00:00 AM')
        self.timeCtrlTotalLength.Enable(False)

        self.rbAudio = wx.RadioButton(id=wxID_DLGPROJECTPROPSRBAUDIO,
              label=_(u'Audio file:'), name=u'rbAudio', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)
        self.rbAudio.Bind(wx.EVT_RADIOBUTTON, self.OnControlStatusTotalLength,
              id=wxID_DLGPROJECTPROPSRBAUDIO)

        self.tcAudiofile = wx.TextCtrl(id=wxID_DLGPROJECTPROPSTCAUDIOFILE,
              name=u'tcAudiofile', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.TE_READONLY, value=u'')

        self.cmdBrowseAudio = wx.BitmapButton(bitmap=wx.ArtProvider.GetBitmap('wxART_FOLDER_OPEN',
              wx.ART_TOOLBAR, wx.DefaultSize),
              id=wxID_DLGPROJECTPROPSCMDBROWSEAUDIO, name=u'cmdBrowseAudio',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.BU_AUTODRAW)
        self.cmdBrowseAudio.Bind(wx.EVT_BUTTON, self.OnCmdBrowseAudioButton,
              id=wxID_DLGPROJECTPROPSCMDBROWSEAUDIO)

        self.cmdAudioPreview = wx.BitmapButton(bitmap=wx.ArtProvider.GetBitmap('PFS_PLAY_PAUSE',
              wx.ART_TOOLBAR, wx.DefaultSize),
              id=wxID_DLGPROJECTPROPSCMDAUDIOPREVIEW, name=u'cmdAudioPreview',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.BU_AUTODRAW)
        self.cmdAudioPreview.Bind(wx.EVT_BUTTON, self.OnCmdAudioPreviewButton,
              id=wxID_DLGPROJECTPROPSCMDAUDIOPREVIEW)

        self.staticLine = wx.StaticLine(id=wxID_DLGPROJECTPROPSSTATICLINE,
              name=u'staticLine', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.staticLine1 = wx.StaticLine(id=wxID_DLGPROJECTPROPSSTATICLINE1,
              name='staticLine1', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.cmdCancel = wx.Button(id=wx.ID_CANCEL, label=u'Cancel',
              name=u'cmdCancel', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.cmdOk = wx.Button(id=wx.ID_OK, label=u'Ok', name=u'cmdOk',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self._init_sizers()

    def __init__(self, parent, photoFilmStrip=None):
        self._init_ctrls(parent)

        font = self.stHeader.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.stHeader.SetFont(font)
        
        self.choiceAspect.Append("16:9", 16.0 / 9.0)
        self.choiceAspect.Append("4:3", 4.0 / 3.0)
        self.choiceAspect.Append("3:2", 3.0 / 2.0)
        self.choiceAspect.Select(0)
        
        self.tcFolder.SetMaxSize(wx.Size(-1, self.tcProject.GetSizeTuple()[1]))
        self.tcAudiofile.SetMaxSize(wx.Size(-1, self.tcProject.GetSizeTuple()[1]))
        self.tcAudiofile.SetMinSize(wx.Size(300, -1))
        
        minTime = wx.DateTime_Now()
        minTime.SetHMS(0, 0, 3)
        maxTime = wx.DateTime_Now()
        maxTime.SetHMS(1, 59, 59)
        self.timeCtrlTotalLength.SetValue(minTime)
        self.timeCtrlTotalLength.SetMin(minTime)
        self.timeCtrlTotalLength.SetMax(maxTime)
        self.timeCtrlTotalLength.SetLimited(True)

        self.Layout()

        self.__photoFilmStrip = photoFilmStrip
        
        if photoFilmStrip is None:
            projName = _(u"Unnamed PhotoFilmStrip")
            self.tcProject.SetValue(projName)
            self.tcProject.SelectAll()
            self.tcProject.SetFocus()

            # TODO: Default aus Settings laden
            self.tcFolder.SetValue(os.path.join(wx.GetHomeDir(), u"My PhotoFilmStrips"))
            
            self.cbTotalLength.SetValue(False)
        else:
            projName = os.path.splitext(os.path.basename(photoFilmStrip.GetFilename()))[0]
            self.tcProject.SetValue(projName)
            self.tcProject.Enable(False)
        
            self.tcFolder.SetValue(os.path.dirname(photoFilmStrip.GetFilename()))
            self.tcFolder.Enable(False)
            self.cmdBrowseFolder.Enable(False)
            
            self.__SetChoiceSelectionByData(self.choiceAspect, photoFilmStrip.GetAspect())
            
            pfsDur = photoFilmStrip.GetDuration()
            dur = wx.DateTime_Now()
            dur.SetHMS(0, pfsDur / 60, pfsDur % 60)
            self.timeCtrlTotalLength.SetWxDateTime(dur)

            if photoFilmStrip.GetDuration(calc=False):
                self.cbTotalLength.SetValue(True)
            
            audioFile = photoFilmStrip.GetAudioFile()
            if audioFile:
                self.__LoadAudioFile(audioFile)
                self.tcAudiofile.SetValue(audioFile)
                self.cbTotalLength.SetValue(True)

        try:
            self.mediaCtrl = wx.media.MediaCtrl(self, style=wx.SIMPLE_BORDER)
            self.Bind(wx.media.EVT_MEDIA_LOADED, self.OnMediaLoaded)
        except NotImplementedError:
            self.mediaCtrl = None

        self.mediaLoaded = False

        self.__ControlStatusTotalLength()
        
        self.SetInitialSize(self.GetEffectiveMinSize())
        
    def OnCmdBrowseFolderButton(self, event):
        dlg = wx.DirDialog(self, defaultPath=self.tcFolder.GetValue())
        if dlg.ShowModal() == wx.ID_OK:
            path = dlg.GetPath()
            self.tcFolder.SetValue(path)
        dlg.Destroy()

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
            
            self.__LoadAudioFile(path)
            
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
        except ValueError, err:
            print err, "invalid media length", dateTime

        event.Skip()

    def GetChoiceDataSelected(self, choice):
        return choice.GetClientData(choice.GetSelection())
    
    def __SetChoiceSelectionByData(self, choice, data):
        for idx in range(choice.GetCount()):
            if choice.GetClientData(idx) == data:
                choice.Select(idx)
                return
            
    def __ControlStatusTotalLength(self):
        active = self.cbTotalLength.GetValue()
        manual = self.rbManual.GetValue()
        if not manual and self.mediaCtrl is None:
            dlg = wx.MessageDialog(self,
                                   _(u"No media support found on this platform!"),  
                                   _(u"Error"),
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()
            self.rbManual.SetValue(True)
            return
            
        self.rbAudio.Enable(active)
        self.rbManual.Enable(active)
        self.timeCtrlTotalLength.Enable(active and manual)
        self.tcAudiofile.Enable(active and not manual)
        self.cmdBrowseAudio.Enable(active and not manual)
        self.cmdAudioPreview.Enable(active and not manual and self.mediaLoaded)
    
    def __LoadAudioFile(self, path):
        if self.mediaCtrl.Load(path):
            self.mediaLoaded = True
            self.tcAudiofile.SetValue(path)
            self.__ControlStatusTotalLength()
        else:
            dlg = wx.MessageDialog(self,
                                   _(u"Invalid audio file!"), 
                                   _(u"Error"),
                                   wx.OK | wx.ICON_ERROR)
            dlg.ShowModal()
            dlg.Destroy()

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

    def __GetTotalLength(self):
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
            
        return totalLength
    
    def __ValidateOutDir(self):
        path = self.tcFolder.GetValue()
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
                                           _(u"Cannot create direcotory: %s") % unicode(err),
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
                                       _(u"Cannot write into direcotory: %s") % unicode(err),
                                       _(u"Error"),
                                       wx.OK | wx.ICON_ERROR)
                dlg.ShowModal()
                dlg.Destroy()
                return False

        return True

    def __GetProjectPath(self):
        projName = self.tcProject.GetValue()
        filepath = os.path.join(self.tcFolder.GetValue(), 
                                projName,
                                "%s.pfs" % projName)
        return filepath
    
    def GetPhotoFilmStrip(self):
        if self.__photoFilmStrip is None:
            self.__photoFilmStrip = PhotoFilmStrip(self.__GetProjectPath())
        self.__photoFilmStrip.SetAudioFile(self.tcAudiofile.GetValue())
        self.__photoFilmStrip.SetDuration(self.__GetTotalLength())
        self.__photoFilmStrip.SetAspect(self.GetChoiceDataSelected(self.choiceAspect))
        return self.__photoFilmStrip

    
