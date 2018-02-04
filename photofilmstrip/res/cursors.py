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

DATA = [[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2],
        [2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 0, 2, 0, 0, 0, 0],
        [2, 2, 2, 2, 2, 2, 2, 2, 0, 1, 0, 2, 0, 1, 1, 0],
        [2, 2, 2, 2, 2, 2, 2, 0, 1, 1, 0, 2, 0, 1, 1, 0],
        [2, 2, 2, 2, 2, 2, 0, 1, 1, 1, 0, 2, 0, 1, 1, 0],
        [2, 2, 2, 2, 2, 0, 1, 1, 1, 1, 0, 2, 0, 1, 1, 0],
        [2, 2, 2, 2, 0, 1, 1, 1, 1, 1, 0, 2, 0, 1, 1, 0],
        [2, 2, 2, 0, 1, 1, 1, 1, 1, 1, 0, 2, 0, 1, 1, 0],
        [2, 2, 0, 1, 1, 1, 1, 1, 1, 1, 0, 2, 0, 1, 1, 0],
        [2, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 2, 0, 1, 1, 0],
        [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 1, 1, 0],
        [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 0, 1, 1, 0],
        [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
        [2, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [2, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]]

__CURSORS = {}


def __MakeCursor(data):
    img = wx.Image(16, 16)
    img.SetMaskColour(255, 0, 0)
    for px in range(len(data)):
        for py in range(len(data[px])):
            val = data[px][py]
            if val == 2:
                img.SetRGB(px, py, 255, 0, 0)
            elif val == 1:
                img.SetRGB(px, py, 0, 0, 0)
            elif val == 0:
                img.SetRGB(px, py, 255, 255, 255)
    img.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_X, 8)
    img.SetOption(wx.IMAGE_OPTION_CUR_HOTSPOT_Y, 8)
    return wx.Cursor(img)


def GetNW():
    if 'NW' in __CURSORS:
        return __CURSORS['NW']

    result = []
    for line in DATA:
        tmp = []
        for value in line:
            tmp.insert(0, value)
        result.insert(0, tmp)
    cursor = __MakeCursor(result)
    __CURSORS['NW'] = cursor
    return cursor


def GetSE():
    if 'SE' in __CURSORS:
        return __CURSORS['SE']

    cursor = __MakeCursor(DATA)
    __CURSORS['SE'] = cursor
    return cursor


def GetSW():
    if 'SW' in __CURSORS:
        return __CURSORS['SW']

    result = []
    for line in DATA:
        tmp = []
        for value in line:
            tmp.append(value)
        result.insert(0, tmp)
    cursor = __MakeCursor(result)
    __CURSORS['SW'] = cursor
    return cursor


def GetNE():
    if 'NE' in __CURSORS:
        return __CURSORS['NE']

    result = []
    for line in DATA:
        tmp = []
        for value in line:
            tmp.insert(0, value)
        result.append(tmp)
    cursor = __MakeCursor(result)
    __CURSORS['NE'] = cursor
    return cursor

