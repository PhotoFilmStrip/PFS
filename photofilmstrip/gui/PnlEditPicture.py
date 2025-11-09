# Boa:FramePanel:PnlEditPicture
# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#

import wx

from photofilmstrip.core.Picture import Picture

from photofilmstrip.gui.Art import Art
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
] = [wx.NewIdRef() for _init_ctrls in range(20)]


class PnlEditPicture(wx.Panel):

    _custom_classes = {"wx.Panel": ["PnlFloatSpinCtrl"]}

    def _init_coll_sizerMain_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.szSettings, 0, border=self.FromDIP(4), flag=wx.ALL)
        parent.AddSpacer(self.FromDIP(8))
        parent.Add(self.staticLine1, 0, border=self.FromDIP(4), flag=wx.ALL | wx.EXPAND)
        parent.AddSpacer(self.FromDIP(8))
        parent.Add(self.szTimes, 0, border=self.FromDIP(4), flag=wx.ALL)
        parent.AddSpacer(self.FromDIP(8))
        parent.Add(self.staticLine2, 0, border=self.FromDIP(4), flag=wx.EXPAND | wx.ALL)
        parent.AddSpacer(self.FromDIP(8))
        parent.Add(self.szSubtitle, 1, border=self.FromDIP(4), flag=wx.ALL | wx.EXPAND)

    def _init_coll_szTimes_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.stProcess, 0, border=0, flag=0)
        parent.Add(self.sizerTimesCtrls, 0, border=self.FromDIP(16), flag=wx.LEFT)

    def _init_coll_szSubtitle_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.stSubtitle, 0, border=0, flag=0)
        parent.Add(self.tcComment, 1, border=self.FromDIP(16), flag=wx.LEFT | wx.EXPAND)

    def _init_coll_sizerTimesCtrls_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.stMovement, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.Add(self.choiceMovement, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)
        parent.Add(self.pnlImgDuration, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.Add(self.stDurationUnit, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.Add(self.stTrans, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.Add(self.choiceTrans, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)
        parent.Add(self.pnlTransDuration, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.Add(self.stTransUnit, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)

    def _init_coll_szSettings_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.stSettings, 0, border=0, flag=0)
        parent.Add(self.szSettingsCtrls, 0, border=self.FromDIP(16), flag=wx.LEFT)

    def _init_coll_szSettingsCtrls_Growables(self, parent):
        # generated method, don't edit

        parent.AddGrowableCol(1)  #!!!

    def _init_coll_szSettingsCtrls_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.stRotation, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.Add(self.sizerRotationTools, 0, border=0, flag=wx.EXPAND)
        parent.Add(self.stEffect, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.Add(self.choiceEffect, 0, border=0, flag=wx.EXPAND)

    def _init_coll_sizerRotationTools_Items(self, parent):
        # generated method, don't edit

        parent.Add(self.cmdRotateLeft, 0, border=0, flag=0)
        parent.AddStretchSpacer(1)
        parent.Add(self.cmdRotateRight, 0, border=0, flag=0)

    def _init_sizers(self):
        # generated method, don't edit
        self.sizerMain = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.szSettingsCtrls = wx.FlexGridSizer(cols=2, hgap=self.FromDIP(8), rows=2, vgap=self.FromDIP(8))

        self.szSubtitle = wx.BoxSizer(orient=wx.VERTICAL)

        self.sizerRotationTools = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.sizerTimesCtrls = wx.FlexGridSizer(cols=4, hgap=self.FromDIP(8), rows=2, vgap=self.FromDIP(8))

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
        wx.Panel.__init__(self, id=wxID_PNLEDITPICTURE, name="PnlEditPicture",
              parent=prnt, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.TAB_TRAVERSAL)

        self.stSettings = wx.StaticText(id=wxID_PNLEDITPICTURESTSETTINGS,
              label=_("Settings"), name="stSettings", parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.stRotation = wx.StaticText(id=wxID_PNLEDITPICTURESTROTATION,
              label=_("Rotation:"), name="stRotation", parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.cmdRotateLeft = wx.BitmapButton(bitmap=Art.GetBitmapBundle('PFS_IMAGE_ROTATION_LEFT', wx.ART_TOOLBAR),
              id=wxID_PNLEDITPICTURECMDROTATELEFT, name="cmdRotateLeft",
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.BU_AUTODRAW)
        self.cmdRotateLeft.SetBitmapDisabled(Art.GetBitmapBundle('PFS_IMAGE_ROTATION_LEFT_D', wx.ART_TOOLBAR))
        self.cmdRotateLeft.Bind(wx.EVT_BUTTON, self.OnCmdRotateLeftButton,
              id=wxID_PNLEDITPICTURECMDROTATELEFT)

        self.cmdRotateRight = wx.BitmapButton(bitmap=Art.GetBitmapBundle('PFS_IMAGE_ROTATION_RIGHT', wx.ART_TOOLBAR),
              id=wxID_PNLEDITPICTURECMDROTATERIGHT, name="cmdRotateRight",
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.BU_AUTODRAW)
        self.cmdRotateRight.SetBitmapDisabled(Art.GetBitmapBundle('PFS_IMAGE_ROTATION_RIGHT_D', wx.ART_TOOLBAR))
        self.cmdRotateRight.Bind(wx.EVT_BUTTON, self.OnCmdRotateRightButton,
              id=wxID_PNLEDITPICTURECMDROTATERIGHT)

        self.stEffect = wx.StaticText(id=wxID_PNLEDITPICTURESTEFFECT,
              label=_("Effect:"), name="stEffect", parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.choiceEffect = wx.Choice(choices=[],
              id=wxID_PNLEDITPICTURECHOICEEFFECT, name="choiceEffect",
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)
        self.choiceEffect.Bind(wx.EVT_CHOICE, self.OnChoiceEffectChoice,
              id=wxID_PNLEDITPICTURECHOICEEFFECT)

        self.staticLine1 = wx.StaticLine(id=wxID_PNLEDITPICTURESTATICLINE1,
              name='staticLine1', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.LI_VERTICAL)

        self.stProcess = wx.StaticText(id=wxID_PNLEDITPICTURESTPROCESS,
              label=_("Process"), name="stProcess", parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.stMovement = wx.StaticText(id=wxID_PNLEDITPICTURESTMOVEMENT,
              label=_("Movement:"), name='stMovement', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.choiceMovement = wx.Choice(choices=[],
              id=wxID_PNLEDITPICTURECHOICEMOVEMENT, name="choiceMovement",
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.pnlImgDuration = PnlFloatSpinCtrl(id=wxID_PNLEDITPICTUREPNLIMGDURATION,
              name="pnlImgDuration", parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.TAB_TRAVERSAL)

        self.stDurationUnit = wx.StaticText(id=wxID_PNLEDITPICTURESTDURATIONUNIT,
              label=_("sec"), name="stDurationUnit", parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.stTrans = wx.StaticText(id=wxID_PNLEDITPICTURESTTRANS,
              label=_("Transition:"), name="stTrans", parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.choiceTrans = wx.Choice(choices=[],
              id=wxID_PNLEDITPICTURECHOICETRANS, name="choiceTrans",
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.pnlTransDuration = PnlFloatSpinCtrl(id=wxID_PNLEDITPICTUREPNLTRANSDURATION,
              name="pnlTransDuration", parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.TAB_TRAVERSAL)

        self.stTransUnit = wx.StaticText(id=wxID_PNLEDITPICTURESTTRANSUNIT,
              label=_("sec"), name="stTransUnit", parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.staticLine2 = wx.StaticLine(id=wxID_PNLEDITPICTURESTATICLINE2,
              name='staticLine2', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.LI_VERTICAL)

        self.stSubtitle = wx.StaticText(id=wxID_PNLEDITPICTURESTSUBTITLE,
              label=_("Subtitle"), name="stSubtitle", parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.tcComment = wx.TextCtrl(id=wxID_PNLEDITPICTURETCCOMMENT,
              name="tcComment", parent=self, pos=wx.Point(-1, -1),
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

        self.choiceMovement.Append(_("Linear"), Picture.MOVE_LINEAR)
        self.choiceMovement.Append(_("Accelerated"), Picture.MOVE_ACCEL)
        self.choiceMovement.Append(_("Delayed"), Picture.MOVE_DELAYED)
        self.choiceMovement.SetSelection(1)
        self.choiceMovement.Bind(wx.EVT_CHOICE, self.OnChoiceMvmntChoice)

        self.pnlImgDuration.SetRange(1, 6000)
        self.pnlImgDuration.SetValue(7)
        self.pnlImgDuration.Bind(EVT_VALUE_CHANGED, self.OnImgDurationChanged)

        self.choiceEffect.Append(_("No effect"), Picture.EFFECT_NONE)
        self.choiceEffect.Append(_("Black and White"), Picture.EFFECT_BLACK_WHITE)
        self.choiceEffect.Append(_("Sepia tone"), Picture.EFFECT_SEPIA)
        self.choiceEffect.SetSelection(0)

        self.pnlTransDuration.SetRange(5, 200)
        self.pnlTransDuration.SetValue(1)
        self.pnlTransDuration.Bind(EVT_VALUE_CHANGED, self.OnTransDurationChanged)
        self.choiceTrans.Append(_("None"), Picture.TRANS_NONE)
        self.choiceTrans.Append(_("Fade"), Picture.TRANS_FADE)
        self.choiceTrans.Append(_("Roll"), Picture.TRANS_ROLL)
        self.choiceTrans.SetSelection(1)
        self.choiceTrans.Bind(wx.EVT_CHOICE, self.OnChoiceTransChoice)

        self._pictures = []
        self.SetPictures(None)

    def __FindChoiceIdxByData(self, choice, data):
        for idx in range(choice.GetCount()):
            if choice.GetClientData(idx) == data:
                return idx
        return wx.NOT_FOUND

    def __GetChoiceDataBySelection(self, choice):
        selIdx = choice.GetSelection()
        if selIdx != wx.NOT_FOUND:
            return choice.GetClientData(selIdx)
        else:
            return None

    def __SetChoiceSelectionByData(self, choice, data):
        idx = self.__FindChoiceIdxByData(choice, data)
        if idx != wx.NOT_FOUND:
            choice.Select(idx)

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

            self.tcComment.ChangeValue(pic.GetComment())
            self.pnlImgDuration.SetValue(pic.GetDuration())
            self.__SetChoiceSelectionByData(self.choiceMovement, pic.GetMovement())
            self.__SetChoiceSelectionByData(self.choiceEffect, pic.GetEffect())

            self.__SetChoiceSelectionByData(self.choiceTrans, pic.GetTransition())
            self.pnlTransDuration.SetValue(pic.GetTransitionDuration(rawValue=True))
            self.pnlTransDuration.Enable(pic.GetTransition() != Picture.TRANS_NONE)

    def SetupModeByProject(self, project):
        if project.GetTimelapse():
            selTrans = self.choiceTrans.GetSelection()
            rollIdx = self.__FindChoiceIdxByData(
                self.choiceTrans, Picture.TRANS_ROLL)
            if rollIdx != wx.NOT_FOUND:
                self.choiceTrans.Delete(rollIdx)
            if rollIdx == selTrans:
                self.choiceTrans.Select(0)

            unit = _("fpp")
            tooltip = _("frames per picture - the number of frames each picture will be shown")
        else:
            projDuration = project.GetDuration(calc=False)
            if projDuration is None:
                unit = _('sec')
            else:
                # project duration is set to a fixed value (or by music), so
                # the units are not seconds but kind of ratio time
                unit = "-"
            tooltip = ""

        self.stDurationUnit.SetLabel(unit)
        self.stTransUnit.SetLabel(unit)
        self.stDurationUnit.SetToolTip(tooltip)
        self.stTransUnit.SetToolTip(tooltip)
