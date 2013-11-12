# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2013 Jens Goepfert
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

from photofilmstrip.action.IAction import IAction

from photofilmstrip.core.Aspect import Aspect
from photofilmstrip.core import PILBackend


class ActionCenterPath(IAction):
    
    def __init__(self, picture, aspect):
        self.__picture = picture
        self.__aspect = aspect
    
    def GetName(self):
        return _(u'Centralize motion')
    
    def Execute(self):
        ratio = Aspect.ToFloat(self.__aspect)
        width, height = PILBackend.GetImageSize(self.__picture.GetFilename())
        
        picRatio = width / float(height)
        if picRatio > ratio:
            scaledWidth = height * ratio
            scaledHeight = height
        else:
            scaledWidth = width
            scaledHeight = width / ratio

        centerRect = (int(round((width - scaledWidth) /2.0)), 
                      int(round((height - scaledHeight) / 2.0)), 
                      int(round(scaledWidth)), int(round(scaledHeight)))
        self.__picture.SetStartRect(centerRect)
        self.__picture.SetTargetRect(centerRect)
