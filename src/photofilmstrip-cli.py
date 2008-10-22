#!/usr/bin/python

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


def initLogging():
    import logging
    logging.basicConfig(level=logging.WARNING,
                        format='%(asctime)s (%(levelname)s): %(message)s',
                        datefmt='%d.%m.%Y %H:%M:%S')

def initI18N():
    import os, gettext, locale
    from lib.Settings import Settings
    curLang = locale.getdefaultlocale()[0]
    localeDir = os.path.join(os.path.dirname(__file__), "../locale")
    
    if not os.path.isdir(localeDir):
        gettext.install(Settings.APP_NAME)
        return 

    lang = gettext.translation(Settings.APP_NAME, 
                               localeDir, 
                               languages=[curLang, "en"])
    lang.install(True)


def main():
    initLogging()
    initI18N()
    
    from cli.Main import main
    main()


if __name__ == "__main__":
    main()

