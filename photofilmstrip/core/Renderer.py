# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2011 Jens Goepfert
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

import photofilmstrip.core.renderer.SingleFileRenderer as SFR

import photofilmstrip.core.renderer.GStreamerRenderer as GSR

# import photofilmstrip.core.renderer.PyGameRenderer as PGR
# import photofilmstrip.core.renderer.OpenCvRenderer as OCR

import photofilmstrip.core.renderer.CairoRenderer as CR


RENDERERS = [SFR.SingleFileRenderer]

RENDERERS.extend([
        GSR.VCDFormat,
        GSR.SVCDFormat,
        GSR.DVDFormat,
        GSR.OggTheoraVorbis,
        GSR.MkvX264MP3,
        GSR.Mp4X264AAC])

# RENDERERS.extend([
#          OCR.OpenCvRenderer,
#          PGR.PyGameRenderer])

RENDERERS.extend([
             CR.CairoRenderer])
