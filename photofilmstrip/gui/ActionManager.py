# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2017 Jens Goepfert
#

import wx

from photofilmstrip.lib.Settings import Settings
from photofilmstrip.gui.Art import Art
from photofilmstrip.gui.helper import CreateMenuItem


class ActionManager:

    ID_JOB_QUEUE = wx.NewIdRef()
    ID_PROJECT_CLOSE = wx.NewIdRef()
    ID_SLIDESHOW = wx.NewIdRef()
    ID_TIMELAPSE = wx.NewIdRef()
    ID_STORY = wx.NewIdRef()

    ID_LANG_EN = wx.NewIdRef()
    ID_LANG_FR = wx.NewIdRef()
    ID_LANG_DE = wx.NewIdRef()
    ID_LANG_PT_BR = wx.NewIdRef()
    ID_LANG_CS = wx.NewIdRef()
    ID_LANG_IT = wx.NewIdRef()
    ID_LANG_KO = wx.NewIdRef()
    ID_LANG_NL = wx.NewIdRef()
    ID_LANG_RU = wx.NewIdRef()
    ID_LANG_TA = wx.NewIdRef()
    ID_LANG_UK = wx.NewIdRef()
    ID_LANG_EL = wx.NewIdRef()
    ID_LANG_ES = wx.NewIdRef()

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
        ID_LANG_EL: "el",
        ID_LANG_ES: "es"
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
        self._menuBar.Append(menuFile, _("&File"))
        self._menuBar.Append(menuEdit, _("&Edit"))
        self._menuBar.Append(menuHelp, _("&Help"))

        self.__MakeToolBar(toolBar)
        self.__SelectLanguage(Settings().GetLanguage())

    def __SelectLanguage(self, lang):
        for ident, l in self.LANG_MAP.items():
            if l == lang:
                self._menuBar.Check(ident, True)

    def __MakeToolBar(self, toolBar):
        toolBar.AddTool(ActionManager.ID_SLIDESHOW, "",
                        Art.GetBitmapBundle('PFS_PROJECT_NEW', wx.ART_TOOLBAR),
                        kind=wx.ITEM_DROPDOWN,
                        shortHelp=_("New Slideshow"))
        toolBar.Bind(wx.EVT_TOOL_DROPDOWN, self.OnDropDownNew)

        toolBar.AddTool(wx.ID_OPEN, "",
                        Art.GetBitmapBundle('PFS_PROJECT_OPEN', wx.ART_TOOLBAR),
                        _("Open"))

        toolBar.AddTool(wx.ID_SAVE, "",
                        Art.GetBitmapBundle('PFS_PROJECT_SAVE', wx.ART_TOOLBAR),
                        Art.GetBitmapBundle('PFS_PROJECT_SAVE_D', wx.ART_TOOLBAR),
                        wx.ITEM_NORMAL,
                        shortHelp=_("Save"))
#        toolBar.AddSimpleTool(wx.ID_SAVEAS,
#                              Art.GetBitmapBundle('PFS_PROJECT_SAVEAS', wx.ART_MENU),
#                              _("Save Project as"), _("Save Project as"))
        toolBar.AddSeparator()

        toolBar.AddTool(self.ID_JOB_QUEUE, "",
                        Art.GetBitmapBundle('PFS_JOB_QUEUE', wx.ART_TOOLBAR),
                        Art.GetBitmapBundle('PFS_JOB_QUEUE_D', wx.ART_TOOLBAR),
                        wx.ITEM_NORMAL,
                        shortHelp=_("Show job queue"))

        toolBar.AddSeparator()
        self._toolFix = toolBar.GetToolsCount()

        toolBar.Realize()

    def __CreateMenuNew(self):
        menu = wx.Menu()
        CreateMenuItem(menu, ActionManager.ID_SLIDESHOW, _("Slideshow") + "\tCtrl+N",
                       Art.GetBitmapBundle('PFS_PROJECT_NEW', wx.ART_MENU))
        CreateMenuItem(menu, ActionManager.ID_TIMELAPSE, _("Timelapse"),
                       Art.GetBitmapBundle('PFS_PROJECT_NEW', wx.ART_MENU))
        bmp = Art.GetBitmapBundle(wx.ART_LIST_VIEW, wx.ART_MENU)
        CreateMenuItem(menu, ActionManager.ID_STORY, _("Story"), bmp)
        return menu

    def __CreateMenuFile(self, editor=None):
        menu = wx.Menu()
        menu.AppendSubMenu(self.__CreateMenuNew(), _("New"))
        CreateMenuItem(menu, wx.ID_OPEN,
                       _("&Open") + "\tCtrl+O",
                       Art.GetBitmapBundle('PFS_PROJECT_OPEN', wx.ART_MENU))

        menu.AppendSeparator()
        CreateMenuItem(menu, wx.ID_SAVE,
                       _("&Save") + "\tCtrl+S",
                       Art.GetBitmapBundle('PFS_PROJECT_SAVE', wx.ART_MENU),
                       Art.GetBitmapBundle('PFS_PROJECT_SAVE_D', wx.ART_MENU))
#        CreateMenuItem(menu, wx.ID_SAVEAS,
#                       _("Save Project &as"),
#                       Art.GetBitmapBundle('PFS_PROJECT_SAVEAS', wx.ART_MENU))
        menu.AppendSeparator()

        if editor:
            if editor.AddMenuFileActions(menu):
                menu.AppendSeparator()

        CreateMenuItem(menu, ActionManager.ID_PROJECT_CLOSE,
                       _("&Close") + "\tCtrl+W",
                       Art.GetBitmapBundle('PFS_PROJECT_CLOSE', wx.ART_MENU),
                       Art.GetBitmapBundle('PFS_PROJECT_CLOSE_D', wx.ART_MENU))
        menu.AppendSeparator()
        CreateMenuItem(menu, wx.ID_EXIT,
                       _("E&xit") + "\tCtrl+Q",
                       Art.GetBitmapBundle('PFS_EXIT', wx.ART_MENU))
        return menu

    def __CreateMenuEdit(self, editor=None):
        menu = wx.Menu()
        if editor:
            editor.AddMenuEditActions(menu)
        return menu

    def __CreateMenuHelp(self):
        menu = wx.Menu()
        CreateMenuItem(menu, wx.ID_HELP,
                       _("&Help") + "\tF1",
                       Art.GetBitmapBundle('PFS_HELP', wx.ART_MENU))
        menu.AppendSeparator()
        langMenu = wx.Menu()
        langMenu.AppendRadioItem(self.ID_LANG_EN, "English")
        langMenu.AppendRadioItem(self.ID_LANG_FR, "Français")
        langMenu.AppendRadioItem(self.ID_LANG_DE, "Deutsch")
        langMenu.AppendRadioItem(self.ID_LANG_NL, "Nederlands")
        langMenu.AppendRadioItem(self.ID_LANG_PT_BR, "Português (Brasil)")
        langMenu.AppendRadioItem(self.ID_LANG_CS, "Český")
        langMenu.AppendRadioItem(self.ID_LANG_IT, "Italiano")
        langMenu.AppendRadioItem(self.ID_LANG_KO, "한국어")
        langMenu.AppendRadioItem(self.ID_LANG_RU, "русский")
        langMenu.AppendRadioItem(self.ID_LANG_TA, "தமிழ்")
        langMenu.AppendRadioItem(self.ID_LANG_UK, "Український")
        langMenu.AppendRadioItem(self.ID_LANG_EL, "ελληνικά")
        langMenu.AppendRadioItem(self.ID_LANG_ES, "Español")
        menu.AppendSubMenu(langMenu, _("Language"))
        menu.AppendSeparator()
        CreateMenuItem(menu, wx.ID_ABOUT,
                       _("&About"),
                       Art.GetBitmapBundle('PFS_ABOUT', wx.ART_MENU))
        return menu

    def OnDropDownNew(self, event):  # pylint: disable=unused-argument
        menu = self.__CreateMenuNew()
        self._frame.PopupMenu(menu)

    def UpdateActions(self, newEditor):
        while self._toolFix < self._toolBar.GetToolsCount():
            self._toolBar.DeleteToolByPos(self._toolFix)

        if self._prevEditor:
            self._prevEditor.DisconnEvents(self._frame)

        menuFile = self.__CreateMenuFile(newEditor)
        menuEdit = self.__CreateMenuEdit(newEditor)
        self._menuBar.Replace(0, menuFile, _("&File")).Destroy()
        self._menuBar.Replace(1, menuEdit, _("&Edit")).Destroy()

        if newEditor:
            newEditor.AddToolBarActions(self._toolBar)
            newEditor.ConnectEvents(self._frame)
        self._prevEditor = newEditor

        self._toolBar.Realize()
