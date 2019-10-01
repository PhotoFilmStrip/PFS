# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
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

    menu.Append(item)


def ChopText(dc, text, maxSize):
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

    for i in range(len(text), -1, -1):
        s = '%s ... %s' % (text[:i * 33 // 100], text[-i * 67 // 100:])

        width, __ = dc.GetTextExtent(s)

        if width <= maxSize:
            break
    return s, width
