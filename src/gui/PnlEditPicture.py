#Boa:FramePanel:PnlEditPicture
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

from core.Picture import Picture

from gui.util.FloatValidator import FloatValidator


[wxID_PNLEDITPICTURE, wxID_PNLEDITPICTURECHOICEEFFECT, 
 wxID_PNLEDITPICTURECMDROTATELEFT, wxID_PNLEDITPICTURECMDROTATERIGHT, 
 wxID_PNLEDITPICTURESPINBUTTONDURATION, wxID_PNLEDITPICTURESTATICLINE1, 
 wxID_PNLEDITPICTURESTDURATION, wxID_PNLEDITPICTURESTEFFECT, 
 wxID_PNLEDITPICTURESTROTATION, wxID_PNLEDITPICTURESTSUBTITLE, 
 wxID_PNLEDITPICTURETCCOMMENT, wxID_PNLEDITPICTURETCDURATION, 
] = [wx.NewId() for _init_ctrls in range(12)]


class PnlEditPicture(wx.Panel):
    
    def _init_coll_sizerMain_Items(self, parent):
        # generated method, don't edit

        parent.AddSizer(self.sizerLeft, 0, border=4, flag=wx.ALL)
        parent.AddWindow(self.staticLine1, 0, border=4, flag=wx.ALL | wx.EXPAND)
        parent.AddSizer(self.sizerRight, 1, border=4, flag=wx.ALL | wx.EXPAND)

    def _init_coll_sizerLeft_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stRotation, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddSizer(self.sizerRotationTools, 0, border=0, flag=wx.EXPAND)
        parent.AddWindow(self.stEffect, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.choiceEffect, 0, border=0, flag=wx.EXPAND)
        parent.AddWindow(self.stDuration, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddSizer(self.spinSizer, 0, border=0, flag=wx.EXPAND)

    def _init_coll_sizerLeft_Growables(self, parent):
        # generated method, don't edit

        parent.AddGrowableCol(1)

    def _init_coll_spinSizer_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.tcDuration, 1, border=0, flag=0)
        parent.AddWindow(self.spinButtonDuration, 0, border=0, flag=0)

    def _init_coll_sizerRight_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stSubtitle, 0, border=0, flag=0)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.tcComment, 1, border=0, flag=wx.EXPAND)

    def _init_coll_sizerRotationTools_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.cmdRotateLeft, 0, border=0, flag=0)
        parent.AddStretchSpacer(1)
        parent.AddWindow(self.cmdRotateRight, 0, border=0, flag=0)

    def _init_sizers(self):
        # generated method, don't edit
        self.sizerMain = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.sizerLeft = wx.FlexGridSizer(cols=2, hgap=8, rows=2, vgap=8)

        self.sizerRight = wx.BoxSizer(orient=wx.VERTICAL)

        self.spinSizer = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.sizerRotationTools = wx.BoxSizer(orient=wx.HORIZONTAL)

        self._init_coll_sizerMain_Items(self.sizerMain)
        self._init_coll_sizerLeft_Items(self.sizerLeft)
        self._init_coll_sizerLeft_Growables(self.sizerLeft)
        self._init_coll_sizerRight_Items(self.sizerRight)
        self._init_coll_spinSizer_Items(self.spinSizer)
        self._init_coll_sizerRotationTools_Items(self.sizerRotationTools)

        self.SetSizer(self.sizerMain)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Panel.__init__(self, id=wxID_PNLEDITPICTURE, name=u'PnlEditPicture',
              parent=prnt, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.TAB_TRAVERSAL)
        self.SetClientSize(wx.Size(687, 192))

        self.stRotation = wx.StaticText(id=wxID_PNLEDITPICTURESTROTATION,
              label=_(u'Rotation:'), name=u'stRotation', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.cmdRotateLeft = wx.BitmapButton(bitmap=wx.ArtProvider.GetBitmap('wxART_UNDO',
              wx.ART_TOOLBAR, wx.DefaultSize),
              id=wxID_PNLEDITPICTURECMDROTATELEFT, name=u'cmdRotateLeft',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.BU_AUTODRAW)
        self.cmdRotateLeft.Bind(wx.EVT_BUTTON, self.OnCmdRotateLeftButton,
              id=wxID_PNLEDITPICTURECMDROTATELEFT)

        self.cmdRotateRight = wx.BitmapButton(bitmap=wx.ArtProvider.GetBitmap('wxART_REDO',
              wx.ART_TOOLBAR, wx.DefaultSize),
              id=wxID_PNLEDITPICTURECMDROTATERIGHT, name=u'cmdRotateRight',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.BU_AUTODRAW)
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

        self.stDuration = wx.StaticText(id=wxID_PNLEDITPICTURESTDURATION,
              label=_(u'Duartion (sec):'), name=u'stDuration', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.tcDuration = wx.TextCtrl(id=wxID_PNLEDITPICTURETCDURATION,
              name=u'tcDuration', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0, value=u'5.0')
        self.tcDuration.Bind(wx.EVT_KILL_FOCUS,
              self.OnTextCtrlDurationKillFocus,
              id=wxID_PNLEDITPICTURETCDURATION)
        self.tcDuration.Bind(wx.EVT_TEXT,
              self.OnTextCtrlDurationText,
              id=wxID_PNLEDITPICTURETCDURATION)

        self.spinButtonDuration = wx.SpinButton(id=wxID_PNLEDITPICTURESPINBUTTONDURATION,
              name=u'spinButtonDuration', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.SP_VERTICAL)
        self.spinButtonDuration.Bind(wx.EVT_SPIN, self.OnSpinButtonDurationSpin,
              id=wxID_PNLEDITPICTURESPINBUTTONDURATION)

        self.staticLine1 = wx.StaticLine(id=wxID_PNLEDITPICTURESTATICLINE1,
              name='staticLine1', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.LI_VERTICAL)

        self.stSubtitle = wx.StaticText(id=wxID_PNLEDITPICTURESTSUBTITLE,
              label=_(u'Subtitle:'), name=u'stSubtitle', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.tcComment = wx.TextCtrl(id=wxID_PNLEDITPICTURETCCOMMENT,
              name=u'tcComment', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.TE_MULTILINE, value='')
        self.tcComment.Bind(wx.EVT_TEXT, self.OnTextCtrlCommentText,
              id=wxID_PNLEDITPICTURETCCOMMENT)

        self._init_sizers()

    def __init__(self, parent, id, pos, size, style, name):
        self._init_ctrls(parent)
        self.tcDuration.SetValidator(FloatValidator())
        self.spinButtonDuration.SetMinSize(wx.Size(-1, self.tcDuration.GetSizeTuple()[1]))
        self.spinButtonDuration.SetRange(10, 200)
        self.spinButtonDuration.SetValue(50)
        
        self.choiceEffect.Append(_(u"No effect"), Picture.EFFECT_NONE)
        self.choiceEffect.Append(_(u"Black and White"), Picture.EFFECT_BLACK_WHITE)
        self.choiceEffect.Append(_(u"Sepia tone"), Picture.EFFECT_SEPIA)
        self.choiceEffect.SetSelection(0)
        
        self._picture = None

    def __SetChoiceSelectionByData(self, choice, data):
        for idx in range(choice.GetCount()):
            if choice.GetClientData(idx) == data:
                choice.Select(idx)
                return

    def OnCmdRotateLeftButton(self, event):
        self._picture.Rotate(False)
        event.Skip()

    def OnCmdRotateRightButton(self, event):
        self._picture.Rotate(True)
        event.Skip()

    def OnChoiceEffectChoice(self, event):
        self._picture.SetEffect(event.GetClientData())
        event.Skip()

    def OnSpinButtonDurationSpin(self, event):
        duration = event.GetPosition() / 10.0
        self.tcDuration.SetValue("%.1f" % duration)
        self._picture.SetDuration(duration)
        event.Skip()
    
    def OnTextCtrlDurationKillFocus(self, event):
        duration = self.__GetDuration()
        self.spinButtonDuration.SetValue(int(duration * 10))
        self.tcDuration.SetValue("%.1f" % duration)
        event.Skip()
        
    def OnTextCtrlDurationText(self, event):
        duration = self.__GetDuration()
        self._picture.SetDuration(duration)
        event.Skip()
        
    def OnTextCtrlCommentText(self, event):
        self._picture.SetComment(self.tcComment.GetValue())
        event.Skip()
        
    def __GetDuration(self):
        val = self.tcDuration.GetValue()
        try:
            floatVal = max(float(val), 1.0)
        except ValueError:
            floatVal = 1.0
        return floatVal
    
    def SetPicture(self, picture):
        self.Enable(picture is not None)

        self._picture = picture
        if self._picture is not None:
            duration = self._picture.GetDuration()
            self.tcDuration.SetValue("%.1f" % duration)
            self.spinButtonDuration.SetValue(int(duration * 10))
            self.tcComment.SetValue(self._picture.GetComment())
            self.__SetChoiceSelectionByData(self.choiceEffect, self._picture.GetEffect())
            
