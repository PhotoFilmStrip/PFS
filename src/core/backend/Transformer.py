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

import array
from core.backend.PILBackend import PILCtx
from core.backend.CairoBackend import CairoCtx
from core.backend.PyGameBackend import PyGameCtx


class Transformer(object):
    
    def __init__(self, backendCtx):
        self.backendCtx = backendCtx
    
    def ToPyGame(self):
        if isinstance(self.backendCtx, PILCtx):
            return self._PilToPyGame()
        elif isinstance(self.backendCtx, PyGameCtx):
            return self.backendCtx.data
        else:
            raise NotImplementedError()

    def _PilToPyGame(self):
        import pygame
        pilImg = self.backendCtx.data
        mode = pilImg.mode
        assert mode in "RGB", "RGBA"
        return pygame.image.fromstring(pilImg.tostring(), pilImg.size, mode)

    def ToCairo(self):
        if isinstance(self.backendCtx, PILCtx):
            return self._PilToCairo()
        elif isinstance(self.backendCtx, CairoCtx):
            return self.backendCtx.data
        else:
            raise NotImplementedError()
    
    def _PilToCairo(self):
        import cairo
        pilImg = self.backendCtx.data.copy()
        w, h = pilImg.size  
        data = pilImg.convert('RGBA').tostring()
        buffer = array.array('B', data)
        cairoImage = cairo.ImageSurface.create_for_data(buffer, cairo.FORMAT_ARGB32, w, h)
#        cairoImage = cairo.ImageSurface.create_for_data(buffer, cairo.FORMAT_RGB24, w, h)
        return cairoImage
    
    def ToPil(self):
        if isinstance(self.backendCtx, CairoCtx):
            return self._CairoToPil()
        else:
            raise NotImplementedError()
        
    def _CairoToPil(self):
        import Image
        cairoImg = self.backendCtx.data
        w = cairoImg.get_width()
        h = cairoImg.get_height()
        data = cairoImg.get_data()
        pilImg = Image.frombuffer('RGB', (w, h), data, "raw", "RGBA", 0, 1).convert('RGBA')
        return pilImg

