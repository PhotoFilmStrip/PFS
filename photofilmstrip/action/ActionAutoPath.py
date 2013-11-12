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

import random

from photofilmstrip.action.IAction import IAction

from photofilmstrip.core.Aspect import Aspect
from photofilmstrip.core import PILBackend


class ActionAutoPath(IAction):
    
    def __init__(self, picture, aspect):
        self.__picture = picture
        self.__aspect = aspect
    
    def GetName(self):
        return _(u'Random motion')
    
    def Execute(self):
        ratio = Aspect.ToFloat(self.__aspect)
        width, height = PILBackend.GetImageSize(self.__picture.GetFilename())
        if self.__picture.GetWidth() == -1:
            # FIXME: stupid if
            self.__picture.SetWidth(width)
            self.__picture.SetHeight(height)
 
        if width < height:
            # portrait
            startRect = (0, 0, width, width / ratio)
            targetRect = (0, height - (width / ratio), width, width / ratio)
        else:
            scaledWidth = width * 0.75
            startRect = (0, 0, width, width / ratio)
            d = random.randint(0, 3)
            if d == 0:
                targetRect = (0, 0, scaledWidth, scaledWidth / ratio)
            elif d == 1:
                targetRect = (0, height - (scaledWidth / ratio), scaledWidth, scaledWidth / ratio)
            elif d == 2:
                targetRect = (width - scaledWidth, 0, scaledWidth, scaledWidth / ratio)
            elif d == 3:
                targetRect = (width - scaledWidth, height - (scaledWidth / ratio), scaledWidth, scaledWidth / ratio)

        if random.randint(0, 1):
            targetRect, startRect = startRect, targetRect
            
        print d, width, height, startRect, targetRect

        self.__picture.SetStartRect(startRect)
        self.__picture.SetTargetRect(targetRect)
