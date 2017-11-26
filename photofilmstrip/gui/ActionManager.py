# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2017 Jens Goepfert
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

from photofilmstrip.lib.Settings import Settings
from photofilmstrip.gui.helper import CreateMenuItem


class ActionManager(object):

    ID_JOB_QUEUE = wx.NewId()
    ID_PROJECT_CLOSE = wx.NewId()

    ID_LANG_EN = wx.NewId()
    ID_LANG_FR = wx.NewId()
    ID_LANG_DE = wx.NewId()
    ID_LANG_PT_BR = wx.NewId()
    ID_LANG_CS = wx.NewId()
    ID_LANG_IT = wx.NewId()
    ID_LANG_KO = wx.NewId()
    ID_LANG_NL = wx.NewId()
    ID_LANG_RU = wx.NewId()
    ID_LANG_TA = wx.NewId()
    ID_LANG_UK = wx.NewId()
    ID_LANG_EL = wx.NewId()

    LANG_MAP = {
        ID_LANG_EN: "en",
        ID_LANG_FR: "fr",
        ID_LANG_DE: "de",
        ID_LANG_CS: "cs",
        ID_LANG_IT: "it",
        ID_LANG_KO: "ko",
        ID_LANG_NL: "nl",
        ID_LANG_RU: "ru",
        ID_LANG_PT_BR: "pt_BR",
        ID_LANG_TA: "ta",
        ID_LANG_UK: "uk",
        ID_LANG_EL: "el"
    }

    def __init__(self, frame, menuBar, toolBar):
        self._frame = frame
        self._menuBar = menuBar
        self._toolBar = toolBar

        self._prevEditor = None
        self._toolFix = 0

        menuFile = self.__CreateMenuFile()
        menuEdit = self.__CreateMenuEdit()
        menuHelp = self.__CreateMenuHelp()
        self._menuBar.Append(menuFile, _(u'&File'))
        self._menuBar.Append(menuEdit, _(u'&Edit'))
        self._menuBar.Append(menuHelp, _(u'&Help'))

        self.__MakeToolBar(toolBar)
        self.__SelectLanguage(Settings().GetLanguage())

    def __SelectLanguage(self, lang):
        for ident, l in self.LANG_MAP.items():
            if l == lang:
                self._menuBar.Check(ident, True)

    def __MakeToolBar(self, toolBar):
        toolBar.DoAddTool(wx.ID_NEW, _(u'New Slideshow'),
                          wx.ArtProvider.GetBitmap('PFS_PROJECT_NEW_24'),
                          kind=wx.ITEM_DROPDOWN,
                          shortHelp=_(u'New Slideshow'))
        toolBar.Bind(wx.EVT_TOOL_DROPDOWN, self.OnDropDownNew)

        toolBar.AddSimpleTool(wx.ID_OPEN,
                              wx.ArtProvider.GetBitmap('PFS_PROJECT_OPEN_24'),
                              _(u'Load'), _(u'Load'))

        toolBar.DoAddTool(wx.ID_SAVE, '',
                             wx.ArtProvider.GetBitmap('PFS_PROJECT_SAVE_24'),
                             wx.ArtProvider.GetBitmap('PFS_PROJECT_SAVE_D_24'),
                             wx.ITEM_NORMAL,
                             _(u'Save'), _(u'Save'), None)
#        toolBar.AddSimpleTool(wx.ID_SAVEAS,
#                              wx.ArtProvider.GetBitmap('PFS_PROJECT_SAVEAS_16'),
#                              _(u'Save Project as'), _(u'Save Project as'))
        toolBar.AddSeparator()

        toolBar.DoAddTool(self.ID_JOB_QUEUE, '',
                          wx.ArtProvider.GetBitmap('PFS_JOB_QUEUE_24'),
                          wx.ArtProvider.GetBitmap('PFS_JOB_QUEUE_D_24'),
                          wx.ITEM_NORMAL,
                          _(u'Show job queue'),
                          _(u'Show job queue'),
                          None)

        toolBar.AddSeparator()
        self._toolFix = toolBar.GetToolsCount()

        toolBar.Realize()

    def __CreateMenuNew(self):
        menu = wx.Menu()
        CreateMenuItem(menu, wx.ID_NEW, _(u'Slideshow') + '\tCtrl+N',
                       wx.ArtProvider.GetBitmap('PFS_PROJECT_NEW_24'))
        return menu

    def __CreateMenuFile(self, editor=None):
        menu = wx.Menu()
        menu.AppendMenu(wx.ID_ANY, _(u'New'), self.__CreateMenuNew())
        CreateMenuItem(menu, wx.ID_OPEN,
                       _(u'&Open') + '\tCtrl+O',
                       wx.ArtProvider.GetBitmap('PFS_PROJECT_OPEN_24'))

        menu.AppendSeparator()
        CreateMenuItem(menu, wx.ID_SAVE,
                       _(u'&Save') + '\tCtrl+S',
                       wx.ArtProvider.GetBitmap('PFS_PROJECT_SAVE_16'),
                       wx.ArtProvider.GetBitmap('PFS_PROJECT_SAVE_D_16'))
#        CreateMenuItem(menu, wx.ID_SAVEAS,
#                       _(u'Save Project &as'),
#                       wx.ArtProvider.GetBitmap('PFS_PROJECT_SAVEAS_16'))
        menu.AppendSeparator()

        if editor:
            editor.AddMenuFileActions(menu)
            menu.AppendSeparator()

        CreateMenuItem(menu, ActionManager.ID_PROJECT_CLOSE,
                       _(u'&Close') + '\tCtrl+W',
                       wx.ArtProvider.GetBitmap('PFS_PROJECT_CLOSE_16'),
                       wx.ArtProvider.GetBitmap('PFS_PROJECT_CLOSE_D_16'))
        menu.AppendSeparator()
        CreateMenuItem(menu, wx.ID_EXIT,
                       _(u'E&xit') + '\tCtrl+Q',
                       wx.ArtProvider.GetBitmap('PFS_EXIT_16'))
        return menu

    def __CreateMenuEdit(self, editor=None):
        menu = wx.Menu()
        if editor:
            editor.AddMenuEditActions(menu)
        return menu

    def __CreateMenuHelp(self):
        menu = wx.Menu()
        CreateMenuItem(menu, wx.ID_HELP,
                       _(u'&Help') + '\tF1',
                       wx.ArtProvider.GetBitmap('PFS_HELP_16'))
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
        langMenu.AppendRadioItem(self.ID_LANG_EL, u"ελληνικά")
        menu.AppendMenu(wx.NewId(), _("Language"), langMenu)
        menu.AppendSeparator()
        CreateMenuItem(menu, wx.ID_ABOUT,
                       _(u'&About'),
                       wx.ArtProvider.GetBitmap('PFS_ABOUT_16'))
        return menu

    def OnDropDownNew(self, event):
        menu = self.__CreateMenuNew()
        self._frame.PopupMenu(menu)

    def UpdateActions(self, newEditor):
        while self._toolFix < self._toolBar.GetToolsCount():
            self._toolBar.DeleteToolByPos(self._toolFix)

        if self._prevEditor:
            self._prevEditor.DisconnEvents(self._frame)

        menuFile = self.__CreateMenuFile(newEditor)
        menuEdit = self.__CreateMenuEdit(newEditor)
        self._menuBar.Replace(0, menuFile, _(u'&File')).Destroy()
        self._menuBar.Replace(1, menuEdit, _(u'&Edit')).Destroy()

        if newEditor:
            newEditor.AddToolBarActions(self._toolBar)
            newEditor.ConnectEvents(self._frame)
        self._prevEditor = newEditor

        self._toolBar.Realize()
