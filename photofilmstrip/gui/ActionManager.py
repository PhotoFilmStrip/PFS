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

import wx


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
    ID_PROJECT_PROPS     = wx.NewId()
    ID_PROJECT_CLOSE     = wx.NewId()
    ID_LANG_EN           = wx.NewId()
    ID_LANG_FR           = wx.NewId()
    ID_LANG_DE           = wx.NewId()
    ID_LANG_PT_BR        = wx.NewId()
    ID_LANG_CS           = wx.NewId()
    ID_LANG_IT           = wx.NewId()
    ID_LANG_KO           = wx.NewId()
    ID_LANG_NL           = wx.NewId()
    ID_LANG_RU           = wx.NewId()
    ID_LANG_TA           = wx.NewId()
    ID_LANG_UK           = wx.NewId()

    LANG_MAP = {ID_LANG_EN: "en",
                ID_LANG_FR: "fr",
                ID_LANG_DE: "de",
                ID_LANG_CS: "cs",
                ID_LANG_IT: "it",
                ID_LANG_KO: "ko",
                ID_LANG_NL: "nl",
                ID_LANG_RU: "ru",
                ID_LANG_PT_BR: "pt_BR",
                ID_LANG_TA: "ta",
                ID_LANG_UK: "uk"}

    def __init__(self):
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
        if parent is None:
            return
        
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
#        toolBar.AddSimpleTool(wx.ID_SAVEAS, 
#                              wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE_AS, wx.ART_TOOLBAR, wx.DefaultSize),
#                              _(u'Save Project as'), _(u'Save Project as'))
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

        menu.AppendSeparator()
        self.__CreateMenuItem(menu, 
                              wx.ID_SAVE, 
                              _(u'&Save Project') + '\tCtrl+S',
                              wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE, wx.ART_MENU, wx.DefaultSize))
        self.__CreateMenuItem(menu, 
                              self.ID_PROJECT_CLOSE, 
                              _(u'&Close Project') + '\tCtrl+W',
                              wx.ArtProvider.GetBitmap(wx.ART_REMOVABLE, wx.ART_MENU, wx.DefaultSize))
#        self.__CreateMenuItem(menu, 
#                              wx.ID_SAVEAS, 
#                              _(u'Save Project &as'),
#                              wx.ArtProvider.GetBitmap(wx.ART_FILE_SAVE_AS, wx.ART_MENU, wx.DefaultSize))
        menu.AppendSeparator()
#        self.__CreateMenuItem(menu, self.ID_PROJECT_IMPORT, _(u"&Import Project"))
#        self.__CreateMenuItem(menu, self.ID_PROJECT_EXPORT, _(u"&Export Project"))
#        menu.AppendSeparator()
        self.__CreateMenuItem(menu, 
                              self.ID_PROJECT_PROPS, 
                              _("&Properties"), 
                              wx.ArtProvider_GetBitmap(wx.ART_EXECUTABLE_FILE, wx.ART_MENU, wx.DefaultSize))
        menu.AppendSeparator()
        self.__CreateMenuItem(menu, 
                              wx.ID_EXIT, 
                              _(u'E&xit') + '\tCtrl+Q',
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
        langMenu = wx.Menu()
        langMenu.AppendRadioItem(self.ID_LANG_EN, u"English")
        langMenu.AppendRadioItem(self.ID_LANG_FR, u"Français")
        langMenu.AppendRadioItem(self.ID_LANG_DE, u"Deutsch")
        langMenu.AppendRadioItem(self.ID_LANG_NL, u"Nederlands")
        langMenu.AppendRadioItem(self.ID_LANG_PT_BR, u"Português (Brasil)")
        langMenu.AppendRadioItem(self.ID_LANG_CS, u"Český")
        langMenu.AppendRadioItem(self.ID_LANG_IT, u"Italiano")
        langMenu.AppendRadioItem(self.ID_LANG_KO, u"한국어")
        langMenu.AppendRadioItem(self.ID_LANG_RU, u"русский")
        langMenu.AppendRadioItem(self.ID_LANG_TA, u"தமிழ்")
        langMenu.AppendRadioItem(self.ID_LANG_UK, u"Український")
        menu.AppendMenu(wx.NewId(), _("Language"), langMenu)
        menu.AppendSeparator()
        self.__CreateMenuItem(menu, 
                              wx.ID_ABOUT, 
                              _(u'&About'),
                              wx.ArtProvider.GetBitmap(wx.ART_INFORMATION, wx.ART_MENU, wx.DefaultSize))
        return menu

    def SelectLanguage(self, lang):
        for ident, l in self.LANG_MAP.items():
            if l == lang:
                self.GetMenuBar().Check(ident, True)
                