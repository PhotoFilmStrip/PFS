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

from lib.common.ObserverPattern import Observable


class ProgressHandler(Observable):
    
    def __init__(self):
        Observable.__init__(self)
        
        self.__maxProgress = 100
        self.__currProgress = 0
        self.__info = _(u"Please wait...")
        self.__isAborted = False
    
    def GetMaxProgress(self):
        return self.__maxProgress
    def SetMaxProgress(self, mp):
        self.__maxProgress = mp
        self.Notify('maxProgress')
        
    def GetCurrentProgress(self):
        return self.__currProgress
    def SetCurrentProgress(self, cp):
        self.__currProgress = cp
        self.Notify('currentProgress')
        
    def GetInfo(self):
        return self.__info    
    def SetInfo(self, info):
        if self.__isAborted:
            return
        self.__info = info
        self.Notify('info')
    
    def Step(self, info=""):
        self.__currProgress += 1
        self.Notify('currentProgress')
        if info and not self.__isAborted:
            self.__info = info
            self.Notify('info')
        
    def Done(self):
        self.__currProgress = self.__maxProgress
        self.Notify('currentProgress')
        self.Notify('done')

    def Abort(self):
        self.__isAborted = True
        self.__info = _(u"aborting...")
        self.Notify('aborting')
        
    def IsAborted(self):
        return self.__isAborted
