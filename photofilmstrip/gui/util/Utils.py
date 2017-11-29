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

    for i in xrange(len(text), -1, -1):
        s = '%s ... %s' % (text[:i * 33 / 100], text[-i * 67 / 100:])

        width, __ = dc.GetTextExtent(s)

        if width <= maxSize:
            break
    return s, width
