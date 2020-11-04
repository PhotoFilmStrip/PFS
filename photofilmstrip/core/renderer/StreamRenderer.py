# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2011 Jens Goepfert
#

import sys

from photofilmstrip.core.renderer.SingleFileRenderer import SingleFileRenderer
from photofilmstrip.core.BaseRenderer import ImageDataFinalizeHandler


class StreamRenderer(SingleFileRenderer):

    def __init__(self):
        SingleFileRenderer.__init__(self)

    @staticmethod
    def GetName():
        return "Stream output"

    @staticmethod
    def GetProperties():
        return SingleFileRenderer.GetProperties() + ["Format"]

    @staticmethod
    def GetDefaultProperty(prop):
        if prop == "Format":
            return "PPM"
        else:
            return SingleFileRenderer.GetDefaultProperty(prop)

    def GetFinalizeHandler(self):
        imgFormat = self.GetProperty("Format")
        if imgFormat in ["JPEG", "PPM"]:
            return ImageDataFinalizeHandler(imgFormat)
        else:
            raise RuntimeError("unsupported format: %s" % imgFormat)

    def ToSink(self, data):
        sys.stdout.buffer.write(data)
