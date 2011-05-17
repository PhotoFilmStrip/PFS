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

import cStringIO
import logging
import Image


def ImageToStream(pilImg, format="JPEG"):
    fd = cStringIO.StringIO()
    pilImg.save(fd, format)
    fd.seek(0)
    return fd


def RotateExif(img):
    exifOrient = 274
    rotation = 0 
    try:
        exif = img._getexif()
        if isinstance(exif, dict) and exif.has_key(exifOrient):
            rotation = exif[exifOrient]
    except AttributeError:
        pass
    except Exception, err:
        print exif, type(exif)
        logging.debug("PILBackend.RotateExif(): %s", err, exc_info=1)
            
    if rotation == 2:
        # flip horizontal
        return img.transpose(Image.FLIP_LEFT_RIGHT)
    elif rotation == 3:
        # rotate 180
        return img.rotate(-180)
    elif rotation == 4:
        # flip vertical
        return img.transpose(Image.FLIP_TOP_BOTTOM)
    elif rotation == 5:
        # transpose
        img = img.rotate(-90)
        return img.transpose(Image.FLIP_LEFT_RIGHT)
    elif rotation == 6:
        # rotate 90
        return img.rotate(-90)
    elif rotation == 7:
        # transverse
        img = img.rotate(-90)
        return img.transpose(Image.FLIP_TOP_BOTTOM)
    elif rotation == 8:
        # rotate 270
        return img.rotate(-270)
        
    return img

