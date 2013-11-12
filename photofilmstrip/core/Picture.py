# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
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

import logging

from photofilmstrip.lib.common.ObserverPattern import Observable


class Picture(Observable):
    
    EFFECT_NONE        = 0
    EFFECT_BLACK_WHITE = 1
    EFFECT_SEPIA       = 2
    
    TRANS_NONE = 0
    TRANS_FADE = 1
    TRANS_ROLL = 2
    
    MOVE_LINEAR  = 0
    MOVE_ACCEL   = 1
    MOVE_DELAYED = 2
    
    def __init__(self, filename):
        Observable.__init__(self)
        self._filename   = filename
        self._startRect  = (0, 0, 1280, 720)
        self._targetRect = (0, 0, 1280, 720)
        self._isDummy    = False
        
        self._duration = 7.0
        self._movement = Picture.MOVE_ACCEL
        self._rotation = 0
        self._comment  = u""
        self._effect   = Picture.EFFECT_NONE
        self._width    = -1
        self._height   = -1
        
        self._trans    = Picture.TRANS_FADE
        self._transDur = 1.0
        
    def Copy(self):
        clone = Picture(self._filename)
        clone.SetStartRect(self._startRect[:])
        clone.SetTargetRect(self._targetRect[:])
        clone.SetDummy(self._isDummy)
        clone.SetDuration(self._duration)
        clone.SetRotation(self._rotation)
        clone.SetComment(self._comment)
        clone.SetEffect(self._effect)
        clone.SetWidth(self._width)
        clone.SetHeight(self._height)
        clone.SetTransition(self._trans)
        clone.SetTransitionDuration(self._transDur)
        return clone
        
    def GetFilename(self):
        return self._filename
    
    def SetStartRect(self, rect):
        if rect == self._startRect or self._isDummy:
            return
        self._startRect = rect
        self.Notify("start")
    def GetStartRect(self):
        return self._startRect
        
    def SetTargetRect(self, rect):
        if rect == self._targetRect or self._isDummy:
            return
        self._targetRect = rect
        self.Notify("target")
    def GetTargetRect(self):
        return self._targetRect
    
    def SetDummy(self, isDummy):
        self._isDummy = isDummy
    def IsDummy(self):
        return self._isDummy
    
    def SetDuration(self, duration):
        if duration == self._duration:
            return
        self._duration = duration
        self.Notify("duration")
    def GetDuration(self):
        return self._duration
    
    def SetMovement(self, movement):
        if movement == self._movement:
            return
        self._movement = movement
        self.Notify("movement")
    def GetMovement(self):
        return self._movement
    
    def SetComment(self, comment):
        if comment == self._comment:
            return
        self._comment = comment
        self.Notify('comment')
    def GetComment(self):
        return self._comment
    
    def SetEffect(self, effect):
        if effect == self._effect:
            return
        self._effect = effect
        self.Notify('effect')
        self.Notify("bitmap")
    def GetEffect(self):
        return self._effect

    def SetRotation(self, rotation):
        for i in range(abs(rotation)):
            self.__Rotate(rotation > 0)
        self.Notify("rotation")
    def GetRotation(self):
        return self._rotation
    
    def SetWidth(self, width):
        self._width = width
    def GetWidth(self):
        if self._width == -1:
            logging.debug("width not set yet!")
        return self._width
    
    def SetHeight(self, height):
        self._height = height
    def GetHeight(self):
        if self._height == -1:
            logging.debug("height not set yet!")
        return self._height
    
    def SetTransition(self, transition):
        if transition == self._trans:
            return
        self._trans = transition
        self.Notify('transition')
        self.Notify('duration') # if set to no transition
    def GetTransition(self):
        return self._trans
    
    def SetTransitionDuration(self, transDur):
        if transDur == self._transDur:
            return
        self._transDur = transDur
        self.Notify('duration')
    def GetTransitionDuration(self, rawValue=False):
        if not rawValue and self._trans == Picture.TRANS_NONE:
            return 0.0
        return self._transDur
    
    def __Rotate(self, clockwise=True):
        if clockwise:
            self._rotation += 1
        else:
            self._rotation -= 1
        if self._rotation > 3:
            self._rotation = 0
        if self._rotation < -3:
            self._rotation = 0

        self._width, self._height = self._height, self._width
    
    def Rotate(self, clockwise=True):
        self.__Rotate(clockwise)
        self.Notify("bitmap")
        
    def GetKey(self):
        key = "%s:%s:%s" % (self.GetFilename(), 
                            self.GetRotation(), 
                            self.GetEffect())
        return key
