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

        self.SetToolTipString(u'{0}\n{1}'.format(label, descr))

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_MOUSE_EVENTS, self.OnMouseEvents)

        self.SetCursor(wx.StockCursor(wx.CURSOR_HAND))

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

        thumSz = self.bmpThumb.GetSize()
        thumbRect = wx.Rect(sz[0] / 2 - thumSz[0] / 2,
                            sz[1] / 2 - thumSz[1] / 2 - 15,
                            thumSz[0],
                            thumSz[1])

        dc.DrawBitmapPoint(self.bmpThumb, thumbRect.GetTopLeft())
        thumbRect.Inflate(1, 1)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        dc.DrawRectangleRect(thumbRect)

        label, width = self.ChopText(dc, self.label, 138)
        dc.DrawText(label, sz[0] / 2 - width / 2, 97)

    def ChopText(self, dc, text, maxSize):
        """
        Chops the input `text` if its size does not fit in `maxSize`, by cutting the
        text and adding ellipsis at the end.

        :param `dc`: a `wx.DC` device context;
        :param `text`: the text to chop;
        :param `maxSize`: the maximum size in which the text should fit.
        """

        # first check if the text fits with no problems
        width, __ = dc.GetTextExtent(text)

        if width <= maxSize:
            return text, width

        for i in xrange(len(text), -1, -1):
            s = '%s ... %s' % (text[:i * 33 / 100], text[-i * 67 / 100:])

            width, __ = dc.GetTextExtent(s)

            if width <= maxSize:
                break
        return s, width

    def OnClick(self):
        raise NotImplementedError("OnClick")
