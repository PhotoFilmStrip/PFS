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

import logging
import os
import subprocess


def IsPathWritable(path):
    _path = path
    try:
        fd = open(os.path.join(_path, 'test'), 'w')
        fd.write(" ")
        fd.close()
        os.remove(os.path.join(_path, 'test'))
        return True
    except Exception as err:
        logging.debug("IsPathWritable(%s): %s", path, err)
        return False


def CheckFile(filename):
    if filename and not os.path.exists(filename):
        return False
    else:
        return True


def StartFile(filename):
    if os.name == "nt":
        try:
            os.startfile(filename)  # pylint: disable=no-member
        except:
            pass
    else:
        subprocess.Popen(["xdg-open", filename])
