# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
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
        for docDir in (os.path.join("..", "share", "doc", "photofilmstrip", "html"),  # linux
                       os.path.join("share", "doc", "photofilmstrip", "html"),  # win
                       os.path.join("..", "build", "sphinx", "html")):  # source
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
