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


class Aspect:

    ASPECT_4_3 = "4:3"
    ASPECT_3_2 = "3:2"
    ASPECT_16_9 = "16:9"

    @classmethod
    def ToFloat(cls, aspect):
        if aspect == cls.ASPECT_16_9:
            return 16.0 / 9.0
        if aspect == cls.ASPECT_4_3:
            return 4.0 / 3.0
        if aspect == cls.ASPECT_3_2:
            return 3.0 / 2.0
