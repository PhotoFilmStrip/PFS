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

APP_NAME = "PhotoFilmStrip"
APP_VERSION = "3.7.1"
APP_VERSION_EX = "%s-%s" % (APP_VERSION, SCM_REV)
APP_SLOGAN = "PhotoFilmStrip - Creates movies out of your pictures."
APP_DESCRIPTION = """\
PhotoFilmStrip creates movies out of your pictures in just 3 steps. First select your photos, customize the motion path and render the video. There are several output possibilities for VCD, SVCD, DVD up to FULL-HD.
"""
APP_URL = "http://www.photofilmstrip.org"
DEVELOPERS = [u"Jens Göpfert"]
TRANSLATORS = ["Teza Lprod - http://lprod.org", "geogeo - http://www.geogeo.gr"]
