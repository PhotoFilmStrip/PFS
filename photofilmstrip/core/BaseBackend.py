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

class BaseBackend(object):
    
    def __init__(self):
        self._draftMode = False
        
    def EnableDraftMode(self, enable=True):
        self._draftMode = enable
    def IsDraftMode(self):
        return self._draftMode
    
    def CreateCtx(self, pic):
        raise NotImplementedError()
    
    def CropAndResize(self, ctx, rect, size, draft=False):
        raise NotImplementedError()
    
    def Transition(self, kind, ctx1, ctx2, percentage):
        raise NotImplementedError()
    

class BaseCtx(object):
    
    def __init__(self, size, data=None):
        self.size = size
        self.data = data
        
    def GetSize(self):
        return self.size
    
    def GetData(self):
        return self.data
    
    def Serialize(self):
        raise NotImplementedError()

    def Unserialize(self, stream):
        raise NotImplementedError()

    def ToStream(self, writer, imgFormat, *args, **kwargs):
        '''
        Stream this context to a Writer which implements a write method
        @param writer:
        @param format:
        - JPEG
        - PPM
        '''
        raise NotImplementedError()
    
