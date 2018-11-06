#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2010 Jens Goepfert
#

import sys

from photofilmstrip.AppMixin import AppMixin


class CliApp(AppMixin):

    def _GetLogFormat(self):
        return '\n%(levelname)s: %(message)s'

    def _OnStart(self):
        showHelp = False
        for helpOption in ("-h", "--help"):
            if helpOption in sys.argv:
                showHelp = True
                sys.argv.remove(helpOption)

        from photofilmstrip.cli.Main import main
        return main(showHelp)


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
