# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2011 Jens Goepfert
#

import photofilmstrip.core.renderer.SingleFileRenderer as SFR

import photofilmstrip.core.renderer.GStreamerRenderer as GSR
import photofilmstrip.core.renderer.CairoRenderer as CR

RENDERERS = [SFR.SingleFileRenderer]

RENDERERS.extend([
        GSR.VCDFormat,
        GSR.SVCDFormat,
        GSR.DVDFormat,
        GSR.OggTheoraVorbis,
        GSR.MkvX264AC3,
        GSR.Mp4X264AAC,
        GSR.MkvX265AC3])

RENDERERS.extend([
             CR.CairoRenderer])
