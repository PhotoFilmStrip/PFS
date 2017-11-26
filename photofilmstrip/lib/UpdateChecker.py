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

import threading
import urllib
import re


class UpdateChecker(threading.Thread):

    URL = "http://www.photofilmstrip.org/update.txt"

    def __init__(self):
        threading.Thread.__init__(self, name="UpdateCheck")

        self._onlineVersion = None
        self._changes = []
        self._checkDone = False
        self._isOk = False

        self.start()

    def run(self):
        try:
            fd = urllib.urlopen(self.URL)
#            fd = open('/home/jens/Projects/Python/PhotoFilmStrip/res/update.txt', 'r')

            data = fd.read()
        except IOError:
            self._checkDone = True
            return

        lines = data.split('\n')

        ovMatch = re.match(r"(\d+).(\d+).(\d+)?(.+)?", lines.pop(0))
        if ovMatch:
            self._onlineVersion = ".".join(ovMatch.groups()[:3])
        else:
            return

        self._changes = lines

        self._checkDone = True
        self._isOk = True

    def IsDone(self):
        return self._checkDone

    def IsOk(self):
        return self._isOk

    def IsNewer(self, currentVersion):
        if self.IsDone() and self.IsOk():
            curTup = currentVersion.split(".")
            newTup = self._onlineVersion.split(".")
            return newTup > curTup
        return False

    def GetChanges(self):
        return "\n".join(self._changes)

    def GetVersion(self):
        return self._onlineVersion
