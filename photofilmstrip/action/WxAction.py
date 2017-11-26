# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2011 Jens Goepfert
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

from photofilmstrip.action.WxAbstractAction import WxAbstractAction


class WxAction(WxAbstractAction):

    def __init__(self, name, target, args=None, bmp=None):
        WxAbstractAction.__init__(self)
        self.name = name
        self.target = target
        if args is None:
            args = ()
        self.args = args
        self.bmp = bmp

    def GetName(self):
        return self.name

    def Execute(self):
        return self.target(*self.args)

    def GetBitmap(self, art=None):
        if isinstance(self.bmp, dict):
            return self.bmp.get(art)
        else:
            return self.bmp
