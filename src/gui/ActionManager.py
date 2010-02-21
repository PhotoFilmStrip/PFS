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

from lib.Settings import Settings


class ActionManager(object):
    
    ID_PIC_MOVE_LEFT     = wx.NewId()
    ID_PIC_MOVE_RIGHT    = wx.NewId()
    ID_PIC_REMOVE        = wx.NewId()
    ID_PIC_ROTATE_CW     = wx.NewId()
    ID_PIC_ROTATE_CCW    = wx.NewId()
    ID_PIC_IMPORT        = wx.NewId()
    ID_RENDER_FILMSTRIP  = wx.NewId()
    ID_PROJECT_IMPORT    = wx.NewId()
    ID_PROJECT_EXPORT    = wx.NewId()

    def __init__(self):
        self.filehistory = wx.FileHistory()
        for filename in Settings().GetFileHistory():
            self.filehistory.AddFileToHistory(filename)
            
        self.__menuBar = None
        self.__toolBar = None
        
    def GetMenuBar(self):
        if self.__menuBar:
            return self.__menuBar
        
        menuBar = wx.MenuBar()
        menuFile = self.__MakeMenuFile()
        menuEdit = self.__MakeMenuEdit()
        menuTools = self.__MakeMenuTools()
        menuHelp = self.__MakeMenuHelp()
        
        menuBar.Append(menuFile, _(u'&File'))
        menuBar.Append(menuEdit, _(u'&Edit'))
        menuBar.Append(menuTools, _(u'&Tools'))
        menuBar.Append(menuHelp, _(u'&Help'))
        
        self.__menuBar = menuBar
        return menuBar
    
    def GetToolBar(self, parent):
        if self.__toolBar:
            return self.__toolBar
        toolBar = wx.ToolBar(parent)
        toolBar.AddSimpleTool(wx.ID_NEW, 
                              wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR, wx.DefaultSize),
                              _(u'New Project'), _(u'New Project'))
        toolBar.AddSimpleTool(wx.ID_OPEN, 
                              wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, wx.DefaultSize),
                              _(u'Load Project'), _(u'Load Project'))
        toolBar.AddSimpleTool(wx.ID_SAVE, 
                              wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_TOOLBAR, wx.DefaultSize),
                              _(u'Save Project'), _(u'Save Project'))
        toolBar.AddSimpleTool(wx.ID_SAVEAS, 
                              wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE_AS, wx.ART_TOOLBAR, wx.DefaultSize),
                              _(u'Save Project as'), _(u'Save Project as'))
        toolBar.AddSeparator()
        toolBar.AddSimpleTool(self.ID_PIC_IMPORT, 
                              wx.ArtProvider.GetBitmap(wx.ART_ADD_BOOKMARK, wx.ART_TOOLBAR, wx.DefaultSize),
                              _(u'Import Pictures'), _(u'Import Pictures'))
        toolBar.AddSimpleTool(self.ID_RENDER_FILMSTRIP, 
                              wx.ArtProvider.GetBitmap(wx.ART_TICK_MARK, wx.ART_TOOLBAR, wx.DefaultSize),
                              _(u'Render filmstrip'), _(u'Render filmstrip'))

        toolBar.Realize()
        
        self.__toolBar = toolBar
        return toolBar

    def __CreateMenuItem(self, menu, ident, text="", bmp=None):
        if text:
            item = wx.MenuItem(menu, ident, text)
            item.SetHelp(text.replace('&', '').split('\t')[0])
        else:
            item = wx.MenuItem(menu, ident)
        if bmp is not None:
            item.SetBitmap(bmp)
        menu.AppendItem(item)
        
    def AddFileToHistory(self, filename):
        self.filehistory.AddFileToHistory(filename)
        
        fileList = Settings().GetFileHistory()
        if filename in fileList:
            fileList.remove(filename)
        fileList.insert(0, filename)
        Settings().SetFileHistory(fileList)
        
    def GetHistoryFile(self, fileNum):
        return self.filehistory.GetHistoryFile(fileNum)
        
    def __MakeMenuFile(self):
        menu = wx.Menu()
        self.__CreateMenuItem(menu, 
                              wx.ID_NEW, 
                              _(u'&New Project') + '\tCtrl+N',
                              wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_MENU, wx.DefaultSize))
        self.__CreateMenuItem(menu, 
                              wx.ID_OPEN, 
                              _(u'&Open Project') + '\tCtrl+O',
                              wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_MENU, wx.DefaultSize))

        fileHistoryMenu = wx.Menu()
        menu.AppendSubMenu(fileHistoryMenu, _(u"Open &recent"))
        self.filehistory.UseMenu(fileHistoryMenu)
        self.filehistory.AddFilesToMenu()
        menu.AppendSeparator()
        self.__CreateMenuItem(menu, wx
                              .ID_SAVE, 
                              _(u'&Save Project') + '\tCtrl+S',
                              wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_MENU, wx.DefaultSize))
        self.__CreateMenuItem(menu, 
                              wx.ID_SAVEAS, 
                              _(u'Save Project &as'),
                              wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE_AS, wx.ART_MENU, wx.DefaultSize))
        menu.AppendSeparator()
        self.__CreateMenuItem(menu, self.ID_PROJECT_IMPORT, _(u"&Import Project"))
        self.__CreateMenuItem(menu, self.ID_PROJECT_EXPORT, _(u"&Export Project"))
        menu.AppendSeparator()
        self.__CreateMenuItem(menu, 
                              wx.ID_EXIT, 
                              _(u'E&xit'),
                              wx.ArtProvider.GetBitmap(wx.ART_QUIT, wx.ART_MENU, wx.DefaultSize))
        return menu

    def __MakeMenuEdit(self):
        menu = wx.Menu()
        self.__CreateMenuItem(menu, 
                              self.ID_PIC_MOVE_LEFT, 
                              _(u'Move picture &left'), 
                              wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_MENU))
        self.__CreateMenuItem(menu, 
                              self.ID_PIC_MOVE_RIGHT, 
                              _(u'Move picture &right'), 
                              wx.ArtProvider.GetBitmap(wx.ART_GO_FORWARD, wx.ART_MENU))
        menu.AppendSeparator()
        self.__CreateMenuItem(menu, 
                              self.ID_PIC_REMOVE, 
                              _(u'&Remove Picture') + '\tCtrl+Del', 
                              wx.ArtProvider.GetBitmap(wx.ART_DELETE, wx.ART_MENU))
        menu.AppendSeparator()
        self.__CreateMenuItem(menu, 
                              self.ID_PIC_ROTATE_CW, 
                              _(u'Rotate &clockwise') + '\tCtrl+r', 
                              wx.ArtProvider.GetBitmap(wx.ART_REDO, wx.ART_MENU))
        self.__CreateMenuItem(menu, 
                              self.ID_PIC_ROTATE_CCW, 
                              _(u'Rotate counter clock&wise') + '\tCtrl+l', 
                              wx.ArtProvider.GetBitmap(wx.ART_UNDO, wx.ART_MENU))
        return menu
        
    def __MakeMenuTools(self):
        menu = wx.Menu()
        self.__CreateMenuItem(menu, 
                              self.ID_PIC_IMPORT, 
                              _(u'&Import Pictures') + '\tCtrl+I', 
                              wx.ArtProvider.GetBitmap(wx.ART_ADD_BOOKMARK, wx.ART_MENU))
        menu.AppendSeparator()
        self.__CreateMenuItem(menu, 
                              self.ID_RENDER_FILMSTRIP, 
                              _(u'&Render filmstrip') + '\tF9', 
                              wx.ArtProvider.GetBitmap(wx.ART_TICK_MARK, wx.ART_MENU))
        return menu
        
    def __MakeMenuHelp(self):
        menu = wx.Menu()
        self.__CreateMenuItem(menu, 
                              wx.ID_HELP, 
                              _(u'&Help') + '\tF1',
                              wx.ArtProvider.GetBitmap(wx.ART_HELP, wx.ART_MENU, wx.DefaultSize))
        menu.AppendSeparator()
        self.__CreateMenuItem(menu, 
                              wx.ID_ABOUT, 
                              _(u'&About'),
                              wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_MENU, wx.DefaultSize))
        return menu
    
    
    def CanSave(self):
        mb = self.GetMenuBar()
        if mb:
            return mb.IsEnabled(wx.ID_SAVE)
        else:
            return False
        
    def OnProjectChanged(self, value):
        mb = self.GetMenuBar()
        if mb:
            mb.Enable(wx.ID_SAVE, value)
            
        tb = self.GetToolBar(None)
        if tb:
            tb.EnableTool(wx.ID_SAVE, value)

    def OnPictureSelected(self, value, kind='any'):
        mb = self.GetMenuBar()
        if mb:
            mb.Enable(self.ID_PIC_MOVE_LEFT, kind not in ['first', 'none'] and value)
            mb.Enable(self.ID_PIC_MOVE_RIGHT, kind not in ['last', 'none'] and value)
            mb.Enable(self.ID_PIC_REMOVE, value)
            mb.Enable(self.ID_PIC_ROTATE_CW, value)
            mb.Enable(self.ID_PIC_ROTATE_CCW, value)

    def OnProjectReady(self, value):
        mb = self.GetMenuBar()
        if mb:
            mb.Enable(self.ID_RENDER_FILMSTRIP, value)
            mb.Enable(wx.ID_SAVEAS, value)
            
        tb = self.GetToolBar(None)
        if tb:
            tb.EnableTool(self.ID_RENDER_FILMSTRIP, value)
        