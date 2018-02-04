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

import os
import sys

from photofilmstrip.lib.util import StartFile


class HelpViewer:

    ID_INDEX = "index.html"
    ID_CREATE_PFS = "createpfs.html"
    ID_RENDER = "renderpfs.html"

    def __init__(self):
        basedir = os.path.dirname(os.path.abspath(sys.argv[0]))
        docDir = None
        for docDir in (os.path.join("..", "share", "doc", "photofilmstrip", "html"),
                        os.path.join("..", "build", "sphinx", "html")):
            docDir = os.path.join(basedir, docDir)
            if os.path.isdir(docDir):
                break
        else:
            raise RuntimeError("helpdir not found!")
        self.docDir = os.path.abspath(docDir)

    def DisplayID(self, ident):
        StartFile(os.path.join(self.docDir, ident))

    def Show(self):
        StartFile(os.path.join(self.docDir, self.ID_INDEX))
