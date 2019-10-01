# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2010 Jens Goepfert
#

import wx

from photofilmstrip.gui.helper import ChopText


class IconLabelLink(wx.Panel):

    def __init__(self,
                 parent,
                 size=wx.DefaultSize,
                 label="label",
                 bmp=None,
                 descr="descr"):
        wx.Panel.__init__(self, parent, -1, wx.DefaultPosition, (150, 150), 0, "IconLabelLink")
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)

        self.bmpDia = wx.ArtProvider.GetBitmap('PFS_DIA')
        self.bmpDiaSelected = wx.ArtProvider.GetBitmap('PFS_DIA_S')
        self.bmpThumb = bmp
        self.label = label
        self.mouseOver = False

        self.SetToolTip(u'{0}\n{1}'.format(label, descr))

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvents)

        self.SetCursor(wx.Cursor(wx.CURSOR_HAND))

    def OnMouseEvents(self, event):
        if event.LeftDown():
            self.OnClick()

        if event.Entering():
            self.mouseOver = True
            self.Refresh()

        if event.Leaving():
            self.mouseOver = False
            self.Refresh()

        # event.Skip()

    def OnPaint(self, event):  # pylint: disable=unused-argument
        dc = wx.AutoBufferedPaintDC(self)
        dc.SetBackground(wx.Brush(self.GetParent().GetBackgroundColour()))
        sz = self.GetSize()
        dc.Clear()

        if self.mouseOver:
            dc.DrawBitmap(self.bmpDiaSelected, 0, 0)
        else:
            dc.DrawBitmap(self.bmpDia, 0, 0)

        thumbSz = self.bmpThumb.GetSize()
        thumbRect = wx.Rect(sz[0] // 2 - thumbSz[0] // 2,
                            sz[1] // 2 - thumbSz[1] // 2 - 15,
                            thumbSz[0],
                            thumbSz[1])

        dc.DrawBitmap(self.bmpThumb, thumbRect.GetTopLeft())
        thumbRect.Inflate(1, 1)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangle(thumbRect)

        label, width = ChopText(dc, self.label, 138)
        dc.DrawText(label, sz[0] // 2 - width // 2, 97)

    def OnClick(self):
        raise NotImplementedError("OnClick")
