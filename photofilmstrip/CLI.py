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
from photofilmstrip.AppMixin import AppMixin


class CliApp(AppMixin):
    
    def _GetLogFormat(self):
        return '\n%(levelname)s: %(message)s'
    
    def _OnStart(self):
        from photofilmstrip.cli.Main import main
        return main()



def main():
    cliApp = CliApp()
    
#    import hotshot    
#    prof = hotshot.Profile("pfs.prof")
#    exitCode = prof.runcall(cliApp.Start)
#    prof.close()
    
#    import hotshot.stats
#    stats = hotshot.stats.load("pfs.prof")
#    stats.strip_dirs()
#    stats.sort_stats('time', 'calls')
#    stats.print_stats(50)

    exitCode = cliApp.Start()

    sys.exit(exitCode)


if __name__ == "__main__":
    main()
