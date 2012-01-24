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
        
        for localeDir in (os.path.join(Constants.APP_DIR, "share", "locale"),
                          os.path.join(Constants.APP_DIR, "locale"),):
            if os.path.isdir(localeDir):
                break
        else:
            gettext.install(Constants.APP_NAME)
            return 
    
        try:
            lang = gettext.translation(Constants.APP_NAME, 
                                       localeDir, 
                                       languages=[curLang, "en"])
            lang.install(True)
        except IOError:
            gettext.install(Constants.APP_NAME)
