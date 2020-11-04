# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2011 Jens Goepfert
#

import os

from photofilmstrip.core.BaseRenderer import BaseRenderer


class SingleFileRenderer(BaseRenderer):

    def __init__(self):
        BaseRenderer.__init__(self)
        self._counter = 0

    @staticmethod
    def GetName():
        return _("Single pictures")

    @staticmethod
    def GetProperties():
        return ["ResampleFilter"]

    @staticmethod
    def GetDefaultProperty(prop):
        if prop == "ResampleFilter":
            return "Antialias"
        else:
            return BaseRenderer.GetDefaultProperty(prop)

    def Prepare(self):
        pass

    def ToSink(self, data):
        self._counter += 1

        outputPath = os.path.dirname(self._outFile)
        newFilename = os.path.join(outputPath,
                                   '%09d.%s' % (self._counter,
                                                "jpg"))
        with open(newFilename, "wb") as fd:
            fd.write(data)

    def Finalize(self):
        pass

    def ProcessAbort(self):
        pass
