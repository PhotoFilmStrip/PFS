#!/usr/bin/python
# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2010 Jens Goepfert
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

import sys


def initLogging():
    import logging
    from lib.Settings import Settings
    logging.basicConfig(level=logging.WARNING,
                        format='\n%(levelname)s: %(message)s',
                        datefmt='')

def initI18N():
    from lib.Settings import Settings
    Settings().InitLanguage()


def main():
    initLogging()
    initI18N()
    
    from cli.Main import main
    return main()



if __name__ == "__main__":
#    import hotshot    
#    prof = hotshot.Profile("pfs.prof")
#    exitCode = prof.runcall(main)
#    prof.close()
    
#    import hotshot.stats
#    stats = hotshot.stats.load("pfs.prof")
#    stats.strip_dirs()
#    stats.sort_stats('time', 'calls')
#    stats.print_stats(50)

    exitCode = main()

    sys.exit(exitCode)
