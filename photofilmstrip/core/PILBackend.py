# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2010 Jens Goepfert
#

import logging
import io

from PIL import Image, ImageDraw

from photofilmstrip.core.Picture import Picture


def ImageToStream(pilImg, imgFormat="JPEG"):
    fd = io.BytesIO()
    pilImg.save(fd, imgFormat)
    fd.seek(0)
    return fd


def ImageFromBuffer(size, buffr):
    pilImg = Image.frombuffer("RGB", size, buffr, 'raw', "RGB", 0, 1)
    return pilImg


def RotateExif(pilImg):
    exifOrient = 274
    rotation = 0
    try:
        exif = pilImg._getexif()  # pylint: disable=protected-access
        if isinstance(exif, dict) and exifOrient in exif:
            rotation = exif[exifOrient]
    except AttributeError:
        pass
    except Exception as err:
        logging.debug("PILBackend.RotateExif(): %s", err, exc_info=1)

    if rotation == 2:
        # flip horizontal
        return pilImg.transpose(Image.FLIP_LEFT_RIGHT)
    elif rotation == 3:
        # rotate 180
        return pilImg.rotate(-180)
    elif rotation == 4:
        # flip vertical
        return pilImg.transpose(Image.FLIP_TOP_BOTTOM)
    elif rotation == 5:
        # transpose
        pilImg = pilImg.rotate(-90, expand=1)
        return pilImg.transpose(Image.FLIP_LEFT_RIGHT)
    elif rotation == 6:
        # rotate 90
        return pilImg.rotate(-90, expand=1)
    elif rotation == 7:
        # transverse
        pilImg = pilImg.rotate(-90, expand=1)
        return pilImg.transpose(Image.FLIP_TOP_BOTTOM)
    elif rotation == 8:
        # rotate 270
        return pilImg.rotate(-270, expand=1)

    return pilImg


def CropAndResize(pilImg, rect, size, draft=False):
    if draft:
        filtr = Image.NEAREST
    else:
        filtr = Image.BILINEAR
    img = pilImg.transform(size,
                           Image.AFFINE,
                           [rect[2] / size[0], 0, rect[0],
                            0, rect[3] / size[1], rect[1]],
                           filtr)
    return img


def Transition(kind, pilImg1, pilImg2, percentage):
    if kind == Picture.TRANS_FADE:
        img = Image.blend(pilImg1, pilImg2, percentage)
    elif kind == Picture.TRANS_ROLL:
        xsize, ysize = pilImg1.size
        delta = int(xsize * percentage)
        part1 = pilImg2.crop((0, 0, delta, ysize))
        part2 = pilImg1.crop((delta, 0, xsize, ysize))
        image = pilImg2.copy()
        image.paste(part2, (0, 0, xsize - delta, ysize))
        image.paste(part1, (xsize - delta, 0, xsize, ysize))
        img = image

    return img


def __CreateDummyImage(message):
    width = 400
    height = 300
    img = Image.new("RGB", (width, height), (255, 255, 255))

    draw = ImageDraw.Draw(img)
    textWidth, textHeight = draw.textsize(message)
    x = (width - textWidth) // 2
    y = (height - textHeight * 2)
    draw.text((x, y), message, fill=(0, 0, 0))

    sz = width // 2
    draw.ellipse(((width - sz) // 2, (height - sz) // 2,
                  (width + sz) // 2, (height + sz) // 2),
                  fill=(255, 0, 0))

    sz = width // 7
    draw.line((width // 2 - sz, height // 2 - sz, width // 2 + sz, height // 2 + sz), fill=(255, 255, 255), width=20)
    draw.line((width // 2 + sz, height // 2 - sz, width // 2 - sz, height // 2 + sz), fill=(255, 255, 255), width=20)

    del draw

    return img


def __GetImage(picture):
    try:
        img = Image.open(picture.GetFilename())
        # open does not validate the image data, because it is not loaded yet
        # use thumbnail() instead of load, it checks image data much faster
        img.thumbnail((10, 10))
        # discard the thumbnail
        img = Image.open(picture.GetFilename())
        picture.SetDummy(False)
    except Exception as err:
        logging.debug("PILBackend.GetImage(%s): %s", picture.GetFilename(), err, exc_info=1)
        img = __CreateDummyImage(str(err))
        picture.SetDummy(True)
    return img


def __ProcessImage(img, picture):
    if not picture.IsDummy():
        img = RotateExif(img)
        rotation = picture.GetRotation() * -90
        if rotation != 0:
            img = img.rotate(rotation)

    if picture.GetEffect() == picture.EFFECT_BLACK_WHITE:
        img = img.convert("L")

    elif picture.GetEffect() == picture.EFFECT_SEPIA:

        def make_linear_ramp(white):
            # putpalette expects [r,g,b,r,g,b,...]
            ramp = []
            r, g, b = white
            for i in range(255):
                ramp.extend((r * i // 255, g * i // 255, b * i // 255))
            return ramp

        # make sepia ramp (tweak color as necessary)
        sepia = make_linear_ramp((255, 240, 192))
        img = img.convert("L")
        img.putpalette(sepia)

    return img.convert("RGB")


def GetImage(picture):
    pilImg = __GetImage(picture)
    pilImg = __ProcessImage(pilImg, picture)
    picture.SetWidth(pilImg.size[0])
    picture.SetHeight(pilImg.size[1])
    return pilImg


def GetExifRotation(pilImg):
    exifOrient = 274
    rotation = 0
    try:
        exif = pilImg._getexif()  # pylint: disable=protected-access
        if isinstance(exif, dict) and exifOrient in exif:
            rotation = exif[exifOrient]
    except AttributeError:
        pass
    except Exception as err:
        logging.debug("PILBackend.RotateExif(): %s", err, exc_info=1)

    if rotation == 3:
        # rotate 180
        return 2
    elif rotation == 5:
        # transpose
        return 1
    elif rotation == 6:
        # rotate 90
        return 1
    elif rotation == 7:
        # transverse
        return 1
    elif rotation == 8:
        # rotate 270
        return 3
    else:
        return 0


def GetImageSize(filename):
    pilImg = Image.open(filename)
    width, height = pilImg.size
    rotation = GetExifRotation(pilImg)
    while rotation > 0:
        width, height = height, width
        rotation -= 1
    return width, height


def GetThumbnail(picture, width=None, height=None):
    img = __GetImage(picture)

    aspect = img.size[0] / img.size[1]
    if width is not None and height is not None:
        thumbWidth = width
        thumbHeight = height
    elif width is not None:
        thumbWidth = width
        thumbHeight = int(round(thumbWidth / aspect))
    elif height is not None:
        thumbHeight = height
        thumbWidth = int(round(thumbHeight * aspect))

    # prescale image to speed up processing
    img.thumbnail((max(thumbWidth, thumbHeight), max(thumbWidth, thumbHeight)), Image.NEAREST)
    img = __ProcessImage(img, picture)

    # make the real thumbnail
    img.thumbnail((thumbWidth, thumbHeight), Image.NEAREST)

#    newImg = Image.new("RGB", (thumbWidth, thumbHeight), 0)
#    newImg.paste(img, (abs(thumbWidth - img.size[0]) / 2,
#                       abs(thumbHeight - img.size[1]) / 2))
#    img = newImg

    return img
