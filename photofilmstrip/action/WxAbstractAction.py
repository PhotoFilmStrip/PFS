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

from photofilmstrip.action.IAction import IAction


class WxAbstractAction(IAction):
    
    def __init__(self):
        pass
    
    def GetBitmap(self, art=None):
        raise NotImplementedError()

    def ToMenu(self, evtHandler, menu, ident=None):
        if ident is None:
            ident = wx.NewId()
        mitm = wx.MenuItem(menu, ident, self.GetName())
        
        try:
            bmp = self.GetBitmap(wx.ART_MENU)
        except NotImplementedError:
            bmp = None
        
        if bmp:
            mitm.SetBitmap(bmp)
        
        menu.AppendItem(mitm)
        evtHandler.Bind(wx.EVT_MENU, self.__OnExecute, id=ident)
        return mitm
    
    def Bind(self, evtHandler, evt):
        evtHandler.Bind(evt, self.__OnExecute)
        
    def __OnExecute(self, event):
        self.Execute()
        event.Skip()
