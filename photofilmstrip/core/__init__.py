# encoding: UTF-8
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

# WA: py2exe and PIL
import os
if os.name == "nt":
    import Image

    import ArgImagePlugin
    import BmpImagePlugin
    import BufrStubImagePlugin
    import CurImagePlugin
    import DcxImagePlugin
    import EpsImagePlugin
    import FitsStubImagePlugin
    import FliImagePlugin
    import FpxImagePlugin
    import GbrImagePlugin
    import GifImagePlugin
    import GribStubImagePlugin
    import Hdf5StubImagePlugin
    import IcnsImagePlugin
    import IcoImagePlugin
    import ImImagePlugin
    import ImtImagePlugin
    import IptcImagePlugin
    import JpegImagePlugin
    import McIdasImagePlugin
    import MicImagePlugin
    import MpegImagePlugin
    import MspImagePlugin
    import PalmImagePlugin
    import PcdImagePlugin
    import PcxImagePlugin
    import PdfImagePlugin
    import PixarImagePlugin
    import PngImagePlugin
    import PpmImagePlugin
    import PsdImagePlugin
    import SgiImagePlugin
    import SpiderImagePlugin
    import SunImagePlugin
    import TgaImagePlugin
    import TiffImagePlugin
    import WmfImagePlugin
    import XbmImagePlugin
    import XpmImagePlugin
    import XVThumbImagePlugin
    Image._initialized=2
# WA: end
