# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2011 Jens Goepfert
#

import gettext
import os

from photofilmstrip.action.IAction import IAction

from photofilmstrip import Constants

from photofilmstrip.lib.Settings import Settings


class ActionI18N(IAction):

    def __init__(self, lang=None):
        self.__lang = lang

    def GetName(self):
        return _("Language")

    def Execute(self):
        curLang = Settings().GetLanguage()

        localeDir = None
        for localeDir in (os.path.join(Constants.APP_DIR, "share", "locale"),
                          os.path.join(Constants.APP_DIR, "locale"),):
            if os.path.isdir(localeDir):
                break

        if localeDir is None:
            gettext.install(Constants.APP_NAME)
            return

        try:
            lang = gettext.translation(Constants.APP_NAME,
                                       localeDir,
                                       languages=[curLang, "en"])
            lang.install(True)
        except IOError:
            gettext.install(Constants.APP_NAME)
