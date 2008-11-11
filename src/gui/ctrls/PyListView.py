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

import wx


class PyListView(wx.ListView):
    
    def __init__(self, parent, id, 
                 pos=wx.DefaultPosition, size=wx.DefaultSize, 
                 style=wx.LC_ICON, validator=wx.DefaultValidator, 
                 name=wx.ListCtrlNameStr):
        wx.ListView.__init__(self, parent, id, pos, size, style, validator, name)
        
        self.__data = {}
        self.__key = 0
        
    def DeleteAllItems(self):
        self.__data.clear()
        wx.ListView.DeleteAllItems(self)
        
    def DeleteItem(self, item):
        key = self.GetItemData(item)
        del self.__data[key]
        wx.ListView.DeleteItem(self, item)
        
    def SetPyData(self, item, data):
        key = self.GetItemData(item)
        if key == 0:
            self.__key += 1
            key = self.__key

        self.SetItemData(item, key)
        self.__data[key] = data
        
    def GetPyData(self, item):
        key = self.GetItemData(item)
        return self.__data.get(key)
    
    def GetPyDataList(self):
        result = []
        for item in range(self.GetItemCount()):
            result.append(self.GetPyData(item))
        return result

    def FindItemPyData(self, data):
        for key, pydata in self.__data.items():
            if data is pydata:
                return self.FindItemData(-1, key)
            