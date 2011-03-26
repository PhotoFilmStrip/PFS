# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2009 Jens Goepfert
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

import time
import threading

import wx

from photofilmstrip.lib.common.ObserverPattern import Observable
from photofilmstrip.lib.util import Encode

from photofilmstrip.core.backend.PILBackend import PILBackend

from photofilmstrip.gui.util.ImageCache import ImageCache
     

class ScaleThread(threading.Thread):
    def __init__(self, picture, callbackOnDone):
        threading.Thread.__init__(self, name="reload %s" % Encode(picture.GetFilename()))
        self._picture = picture
        self._abort = False
        self._callbackOnDone = callbackOnDone

    def Abort(self):
        self._abort = True

    def run(self):
        self._abort = False
        for i in range(20):
            time.sleep(0.1)
            if self._abort:
                return
        
        img = self._picture.GetImage()
        wxImg = wx.ImageFromStream(PILBackend.ImageToStream(img), wx.BITMAP_TYPE_JPEG)

        if not self._abort:
            self._callbackOnDone(wxImg)

    
class ImageProxy(Observable):
    
    def __init__(self):
        Observable.__init__(self)
        self._curThread = None
        
        self._picture = None
        self._wxImg = None
        self._wxBmp = None
        self._curSize = -1, -1
    
    def Destroy(self):
        if self._curThread:
            self._curThread.Abort()
            self._curThread.join()
    
    def IsOk(self):
        return self._picture is not None
    
    def OnThreadDone(self, img):
        self._wxImg = img
        wx.CallAfter(self.Notify)

    def SetPicture(self, picture):
        self._picture = picture
        if self._picture is not None:
            self._wxImg = ImageCache().GetImage(picture)
            
            if self._curThread is not None:
                self._curThread.Abort()
                        
            self._curThread = ScaleThread(picture, self.OnThreadDone)
            self._curThread.start()
        
        self.Notify()
        
    def GetWidth(self):
        return self._picture.GetWidth()
    
    def GetHeight(self):
        return self._picture.GetHeight()
    
    def GetSize(self):
        return self.GetWidth(), self.GetHeight()
        
    def Scale(self, width, height):
        img = self._wxImg.Scale(width, height)
        self._wxBmp = img.ConvertToBitmap()
        self._curSize = width, height
    
    def GetCurrentSize(self):
        return self._curSize
    
    def GetBitmap(self):
        return  self._wxBmp
