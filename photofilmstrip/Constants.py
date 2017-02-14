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

import os
import sys

try:
    from photofilmstrip._scmInfo import SCM_REV # IGNORE:F0401
except ImportError:
    SCM_REV = "src"


APP_DIR = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "..")

APP_NAME        = "PhotoFilmStrip"
APP_VERSION     = "3.0.1"
APP_VERSION_EX  = "%s-%s" % (APP_VERSION, SCM_REV)
APP_SLOGAN      = "PhotoFilmStrip - Creates movies out of your pictures."
APP_DESCRIPTION = """\
PhotoFilmStrip creates movies out of your pictures in just 3 steps. First select your photos, customize the motion path and render the video. There are several output possibilities for VCD, SVCD, DVD up to FULL-HD.
"""
APP_URL         = "http://www.photofilmstrip.org"
DEVELOPERS      = [u"Jens Göpfert", 
                   u"Markus Wintermann"] 
TRANSLATORS     = ["Teza Lprod - http://lprod.org", "geogeo - http://www.geogeo.gr"]
