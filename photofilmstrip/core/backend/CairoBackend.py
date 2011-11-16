# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2010 Jens Goepfert
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

import cairo

from photofilmstrip.core.BaseBackend import BaseBackend, BaseCtx
from photofilmstrip.core.backend.PILBackend import PILBackend, PILCtx


class CairoBackend(PILBackend):
    
    def CropAndResize(self, ctx, rect, size, draft=False):
        from photofilmstrip.core.backend.Transformer import Transformer
        cairoImg = Transformer(ctx).ToCairo()

        destWidth, destHeight = size
        cairoDest = cairo.ImageSurface(cairo.FORMAT_RGB24, destWidth, destHeight)

        _ctx = cairo.Context(cairoDest)
        
#        _ctx.save()
    
        x, y, w, h = rect
        _ctx.scale(destWidth / w, destHeight / h)
        _ctx.set_source_surface(cairoImg, -x, -y)            
        _ctx.paint()        
        cairoDest.flush()

        
#        _ctx.restore()
        
        cairoCtx = CairoCtx(cairoDest)
        pilImg = Transformer(cairoCtx).ToPil()
        return PILCtx(pilImg)
    
#    def Transition(self, kind, ctx1, ctx2, percentage):
#        w = ctx1.get_width()
#        h = ctx1.get_height()
#
#        cairoDest = cairo.ImageSurface(cairo.FORMAT_RGB24, w, h)
#        _ctx = cairo.Context(cairoDest)
#        
#        _ctx.set_source_surface(ctx1, 0, 0)
#        _ctx.paint()
#        _ctx.set_source_surface(ctx2, 0, 0)
#        _ctx.paint_with_alpha(percentage)
#        cairoDest.flush()
#        
#        return cairoDest   


class CairoCtx(BaseCtx):
    
    def __init__(self, obj):
        BaseCtx.__init__(self, (obj.get_width(), obj.get_height()), obj)
    
#    def Serialize(self):
#        raise NotImplementedError()
#
#    def Unserialize(self, stream):
#        raise NotImplementedError()

    def ToStream(self, writer, imgFormat):
        pass
