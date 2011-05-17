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

from gui.util.ImageCache import ImageCache


EVT_CHANGED_TYPE  = wx.NewEventType()
EVT_CHANGED       = wx.PyEventBinder(EVT_CHANGED_TYPE, 1)


class ChangedEvent(wx.PyCommandEvent):
    def __init__(self, wxId):
        wx.PyCommandEvent.__init__(self, EVT_CHANGED_TYPE, wxId)


class PhotoFilmStripList(wx.ScrolledWindow):
    
    HEIGHT = 200
    BORDER = 40
    GAP    = 10
    
    def __init__(self, parent, id=-1, 
                 pos=wx.DefaultPosition, size=wx.DefaultSize, 
                 style=wx.HSCROLL | wx.VSCROLL, name='PhotoFilmStripList'):
        wx.ScrolledWindow.__init__(self, parent, id, pos, size,  style, name)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.SetBackgroundColour(wx.BLACK)
        self.SetClientSizeWH(-1, self.HEIGHT+20)
        
        self.__pictures = []
        self.__selIdx   = -1
        self.__hvrIdx   = -1
        
        self.__dragPic  = None
        self.__dragX    = 0
        self.__dragOffX = 0
        
        self.__UpdateVirtualSize()
        
        self.SetScrollRate(1, 0)
        
        self.Bind(wx.EVT_MOUSEWHEEL, self.OnMouseWheel)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvent)
        self.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.Bind(wx.EVT_MOUSE_CAPTURE_LOST, self.OnCaptureLost)
        
    def OnPaint(self, event):
        pdc = wx.BufferedPaintDC(self)
        try:
            dc = wx.GCDC(pdc)
        except StandardError:
            dc = pdc
        
        self.PrepareDC(dc)

        font = wx.SystemSettings_GetFont(wx.SYS_ANSI_FIXED_FONT)
        font.SetPointSize(9)
        dc.SetFont(font)
        dc.SetTextForeground(wx.Color(237, 156, 0))
        dc.SetBackground(wx.BLACK_BRUSH)

        dc.Clear()
        
        dc.SetBrush(wx.WHITE_BRUSH)
        dc.SetPen(wx.WHITE_PEN)

        vx = self.GetViewStart()[0]
        hx = self.GetClientSize()[0]

        sxPic = self.GAP
        n = 0
        for idx, pic in enumerate(self.__pictures):
            bmp = ImageCache().GetThumbBmp(pic)

            # if the picture cannot be loaded GetWidth may return -1
            stepWidth = bmp.GetWidth() + self.GAP

            if sxPic >= vx - stepWidth:
                if sxPic <= vx + hx:
                    dc.DrawBitmap(bmp, sxPic, self.BORDER, True)
                    labelRect = wx.Rect(sxPic, 0, bmp.GetWidth(), self.HEIGHT)
                    dc.DrawLabel(str(idx + 1), labelRect, wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_TOP)
                    dc.DrawLabel(os.path.basename(pic.GetFilename()), 
                                 labelRect, 
                                 wx.ALIGN_CENTER_HORIZONTAL | wx.ALIGN_BOTTOM)
                else:
                    break

            sxPic += stepWidth
            
            # draw filmstrip
            while 1:
                sxFilmStrip = (n * 32) + 10
                if sxFilmStrip > sxPic:
                    break
                
                dc.DrawRoundedRectangle(sxFilmStrip, 14, 14, 20, 3)
                dc.DrawRoundedRectangle(sxFilmStrip, self.HEIGHT - 34, 14, 20, 3)
                n += 1
            
        self.__DrawHighlights(dc)
        
        if self.__dragPic is not None:
            if self.__dragPic >= 0 and self.__dragPic < len(self.__pictures):
                bmp = ImageCache().GetThumbBmp(self.__pictures[self.__dragPic])
                dc.DrawBitmap(bmp, self.__dragX - self.__dragOffX, self.BORDER)
            else:
                self.__dragPic = None

    def __DrawHighlights(self, dc):
        dc.SetPen(wx.TRANSPARENT_PEN)
        if self.__selIdx != -1:
            rect = self.GetThumbRect(self.__selIdx)
            col = wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT)
            dc.SetBrush(wx.Brush(wx.Color(col.Red(), col.Green(), col.Blue(), 180)))
            dc.DrawRectangleRect(rect)
        if self.__hvrIdx != -1:
            rect = self.GetThumbRect(self.__hvrIdx)
            col = wx.SystemSettings_GetColour(wx.SYS_COLOUR_HIGHLIGHT)
            color = wx.Color(col.Red(), col.Green(), col.Blue(), 80)
            dc.SetBrush(wx.Brush(color))
            dc.DrawRectangleRect(rect)

    def _SendChangedEvent(self):
        evt = ChangedEvent(self.GetId())
        evt.SetEventObject(self)
        self.GetEventHandler().ProcessEvent(evt)        

    def __Scroll(self, value):
        sp = self.GetScrollPos(wx.HORIZONTAL)
        self.Scroll(sp + value, -1)
    
    def OnMouseWheel(self, event):
        rot = event.GetWheelRotation()
        linesPer = 40 #event.GetLinesPerAction()
        if rot > 0:
            self.__Scroll(-linesPer)
        else:
            self.__Scroll(linesPer)
            
    def OnMouseEvent(self, event):
        mPos = event.GetPosition()
        unscrolledPos = self.CalcUnscrolledPosition(mPos)
        idx = self.HitTest(mPos)
        if event.Moving():
            if idx != self.__hvrIdx:
                self.__hvrIdx = idx
                self.Refresh()
        if event.Dragging():
            if mPos.x < 10:
                self.__Scroll(-40)
            elif mPos.x > self.GetClientSizeTuple()[0] - 10:
                self.__Scroll(40)
            self.__dragX = unscrolledPos.x
            if self.__dragPic is None and idx != -1:
                self.__dragPic = idx
                rect = self.GetThumbRect(idx)
                self.__dragOffX = self.__dragX - rect.GetLeft()
                self.CaptureMouse()
            self.Refresh()
        if event.Leaving():
            self.__hvrIdx = -1
            self.Refresh()
        if event.LeftDown():
            if idx != -1 and idx != self.__selIdx:
                self.Select(idx)
        if event.LeftUp() and self.__dragPic is not None:
            if self.HasCapture():
                self.ReleaseMouse()        
            if idx == -1:
                self.__dragPic = None
                self.Refresh()
            else:
                self.MovePicture(self.__dragPic, idx)
                self.__dragPic = None
                self.Select(idx)
        event.Skip()
        
    def OnCaptureLost(self, event):
        self.__dragPic = None
        self.Refresh()
        event.Skip()
    
    def OnKeyDown(self, event):
        if event.HasModifiers():
            event.Skip()
            return
        
        key = event.GetKeyCode()
        sel = self.GetSelected()
        if key == wx.WXK_LEFT:
            if sel > 0:
                self.Select(sel - 1)
                self.EnsureVisible(sel - 1)
        
        elif key == wx.WXK_RIGHT:
            if sel < self.GetItemCount() - 1:
                self.Select(sel + 1)
                self.EnsureVisible(sel + 1)
        
        elif key == wx.WXK_END:
            self.Select(self.GetItemCount() - 1)
            self.EnsureVisible(self.GetItemCount() - 1)
            
        elif key == wx.WXK_HOME:
            self.Select(0)
            self.EnsureVisible(0)
        
        else:
            event.Skip()

    def EnsureVisible(self, idx):
        rect = self.GetThumbRect(idx)
        left = rect.GetLeft()
        vs = self.GetViewStart()[0]
        ch = self.GetClientSizeTuple()[0]
        if left < vs:
            self.Scroll(left, 0)
        elif left > vs + ch:
            self.Scroll(rect.GetRight() - ch, 0)

    def __UpdateVirtualSize(self):
        width = self.GAP
        for pic in self.__pictures:
            bmp = ImageCache().GetThumbBmp(pic)
            # if the picture cannot be loaded GetWidth may return -1
            width += bmp.GetWidth() + self.GAP
        
        self.SetVirtualSize((width, self.HEIGHT))
        self.Refresh()

    def GetThumbSize(self, pic):
        pw, ph = float(pic.GetWidth()), float(pic.GetHeight())
        thumbHeight = self.HEIGHT - (2 * self.BORDER)
        thumbWidth = int(thumbHeight * (pw / ph))
        return thumbWidth, thumbHeight
    
    def GetThumbRect(self, idx):
        sx = self.GAP
        for picIdx, pic in enumerate(self.__pictures):
            thumbWidth = self.GetThumbSize(pic)[0]
            
            if idx == picIdx:
                rect = wx.Rect(sx, 0, thumbWidth, self.HEIGHT)
                return rect
        
            sx += thumbWidth + self.GAP
            
    def HitTest(self, pos):
        pos = self.CalcUnscrolledPosition(pos)
        sx = self.GAP
        for idx, pic in enumerate(self.__pictures):
            thumbWidth = self.GetThumbSize(pic)[0]
            
            rect = wx.Rect(sx, 0, thumbWidth + self.GAP, self.HEIGHT)
            if rect.Contains(pos):
                return idx
        
            sx += thumbWidth + self.GAP
        return -1
    
#    def AddPicture(self, pic):
#        self.__pictures.append(pic)
#        self.__UpdateVirtualSize()
#        self._SendChangedEvent()
        
    def InsertPicture(self, idx, pic):
        self.__pictures.insert(idx, pic)
        self.__UpdateVirtualSize()
        self._SendChangedEvent()
        
    def DeleteItem(self, idx):
        self.__pictures.pop(idx)
        if self.__selIdx >= len(self.__pictures):
            self.__selIdx = len(self.__pictures) - 1
        self.__UpdateVirtualSize()
        self._SendChangedEvent()
        
    def DeleteAllItems(self):
        self.__selIdx   = -1
        self.__pictures = []
        self.__UpdateVirtualSize()
        self._SendChangedEvent()
        
    def GetItemCount(self):
        return len(self.__pictures)
    
    def GetPicture(self, idx):
        try:
            return self.__pictures[idx]
        except IndexError:
            return None
    def SetPicture(self, idx, pic):
        if idx in xrange(len(self.__pictures)):
            self.__pictures[idx] = pic
            self.Refresh()
            
    def GetPictures(self):
        return self.__pictures[:]
        
    def GetSelected(self):
        return self.__selIdx
    
    def Select(self, idx):
        if idx in xrange(len(self.__pictures)):
            evt = wx.ListEvent(wx.EVT_LIST_ITEM_SELECTED.typeId, self.GetId())
            evt.m_itemIndex = idx
            evt.m_oldItemIndex = self.__selIdx

            self.__selIdx = idx
            self.Refresh()
            
            self.GetEventHandler().ProcessEvent(evt)
            return True
        else:
            return False
        
    def SwapPictures(self, idxFrom, idxTo):
        picFrom = self.__pictures[idxFrom]
        picTo = self.__pictures[idxTo]
        self.__pictures[idxFrom] = picTo
        self.__pictures[idxTo] = picFrom
        self.Refresh()
        self._SendChangedEvent()

    def MovePicture(self, idxFrom, idxTo):
        pic = self.__pictures.pop(idxFrom)
        self.__pictures.insert(idxTo, pic)
        self.Refresh()
        self._SendChangedEvent()


ImageCache.THUMB_SIZE = PhotoFilmStripList.HEIGHT - (2 * PhotoFilmStripList.BORDER)

