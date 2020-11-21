# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#

import logging
import os
import subprocess
import sys

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
    if filename and not os.path.isfile(filename):
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


def GetDocDir(subfolder):
    basedir = os.path.dirname(os.path.abspath(sys.argv[0]))
    for docDir in (os.path.join("..", "share", "doc", "photofilmstrip", subfolder),  # linux
                   os.path.join("share", "doc", "photofilmstrip", subfolder),  # win
                   os.path.join("..", "build", "sphinx", subfolder)):  # source
        docDir = os.path.join(basedir, docDir)
        if os.path.isdir(docDir):
            return os.path.abspath(docDir)
    else:
        return None


def GetDataDir(subfolder):
    basedir = os.path.dirname(os.path.abspath(sys.argv[0]))
    for dataDir in (os.path.join("..", "share", "photofilmstrip", subfolder),  # linux
                   os.path.join("share", "photofilmstrip", subfolder),  # win
                   os.path.join("..", "data", subfolder)):  # source
        dataDir = os.path.join(basedir, dataDir)
        if os.path.isdir(dataDir):
            return os.path.abspath(dataDir)
    else:
        return None


class StreamToLogger(object):

    def __init__(self, loggerName, logLevel):
        self.logger = logging.getLogger(loggerName)
        self.logLevel = logLevel
        self.buffer = []

    def write(self, value):
        if value == "\n":
            current = self.buffer
            self.buffer = []
            self.logger.log(self.logLevel, "".join(current))
        else:
            self.buffer.append(value)

    def flush(self):
        pass
