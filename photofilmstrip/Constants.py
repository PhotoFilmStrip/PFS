# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2011 Jens Goepfert
#

import os
import sys

try:
    from photofilmstrip._scmInfo import SCM_REV  # IGNORE:F0401
except ImportError:
    SCM_REV = "src"

if getattr(sys, "frozen", False):
    APP_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
else:
    APP_DIR = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "..")

VERSION_SUFFIX = ''

APP_NAME = "PhotoFilmStrip"
APP_VERSION = "4.1.0"
APP_VERSION_SUFFIX = "%s%s" % (APP_VERSION, VERSION_SUFFIX)
APP_VERSION_FULL = "%s-%s" % (APP_VERSION_SUFFIX, SCM_REV)
APP_SLOGAN = "PhotoFilmStrip - Creates movies out of your pictures."
APP_DESCRIPTION = """\
PhotoFilmStrip creates movies out of your pictures in just 3 steps. First select your photos, customize the motion path and render the video. There are several output possibilities for VCD, SVCD, DVD up to FULL-HD.
"""
APP_URL = "http://www.photofilmstrip.org"
DEVELOPERS = ["Jens Göpfert"]
TRANSLATORS = ["Jens Göpfert"]
