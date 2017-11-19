# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2017 Jens Goepfert
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
import re


class PicturePattern(object):

    @staticmethod
    def Create(path):
        result = None
        getnum = re.compile(r"(.*?)(\d+)([.].*)")
        match = getnum.match(os.path.basename(path))
        if match is None:
            result = PicturePattern()
        else:
            prefix = match.groups()[0]
            num = int(match.groups()[1])
            postfix = match.groups()[2]
            digits = len(match.groups()[1])
            result = PicturePattern(prefix, num, postfix, digits)
        return result

    def __init__(self, prefix=None, num=None, postfix=None, digits=None):
        self.prefix = prefix
        self.num = num
        self.postfix = postfix
        self.digits = digits

    def IsOk(self):
        return self.num is not None

