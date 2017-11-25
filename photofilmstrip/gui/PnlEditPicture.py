#Boa:FramePanel:PnlEditPicture
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

from photofilmstrip.core.Picture import Picture

from photofilmstrip.gui.ctrls.PnlFloatSpinCtrl import (
        PnlFloatSpinCtrl, 
        EVT_VALUE_CHANGED)


[wxID_PNLEDITPICTURE, wxID_PNLEDITPICTURECHOICEEFFECT, 
 wxID_PNLEDITPICTURECHOICEMOVEMENT, wxID_PNLEDITPICTURECHOICETRANS, 
 wxID_PNLEDITPICTURECMDROTATELEFT, wxID_PNLEDITPICTURECMDROTATERIGHT, 
 wxID_PNLEDITPICTUREPNLIMGDURATION, wxID_PNLEDITPICTUREPNLTRANSDURATION, 
 wxID_PNLEDITPICTURESTATICLINE1, wxID_PNLEDITPICTURESTATICLINE2, 
 wxID_PNLEDITPICTURESTDURATIONUNIT, wxID_PNLEDITPICTURESTEFFECT, 
 wxID_PNLEDITPICTURESTMOVEMENT, wxID_PNLEDITPICTURESTPROCESS, 
 wxID_PNLEDITPICTURESTROTATION, wxID_PNLEDITPICTURESTSETTINGS, 
 wxID_PNLEDITPICTURESTSUBTITLE, wxID_PNLEDITPICTURESTTRANS, 
 wxID_PNLEDITPICTURESTTRANSUNIT, wxID_PNLEDITPICTURETCCOMMENT, 
] = [wx.NewId() for _init_ctrls in range(20)]


class PnlEditPicture(wx.Panel):
    
    _custom_classes = {"wx.Panel": ["PnlFloatSpinCtrl"]}
    
    def _init_coll_sizerMain_Items(self, parent):
        # generated method, don't edit

        parent.AddSizer(self.szSettings, 0, border=4, flag=wx.ALL)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.staticLine1, 0, border=4, flag=wx.ALL | wx.EXPAND)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddSizer(self.szTimes, 0, border=4, flag=wx.ALL)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.staticLine2, 0, border=4, flag=wx.EXPAND | wx.ALL)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddSizer(self.szSubtitle, 1, border=4, flag=wx.ALL | wx.EXPAND)

    def _init_coll_szTimes_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stProcess, 0, border=0, flag=0)
        parent.AddSizer(self.sizerTimesCtrls, 0, border=16, flag=wx.LEFT)

    def _init_coll_szSubtitle_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stSubtitle, 0, border=0, flag=0)
        parent.AddWindow(self.tcComment, 1, border=16, flag=wx.LEFT | wx.EXPAND)

    def _init_coll_sizerTimesCtrls_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stMovement, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.choiceMovement, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.pnlImgDuration, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.stDurationUnit, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.stTrans, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.choiceTrans, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.pnlTransDuration, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.stTransUnit, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)

    def _init_coll_szSettings_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stSettings, 0, border=0, flag=0)
        parent.AddSizer(self.szSettingsCtrls, 0, border=16, flag=wx.LEFT)

    def _init_coll_szSettingsCtrls_Growables(self, parent):
        # generated method, don't edit

        parent.AddGrowableCol(1)

    def _init_coll_szSettingsCtrls_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stRotation, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddSizer(self.sizerRotationTools, 0, border=0, flag=wx.EXPAND)
        parent.AddWindow(self.stEffect, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.choiceEffect, 0, border=0, flag=wx.EXPAND)

    def _init_coll_sizerRotationTools_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.cmdRotateLeft, 0, border=0, flag=0)
        parent.AddStretchSpacer(1)
        parent.AddWindow(self.cmdRotateRight, 0, border=0, flag=0)

    def _init_sizers(self):
        # generated method, don't edit
        self.sizerMain = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.szSettingsCtrls = wx.FlexGridSizer(cols=2, hgap=8, rows=2, vgap=8)

        self.szSubtitle = wx.BoxSizer(orient=wx.VERTICAL)

        self.sizerRotationTools = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.sizerTimesCtrls = wx.FlexGridSizer(cols=4, hgap=8, rows=1, vgap=8)

        self.szTimes = wx.BoxSizer(orient=wx.VERTICAL)

        self.szSettings = wx.BoxSizer(orient=wx.VERTICAL)

        self._init_coll_sizerMain_Items(self.sizerMain)
        self._init_coll_szSettingsCtrls_Items(self.szSettingsCtrls)
        self._init_coll_szSettingsCtrls_Growables(self.szSettingsCtrls)
        self._init_coll_szSubtitle_Items(self.szSubtitle)
        self._init_coll_sizerRotationTools_Items(self.sizerRotationTools)
        self._init_coll_sizerTimesCtrls_Items(self.sizerTimesCtrls)
        self._init_coll_szTimes_Items(self.szTimes)
        self._init_coll_szSettings_Items(self.szSettings)

        self.SetSizer(self.sizerMain)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Panel.__init__(self, id=wxID_PNLEDITPICTURE, name=u'PnlEditPicture',
              parent=prnt, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.TAB_TRAVERSAL)
        self.SetClientSize(wx.Size(827, 137))

        self.stSettings = wx.StaticText(id=wxID_PNLEDITPICTURESTSETTINGS,
              label=_(u'Settings'), name=u'stSettings', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.stRotation = wx.StaticText(id=wxID_PNLEDITPICTURESTROTATION,
              label=_(u'Rotation:'), name=u'stRotation', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.cmdRotateLeft = wx.BitmapButton(bitmap=wx.ArtProvider.GetBitmap('PFS_IMAGE_ROTATION_LEFT_16'),
              id=wxID_PNLEDITPICTURECMDROTATELEFT, name=u'cmdRotateLeft',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.BU_AUTODRAW)
        self.cmdRotateLeft.SetBitmapDisabled(wx.ArtProvider.GetBitmap('PFS_IMAGE_ROTATION_LEFT_D_16'))
        self.cmdRotateLeft.Bind(wx.EVT_BUTTON, self.OnCmdRotateLeftButton,
              id=wxID_PNLEDITPICTURECMDROTATELEFT)

        self.cmdRotateRight = wx.BitmapButton(bitmap=wx.ArtProvider.GetBitmap('PFS_IMAGE_ROTATION_RIGHT_16'),
              id=wxID_PNLEDITPICTURECMDROTATERIGHT, name=u'cmdRotateRight',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.BU_AUTODRAW)
        self.cmdRotateRight.SetBitmapDisabled(wx.ArtProvider.GetBitmap('PFS_IMAGE_ROTATION_RIGHT_D_16'))
        self.cmdRotateRight.Bind(wx.EVT_BUTTON, self.OnCmdRotateRightButton,
              id=wxID_PNLEDITPICTURECMDROTATERIGHT)

        self.stEffect = wx.StaticText(id=wxID_PNLEDITPICTURESTEFFECT,
              label=_(u'Effect:'), name=u'stEffect', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.choiceEffect = wx.Choice(choices=[],
              id=wxID_PNLEDITPICTURECHOICEEFFECT, name=u'choiceEffect',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)
        self.choiceEffect.Bind(wx.EVT_CHOICE, self.OnChoiceEffectChoice,
              id=wxID_PNLEDITPICTURECHOICEEFFECT)

        self.staticLine1 = wx.StaticLine(id=wxID_PNLEDITPICTURESTATICLINE1,
              name='staticLine1', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.LI_VERTICAL)

        self.stProcess = wx.StaticText(id=wxID_PNLEDITPICTURESTPROCESS,
              label=_(u'Process'), name=u'stProcess', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.stMovement = wx.StaticText(id=wxID_PNLEDITPICTURESTMOVEMENT,
              label=_(u'Movement:'), name=u'stMovement', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.choiceMovement = wx.Choice(choices=[],
              id=wxID_PNLEDITPICTURECHOICEMOVEMENT, name=u'choiceMovement',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.pnlImgDuration = PnlFloatSpinCtrl(id=wxID_PNLEDITPICTUREPNLIMGDURATION,
              name=u'pnlImgDuration', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.TAB_TRAVERSAL)

        self.stDurationUnit = wx.StaticText(id=wxID_PNLEDITPICTURESTDURATIONUNIT,
              label=_(u'sec'), name=u'stDurationUnit', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.stTrans = wx.StaticText(id=wxID_PNLEDITPICTURESTTRANS,
              label=_(u'Transition:'), name=u'stTrans', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.choiceTrans = wx.Choice(choices=[],
              id=wxID_PNLEDITPICTURECHOICETRANS, name=u'choiceTrans',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.pnlTransDuration = PnlFloatSpinCtrl(id=wxID_PNLEDITPICTUREPNLTRANSDURATION,
              name=u'pnlTransDuration', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.TAB_TRAVERSAL)

        self.stTransUnit = wx.StaticText(id=wxID_PNLEDITPICTURESTTRANSUNIT,
              label=_(u'sec'), name=u'stTransUnit', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.staticLine2 = wx.StaticLine(id=wxID_PNLEDITPICTURESTATICLINE2,
              name='staticLine2', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.LI_VERTICAL)

        self.stSubtitle = wx.StaticText(id=wxID_PNLEDITPICTURESTSUBTITLE,
              label=_(u'Subtitle'), name=u'stSubtitle', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.tcComment = wx.TextCtrl(id=wxID_PNLEDITPICTURETCCOMMENT,
              name=u'tcComment', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.TE_MULTILINE, value='')
        self.tcComment.Bind(wx.EVT_TEXT, self.OnTextCtrlCommentText,
              id=wxID_PNLEDITPICTURETCCOMMENT)

        self._init_sizers()

    def __init__(self, parent, id, pos, size, style, name):
        self._init_ctrls(parent)

        font = self.stSettings.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.stSettings.SetFont(font)
        self.stProcess.SetFont(font)
        self.stSubtitle.SetFont(font)
        
        self.choiceMovement.Append(_(u"Linear"), Picture.MOVE_LINEAR)
        self.choiceMovement.Append(_(u"Accelerated"), Picture.MOVE_ACCEL)
        self.choiceMovement.Append(_(u"Delayed"), Picture.MOVE_DELAYED)
        self.choiceMovement.SetSelection(1)
        self.choiceMovement.Bind(wx.EVT_CHOICE, self.OnChoiceMvmntChoice)
        
        self.pnlImgDuration.SetRange(1, 6000)
        self.pnlImgDuration.SetValue(7)
        self.pnlImgDuration.Bind(EVT_VALUE_CHANGED, self.OnImgDurationChanged)
        
        self.choiceEffect.Append(_(u"No effect"), Picture.EFFECT_NONE)
        self.choiceEffect.Append(_(u"Black and White"), Picture.EFFECT_BLACK_WHITE)
        self.choiceEffect.Append(_(u"Sepia tone"), Picture.EFFECT_SEPIA)
        self.choiceEffect.SetSelection(0)
        
        self.pnlTransDuration.SetRange(5, 200)
        self.pnlTransDuration.SetValue(1)
        self.pnlTransDuration.Bind(EVT_VALUE_CHANGED, self.OnTransDurationChanged)
        self.choiceTrans.Append(_(u"None"), Picture.TRANS_NONE)
        self.choiceTrans.Append(_(u"Fade"), Picture.TRANS_FADE)
        self.choiceTrans.Append(_(u"Roll"), Picture.TRANS_ROLL)
        self.choiceTrans.SetSelection(1)
        self.choiceTrans.Bind(wx.EVT_CHOICE, self.OnChoiceTransChoice)

        self._pictures = []
        self.SetPictures(None)

    def __SetChoiceSelectionByData(self, choice, data):
        for idx in range(choice.GetCount()):
            if choice.GetClientData(idx) == data:
                choice.Select(idx)
                return

    def OnCmdRotateLeftButton(self, event):
        for pic in self._pictures:
            pic.Rotate(False)

    def OnCmdRotateRightButton(self, event):
        for pic in self._pictures:
            pic.Rotate(True)

    def OnChoiceEffectChoice(self, event):
        for pic in self._pictures:
            pic.SetEffect(event.GetClientData())
        event.Skip()
        
    def OnChoiceMvmntChoice(self, event):
        mvmnt = event.GetClientData()
        for pic in self._pictures:
            pic.SetMovement(mvmnt)
        event.Skip()
        
    def OnChoiceTransChoice(self, event):
        trans = event.GetClientData()
        for pic in self._pictures:
            pic.SetTransition(trans)
        self.pnlTransDuration.Enable(trans != Picture.TRANS_NONE)
        event.Skip()
    
    def OnTransDurationChanged(self, event):
        duration = event.GetValue()
        for pic in self._pictures:
            pic.SetTransitionDuration(duration)

    def OnImgDurationChanged(self, event):
        duration = event.GetValue()
        for pic in self._pictures:
            pic.SetDuration(duration)

    def OnTextCtrlCommentText(self, event):
        for pic in self._pictures:
            pic.SetComment(self.tcComment.GetValue())
        event.Skip()
        
    def SetPictures(self, pictures):
        if pictures is None:
            pictures = []
        self.Enable(len(pictures) > 0)

        self._pictures = pictures
        if self._pictures:
            pic = self._pictures[0]
            
            self.tcComment.SetValue(pic.GetComment())
            self.pnlImgDuration.SetValue(pic.GetDuration())
            self.__SetChoiceSelectionByData(self.choiceMovement, pic.GetMovement())
            self.__SetChoiceSelectionByData(self.choiceEffect, pic.GetEffect())
            
            self.__SetChoiceSelectionByData(self.choiceTrans, pic.GetTransition())
            self.pnlTransDuration.SetValue(pic.GetTransitionDuration(rawValue=True))
            self.pnlTransDuration.Enable(pic.GetTransition() != Picture.TRANS_NONE)
