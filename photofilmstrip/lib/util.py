# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#

import logging
import os
import subprocess

FILE_EXTENSIONS_AUDIO = (".mp3", ".wav", ".flac", ".ogg", ".oga")
FILE_EXTENSIONS_VIDEO = (".avi", ".flv", ".mp4", ".mkv", ".ogg", ".ogv",
                         ".mts", ".mov", ".mpg", ".m4v")


def IsPathWritable(path):
    _path = path
    try:
        fd = open(os.path.join(_path, 'test'), 'w')
        fd.write(" ")
        fd.close()
        os.remove(os.path.join(_path, 'test'))
        return True
    except Exception as err:
        logging.debug("IsPathWritable(%s): %s", path, err)
        return False


def CheckFile(filename):
    if filename and not os.path.exists(filename):
        return False
    else:
        return True


def StartFile(filename):
    if os.name == "nt":
        try:
            os.startfile(filename)  # pylint: disable=no-member
        except:
            pass
    else:
        subprocess.Popen(["xdg-open", filename])
