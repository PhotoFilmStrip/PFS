#Boa:Dialog:DlgPositionInput
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

import wx

from core.Aspect import Aspect


[wxID_DLGPOSITIONINPUT, wxID_DLGPOSITIONINPUTBMPHDR, 
 wxID_DLGPOSITIONINPUTCMDCANCEL, wxID_DLGPOSITIONINPUTCMDOK, 
 wxID_DLGPOSITIONINPUTCMDRESET, wxID_DLGPOSITIONINPUTPNLHDR, 
 wxID_DLGPOSITIONINPUTSLENDPOS, wxID_DLGPOSITIONINPUTSLHDR, 
 wxID_DLGPOSITIONINPUTSLSTARTPOS, wxID_DLGPOSITIONINPUTSPINENDHEIGHT, 
 wxID_DLGPOSITIONINPUTSPINENDWIDTH, wxID_DLGPOSITIONINPUTSPINENDX, 
 wxID_DLGPOSITIONINPUTSPINENDY, wxID_DLGPOSITIONINPUTSPINSTARTHEIGHT, 
 wxID_DLGPOSITIONINPUTSPINSTARTWIDTH, wxID_DLGPOSITIONINPUTSPINSTARTX, 
 wxID_DLGPOSITIONINPUTSPINSTARTY, wxID_DLGPOSITIONINPUTSTENDLOCATION, 
 wxID_DLGPOSITIONINPUTSTENDPOS, wxID_DLGPOSITIONINPUTSTENDSIZE, 
 wxID_DLGPOSITIONINPUTSTHDR, wxID_DLGPOSITIONINPUTSTSTARTLOCATION, 
 wxID_DLGPOSITIONINPUTSTSTARTPOS, wxID_DLGPOSITIONINPUTSTSTARTSIZE, 
] = [wx.NewId() for _init_ctrls in range(24)]


class DlgPositionInput(wx.Dialog):
    def _init_coll_szStart_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stStartLocation, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.spinStartX, 0, border=0, flag=0)
        parent.AddWindow(self.spinStartY, 0, border=0, flag=0)
        parent.AddWindow(self.stStartSize, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.spinStartWidth, 0, border=0, flag=0)
        parent.AddWindow(self.spinStartHeight, 0, border=0, flag=0)

    def _init_coll_szStartHdr_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stStartPos, 0, border=0, flag=0)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.slStartPos, 1, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)

    def _init_coll_szEndCtrls_Items(self, parent):
        # generated method, don't edit

        parent.AddSpacer(wx.Size(16, 8), border=0, flag=0)
        parent.AddSizer(self.szEnd, 1, border=0, flag=0)

    def _init_coll_szEnd_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stEndLocation, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.spinEndX, 0, border=0, flag=0)
        parent.AddWindow(self.spinEndY, 0, border=0, flag=0)
        parent.AddWindow(self.stEndSize, 0, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)
        parent.AddWindow(self.spinEndWidth, 0, border=0, flag=0)
        parent.AddWindow(self.spinEndHeight, 0, border=0, flag=0)

    def _init_coll_szCmds_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.cmdReset, 0, border=0, flag=0)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.cmdCancel, 0, border=0, flag=0)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.cmdOk, 0, border=0, flag=0)

    def _init_coll_szMain_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.pnlHdr, 0, border=0, flag=wx.EXPAND)
        parent.AddWindow(self.slHdr, 0, border=0, flag=wx.EXPAND)
        parent.AddSizer(self.szStartHdr, 0, border=4, flag=wx.ALL | wx.EXPAND)
        parent.AddSizer(self.szStartCtrls, 0, border=4, flag=wx.EXPAND | wx.ALL)
        parent.AddSpacer(wx.Size(8, 16), border=0, flag=0)
        parent.AddSizer(self.szEndHdr, 0, border=4, flag=wx.ALL | wx.EXPAND)
        parent.AddSizer(self.szEndCtrls, 0, border=4, flag=wx.EXPAND | wx.ALL)
        parent.AddSpacer(wx.Size(8, 16), border=0, flag=0)
        parent.AddSizer(self.szCmds, 0, border=4, flag=wx.ALL | wx.ALIGN_RIGHT)

    def _init_coll_szHdr_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.bmpHdr, 0, border=8, flag=wx.ALL)
        parent.AddWindow(self.stHdr, 0, border=8,
              flag=wx.ALIGN_CENTER_VERTICAL | wx.ALL)

    def _init_coll_szStartCtrls_Items(self, parent):
        # generated method, don't edit

        parent.AddSpacer(wx.Size(16, 8), border=0, flag=0)
        parent.AddSizer(self.szStart, 1, border=0, flag=0)

    def _init_coll_szEndHdr_Items(self, parent):
        # generated method, don't edit

        parent.AddWindow(self.stEndPos, 0, border=0, flag=0)
        parent.AddSpacer(wx.Size(8, 8), border=0, flag=0)
        parent.AddWindow(self.slEndPos, 1, border=0,
              flag=wx.ALIGN_CENTER_VERTICAL)

    def _init_sizers(self):
        # generated method, don't edit
        self.szMain = wx.BoxSizer(orient=wx.VERTICAL)

        self.szStart = wx.FlexGridSizer(cols=3, hgap=4, rows=2, vgap=8)

        self.szStartHdr = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.szEndHdr = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.szStartCtrls = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.szEnd = wx.FlexGridSizer(cols=3, hgap=4, rows=2, vgap=8)

        self.szEndCtrls = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.szCmds = wx.BoxSizer(orient=wx.HORIZONTAL)

        self.szHdr = wx.BoxSizer(orient=wx.HORIZONTAL)

        self._init_coll_szMain_Items(self.szMain)
        self._init_coll_szStart_Items(self.szStart)
        self._init_coll_szStartHdr_Items(self.szStartHdr)
        self._init_coll_szEndHdr_Items(self.szEndHdr)
        self._init_coll_szStartCtrls_Items(self.szStartCtrls)
        self._init_coll_szEnd_Items(self.szEnd)
        self._init_coll_szEndCtrls_Items(self.szEndCtrls)
        self._init_coll_szCmds_Items(self.szCmds)
        self._init_coll_szHdr_Items(self.szHdr)

        self.SetSizer(self.szMain)
        self.pnlHdr.SetSizer(self.szHdr)

    def _init_ctrls(self, prnt):
        # generated method, don't edit
        wx.Dialog.__init__(self, id=wxID_DLGPOSITIONINPUT,
              name=u'DlgPositionInput', parent=prnt, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=wx.DEFAULT_DIALOG_STYLE,
              title=_(u'Motion positions'))

        self.pnlHdr = wx.Panel(id=wxID_DLGPOSITIONINPUTPNLHDR, name=u'pnlHdr',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.TAB_TRAVERSAL)
        self.pnlHdr.SetBackgroundColour(wx.Colour(255, 255, 255))

        self.bmpHdr = wx.StaticBitmap(bitmap=wx.ArtProvider.GetBitmap('PFS_MOTION_INPUT',
              wx.ART_TOOLBAR, (32, 32)), id=wxID_DLGPOSITIONINPUTBMPHDR,
              name=u'bmpHdr', parent=self.pnlHdr, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.stHdr = wx.StaticText(id=wxID_DLGPOSITIONINPUTSTHDR,
              label=_(u'Adjust motion positions directly'), name=u'stHdr',
              parent=self.pnlHdr, pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=0)

        self.slHdr = wx.StaticLine(id=wxID_DLGPOSITIONINPUTSLHDR, name=u'slHdr',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.stStartPos = wx.StaticText(id=wxID_DLGPOSITIONINPUTSTSTARTPOS,
              label=_(u'Start position'), name=u'stStartPos', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.slStartPos = wx.StaticLine(id=wxID_DLGPOSITIONINPUTSLSTARTPOS,
              name=u'slStartPos', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.stStartLocation = wx.StaticText(id=wxID_DLGPOSITIONINPUTSTSTARTLOCATION,
              label=_(u'Location:'), name=u'stStartLocation', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.spinStartX = wx.SpinCtrl(id=wxID_DLGPOSITIONINPUTSPINSTARTX,
              initial=0, max=100, min=0, name=u'spinStartX', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.SP_ARROW_KEYS)
        self.spinStartX.Bind(wx.EVT_TEXT, self.OnSpinChange,
              id=wxID_DLGPOSITIONINPUTSPINSTARTX)

        self.spinStartY = wx.SpinCtrl(id=wxID_DLGPOSITIONINPUTSPINSTARTY,
              initial=0, max=100, min=0, name=u'spinStartY', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.SP_ARROW_KEYS)
        self.spinStartY.Bind(wx.EVT_TEXT, self.OnSpinChange,
              id=wxID_DLGPOSITIONINPUTSPINSTARTY)

        self.stStartSize = wx.StaticText(id=wxID_DLGPOSITIONINPUTSTSTARTSIZE,
              label=_(u'Size:'), name=u'stStartSize', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.spinStartWidth = wx.SpinCtrl(id=wxID_DLGPOSITIONINPUTSPINSTARTWIDTH,
              initial=0, max=100, min=0, name=u'spinStartWidth', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.SP_ARROW_KEYS)
        self.spinStartWidth.Bind(wx.EVT_TEXT, self.OnSpinChange,
              id=wxID_DLGPOSITIONINPUTSPINSTARTWIDTH)

        self.spinStartHeight = wx.SpinCtrl(id=wxID_DLGPOSITIONINPUTSPINSTARTHEIGHT,
              initial=0, max=100, min=0, name=u'spinStartHeight', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.SP_ARROW_KEYS)
        self.spinStartHeight.Bind(wx.EVT_TEXT, self.OnSpinChange,
              id=wxID_DLGPOSITIONINPUTSPINSTARTHEIGHT)

        self.stEndPos = wx.StaticText(id=wxID_DLGPOSITIONINPUTSTENDPOS,
              label=_(u'End position'), name=u'stEndPos', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.slEndPos = wx.StaticLine(id=wxID_DLGPOSITIONINPUTSLENDPOS,
              name=u'slEndPos', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)

        self.stEndLocation = wx.StaticText(id=wxID_DLGPOSITIONINPUTSTENDLOCATION,
              label=_(u'Location:'), name=u'stEndLocation', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self.spinEndX = wx.SpinCtrl(id=wxID_DLGPOSITIONINPUTSPINENDX, initial=0,
              max=100, min=0, name=u'spinEndX', parent=self, pos=wx.Point(-1,
              -1), size=wx.Size(-1, -1), style=wx.SP_ARROW_KEYS)
        self.spinEndX.Bind(wx.EVT_TEXT, self.OnSpinChange,
              id=wxID_DLGPOSITIONINPUTSPINENDX)

        self.spinEndY = wx.SpinCtrl(id=wxID_DLGPOSITIONINPUTSPINENDY, initial=0,
              max=100, min=0, name=u'spinEndY', parent=self, pos=wx.Point(-1,
              -1), size=wx.Size(-1, -1), style=wx.SP_ARROW_KEYS)
        self.spinEndY.Bind(wx.EVT_TEXT, self.OnSpinChange,
              id=wxID_DLGPOSITIONINPUTSPINENDY)

        self.stEndSize = wx.StaticText(id=wxID_DLGPOSITIONINPUTSTENDSIZE,
              label=_(u'Size:'), name=u'stEndSize', parent=self, pos=wx.Point(-1,
              -1), size=wx.Size(-1, -1), style=0)

        self.spinEndWidth = wx.SpinCtrl(id=wxID_DLGPOSITIONINPUTSPINENDWIDTH,
              initial=0, max=100, min=0, name=u'spinEndWidth', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.SP_ARROW_KEYS)
        self.spinEndWidth.Bind(wx.EVT_TEXT, self.OnSpinChange,
              id=wxID_DLGPOSITIONINPUTSPINENDWIDTH)

        self.spinEndHeight = wx.SpinCtrl(id=wxID_DLGPOSITIONINPUTSPINENDHEIGHT,
              initial=0, max=100, min=0, name=u'spinEndHeight', parent=self,
              pos=wx.Point(-1, -1), size=wx.Size(-1, -1),
              style=wx.SP_ARROW_KEYS)
        self.spinEndHeight.Bind(wx.EVT_TEXT, self.OnSpinChange,
              id=wxID_DLGPOSITIONINPUTSPINENDHEIGHT)

        self.cmdReset = wx.Button(id=wxID_DLGPOSITIONINPUTCMDRESET,
              label=_(u'Reset'), name=u'cmdReset', parent=self, pos=wx.Point(-1,
              -1), size=wx.Size(-1, -1), style=0)
        self.cmdReset.Bind(wx.EVT_BUTTON, self.OnCmdResetButton,
              id=wxID_DLGPOSITIONINPUTCMDRESET)

        self.cmdCancel = wx.Button(id=wx.ID_CANCEL, label=_(u'&Cancel'),
              name=u'cmdCancel', parent=self, pos=wx.Point(-1, -1),
              size=wx.Size(-1, -1), style=0)
        self.cmdCancel.Bind(wx.EVT_BUTTON, self.OnCmdCancelButton,
              id=wx.ID_CANCEL)

        self.cmdOk = wx.Button(id=wx.ID_OK, label=_(u'&Ok'), name=u'cmdOk',
              parent=self, pos=wx.Point(-1, -1), size=wx.Size(-1, -1), style=0)

        self._init_sizers()

    def __init__(self, parent, pic, aspect):
        self._init_ctrls(parent)

        font = self.stHdr.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.stHdr.SetFont(font)
        
        self.__pic = pic
        self.__ratio = Aspect.ToFloat(aspect)
        self.__doOnChange = True
        
        self.__backupStart = self.__pic.GetStartRect()
        self.__backupEnd = self.__pic.GetTargetRect()
        
        font = self.stStartPos.GetFont()
        font.SetWeight(wx.FONTWEIGHT_BOLD)
        self.stStartPos.SetFont(font)
        self.stEndPos.SetFont(font)
        
        self._InitValues()
        
        self.SetInitialSize(self.GetEffectiveMinSize())
        self.CenterOnParent()        
        
    def _InitValues(self):
        self.__doOnChange = False
        # Init ranges with max values
        self.spinStartX.SetRange(0, self.__pic.GetWidth())
        self.spinStartY.SetRange(0, self.__pic.GetHeight())
        self.spinStartWidth.SetRange(0, min(int(round(self.__pic.GetHeight() * self.__ratio)), 
                                            self.__pic.GetWidth()))
        self.spinStartHeight.SetRange(0, min(int(round(self.__pic.GetWidth() / self.__ratio)), 
                                             self.__pic.GetHeight()))
        
        self.spinEndX.SetRange(0, self.__pic.GetWidth())
        self.spinEndY.SetRange(0, self.__pic.GetHeight())
        self.spinEndWidth.SetRange(0, min(int(round(self.__pic.GetHeight() * self.__ratio)), 
                                          self.__pic.GetWidth()))
        self.spinEndHeight.SetRange(0, min(int(round(self.__pic.GetWidth() / self.__ratio)), 
                                           self.__pic.GetHeight()))
        
        # Init values
        self.spinStartX.SetValue(self.__pic.GetStartRect()[0])
        self.spinStartY.SetValue(self.__pic.GetStartRect()[1])
        self.spinStartWidth.SetValue(self.__pic.GetStartRect()[2])
        self.spinStartHeight.SetValue(self.__pic.GetStartRect()[3])

        self.spinEndX.SetValue(self.__pic.GetTargetRect()[0])
        self.spinEndY.SetValue(self.__pic.GetTargetRect()[1])
        self.spinEndWidth.SetValue(self.__pic.GetTargetRect()[2])
        self.spinEndHeight.SetValue(self.__pic.GetTargetRect()[3])

        self.__doOnChange = True
        
        self._SetupRanges()
        
    def _SetupRanges(self):
        '''
        Limit the location ranges to the current adjusted size
        '''
        self.spinStartX.SetRange(0, self.__pic.GetWidth() - self.spinStartWidth.GetValue())
        self.spinStartY.SetRange(0, self.__pic.GetHeight() - self.spinStartHeight.GetValue())
        
        self.spinEndX.SetRange(0, self.__pic.GetWidth() - self.spinEndWidth.GetValue())
        self.spinEndY.SetRange(0, self.__pic.GetHeight() - self.spinEndHeight.GetValue())
        
    def _PreserveAspect(self, wxId):
        self.__doOnChange = False

        if wxId == wxID_DLGPOSITIONINPUTSPINSTARTWIDTH:
            self.spinStartHeight.SetValue(int(round(self.spinStartWidth.GetValue() / self.__ratio)))
        if wxId == wxID_DLGPOSITIONINPUTSPINSTARTHEIGHT:
            self.spinStartWidth.SetValue(int(round(self.spinStartHeight.GetValue() * self.__ratio)))

        if wxId == wxID_DLGPOSITIONINPUTSPINENDWIDTH:
            self.spinEndHeight.SetValue(int(round(self.spinEndWidth.GetValue() / self.__ratio)))
        if wxId == wxID_DLGPOSITIONINPUTSPINENDHEIGHT:
            self.spinEndWidth.SetValue(int(round(self.spinEndHeight.GetValue() * self.__ratio)))

        self.__doOnChange = True
        
    def OnSpinChange(self, event):
        if not self.__doOnChange:
            return
        self._PreserveAspect(event.GetId())
        
        startRect = (self.spinStartX.GetValue(), self.spinStartY.GetValue(),
                     self.spinStartWidth.GetValue(), self.spinStartHeight.GetValue())
        
        endRect = (self.spinEndX.GetValue(), self.spinEndY.GetValue(),
                   self.spinEndWidth.GetValue(), self.spinEndHeight.GetValue())
        
        if event.GetId() in (wxID_DLGPOSITIONINPUTSPINENDWIDTH, wxID_DLGPOSITIONINPUTSPINENDHEIGHT,
                             wxID_DLGPOSITIONINPUTSPINSTARTWIDTH, wxID_DLGPOSITIONINPUTSPINSTARTHEIGHT):
            self._SetupRanges()
            
        self.__pic.SetStartRect(startRect)
        self.__pic.SetTargetRect(endRect)
        
        event.Skip()

    def OnCmdResetButton(self, event):
        self.__pic.SetStartRect(self.__backupStart)
        self.__pic.SetTargetRect(self.__backupEnd)
        self._InitValues()
        event.Skip()

    def OnCmdCancelButton(self, event):
        self.__pic.SetStartRect(self.__backupStart)
        self.__pic.SetTargetRect(self.__backupEnd)
        event.Skip()
