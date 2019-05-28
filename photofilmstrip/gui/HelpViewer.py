# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#

import os

from photofilmstrip.lib.util import StartFile, GetDocDir


class HelpViewer:

    ID_INDEX = "index.html"
    ID_CREATE_PFS = "createpfs.html"
    ID_RENDER = "renderpfs.html"

    def __init__(self):
        docDir = GetDocDir("html")
        if docDir is None:
            raise RuntimeError("helpdir not found!")
        self.docDir = os.path.abspath(docDir)

    def DisplayID(self, ident):
        StartFile(os.path.join(self.docDir, ident))

    def Show(self):
        StartFile(os.path.join(self.docDir, self.ID_INDEX))
