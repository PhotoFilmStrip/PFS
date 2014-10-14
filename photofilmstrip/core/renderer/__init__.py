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

import sys

from photofilmstrip.core.renderer.MovieRenderer import (
        MPEGRenderer, 
        MPEG4MP3Renderer,
        MPEG4AC3Renderer,
        FlashMovieRenderer, 
        MJPEGRenderer)
from photofilmstrip.core.renderer.SingleFileRenderer import (
        SingleFileRenderer)

# from photofilmstrip.core.renderer.PyGameRenderer import (
#         PyGameRenderer)
from photofilmstrip.core.renderer.CairoRenderer import (
        CairoRenderer)
# from photofilmstrip.core.renderer.OpenCvRenderer import (
#         OpenCvRenderer)
from photofilmstrip.core.renderer.GStreamerRenderer import (
        MkvX264MP3, OggTheoraVorbis)


RENDERERS = [SingleFileRenderer]  
             
if sys.platform == "win32":
    RENDERERS.extend([
             MPEG4MP3Renderer,
             MPEG4AC3Renderer,
             MPEGRenderer,
             FlashMovieRenderer,
             MJPEGRenderer])
else:
    RENDERERS.extend([
             MkvX264MP3,
             OggTheoraVorbis])
             
#     RENDERERS.extend([
#              OpenCvRenderer,
#              PyGameRenderer])
    
RENDERERS.extend([
             CairoRenderer])
