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

import wx

from lib.common.Singleton import Singleton

from core.util import ImageToStream


class ImageCache(Singleton):
    
    SIZE = 400
    THUMB_SIZE = 100
    
    def __init__(self):
        self._wxImgCache = {}
        self._wxBmpCache = {}
        
    def ClearCache(self):
        self._wxImgCache.clear()
        self._wxBmpCache.clear()
    
    def RegisterPicture(self, picture):
        key = self.__GetPicKey(picture)
        if not self._wxImgCache.has_key(key):
            img = picture.GetThumbnail(width=ImageCache.SIZE)
            wxImg = wx.ImageFromStream(ImageToStream(img), wx.BITMAP_TYPE_JPEG)
            self._wxImgCache[key] = wxImg
            
            img = picture.GetThumbnail(height=ImageCache.THUMB_SIZE)
            wxImg = wx.ImageFromStream(ImageToStream(img), wx.BITMAP_TYPE_JPEG)
            self._wxBmpCache[key] = wxImg.ConvertToBitmap()

    def UpdatePicture(self, picture):
        key = self.__GetPicKey(picture)
        if self._wxImgCache.has_key(key):
            del self._wxImgCache[key]
        self.RegisterPicture(picture)
    
    def GetImage(self, picture):
        key = self.__GetPicKey(picture)
        if not self._wxImgCache.has_key(key):
            self.RegisterPicture(picture)
        wxImg  = self._wxImgCache[key]
        return wxImg
    
    def GetThumbBmp(self, picture):
        key = self.__GetPicKey(picture)
        if not self._wxBmpCache.has_key(key):
            self.RegisterPicture(picture)
        wxBmp  = self._wxBmpCache[key]
        return wxBmp
    
    def __GetPicKey(self, picture):
        key = "%s:%s:%s" % (picture.GetFilename(), 
                            picture.GetRotation(), 
                            picture.GetEffect())
        return key
