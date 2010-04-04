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


class IconLabelLink(wx.Panel):
    
    def __init__(self, 
                 parent, 
                 size=wx.DefaultSize, 
                 label="label",
                 bmp=None,
                 descr="descr"):
        wx.Panel.__init__(self, parent, -1, wx.DefaultPosition, (150, 100), 0, "IconLabelLink")
        self.SetBackgroundColour(parent.GetBackgroundColour())
        stBmp = wx.StaticBitmap(self, -1, bmp)
        self.lbl = wx.StaticText(self, -1, label)
        
        sz = wx.BoxSizer(wx.VERTICAL)
        sz.AddStretchSpacer(1)
        sz.Add(stBmp, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 4)
        sz.Add(self.lbl, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.BOTTOM, 4)
        self.SetSizer(sz)
        
        self.SetToolTipString(descr)
        stBmp.SetToolTipString(descr)
        self.lbl.SetToolTipString(descr)

        self.Layout()
        
        stBmp.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        self.lbl.SetCursor(wx.StockCursor(wx.CURSOR_HAND))
        
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvents)
        stBmp.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvents)
        self.lbl.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvents)
        
        self.fontNormal = self.lbl.GetFont()
        self.fontOver = self.lbl.GetFont()
        self.fontOver.SetUnderlined(True)
        
    def OnMouseEvents(self, event):
        if event.LeftDown():
            self.OnClick()
        if event.Leaving():
            self.lbl.SetFont(self.fontNormal)
            self.lbl.SetForegroundColour(wx.BLACK)
            self.lbl.Refresh()
        if event.Moving():
            self.lbl.SetFont(self.fontOver)
            self.lbl.SetForegroundColour(wx.BLUE)
            self.lbl.Refresh()
        event.Skip()

    def OnClick(self):
        raise NotImplementedError("OnClick")
