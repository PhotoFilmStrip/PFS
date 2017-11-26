# encoding: UTF-8
#
# Copyright (C) 2017 Jens Goepfert
#

import wx


def CreateMenuItem(menu, ident, text="", bmp=None, disabledBitmap=None):
    if text:
        item = wx.MenuItem(menu, ident, text)
        item.SetHelp(text.replace('&', '').split('\t')[0])
    else:
        item = wx.MenuItem(menu, ident)
    if bmp is not None:
        item.SetBitmap(bmp)

    if disabledBitmap is not None:
        item.SetDisabledBitmap(disabledBitmap)

    menu.AppendItem(item)
