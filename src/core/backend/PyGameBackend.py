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

import pygame

from core.BaseBackend import BaseBackend, BaseCtx
from core.Picture import Picture


class PyGameBackend(BaseBackend):
    
    def __init__(self):
        BaseBackend.__init__(self)
    
    def CreateCtx(self, pic):
        ctx = pygame.image.load(pic.GetFilename())
        return PyGameCtx(ctx.get_size(), ctx)

    def CropAndResize(self, ctx, rect, size):
        subCtx = ctx.subsurface(rect)
        sfc = pygame.transform.smoothscale(subCtx, size)
        return sfc
    
    def Transition(self, kind, ctx1, ctx2, percentage):
        if kind == Picture.TRANS_FADE:
            _ctx1 = ctx1.copy()
            ctx2.set_alpha(255 * percentage)
            _ctx1.blit(ctx2, (0, 0))
            return _ctx1
        elif kind == Picture.TRANS_ROLL:
            return ctx1
        

class PyGameCtx(BaseCtx):
    
    def __init__(self, size, obj):
        BaseCtx.__init__(self, size, obj)
    
#    def Serialize(self):
#        raise NotImplementedError()
#
#    def Unserialize(self, stream):
#        raise NotImplementedError()

    def ToStream(self, writer, imgFormat):
        if imgFormat == "JPEG":
            pygame.image.save(self.data, "/tmp/pfs.jpg")
            writer.write(open("/tmp/pfs.jpg", "rb").read())
        else:
            raise RuntimeError("unsupported format")
