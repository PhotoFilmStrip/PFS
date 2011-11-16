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

import logging
import cStringIO

import Image, ImageDraw

from photofilmstrip.core.BaseBackend import BaseBackend, BaseCtx
from photofilmstrip.core.Picture import Picture


class PILBackend(BaseBackend):
    
    def __init__(self):
        BaseBackend.__init__(self)
    
    @staticmethod
    def ImageToStream(pilImg, imgFormat="JPEG"):
        fd = cStringIO.StringIO()
        pilImg.save(fd, imgFormat)
        fd.seek(0)
        return fd
    
    @staticmethod
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
    
    def CreateCtx(self, pic):
        pilImg = pic.GetImage()
        return PILCtx(pilImg)

    def _CropAndResize(self, ctx, rect, size):
        width, height = ctx.size
        mask_width, mask_height = size
        aspect = 1.0 * width / height
        mask_aspect = 1.0*mask_width/mask_height
        im = ctx.data
        if aspect > mask_aspect:
            ratio = 1.0 * height / mask_height
            imt = im.transform((mask_width, mask_height), 
                               Image.AFFINE,
                               (ratio, 0, (width-mask_width*ratio)/2, 0, ratio, 0),
                               Image.CUBIC)
        else:
            ratio = 1.0 * width / mask_width
            imt = im.transform((mask_width, mask_height), 
                               Image.AFFINE, 
                               (ratio, 0, 0, 0, ratio, (height-mask_height*ratio)/2),
                               Image.CUBIC)
        return PILCtx(imt)
            
    def CropAndResize(self, ctx, rect, size, draft=False):
        box = [int(rect[0]), int(rect[1]), 
               int(rect[0] + rect[2]), int(rect[1] + rect[3])]
        subImg = ctx.data.crop(box)
        
        if draft:
            filtr = Image.NEAREST
        else:
            filtr = Image.ANTIALIAS
            
#        if not self._draft:
#            # Begin Optimizations
#            if cropRect[2] > size[0] * 3:
#                # downscale more than factor 3, prescaling
#                subImg = subImg.resize((size[0] * 2, size[1] * 2))#, Image.BILINEAR)
#            if cropRect[2] < size[0]:
#                # upscaling
#                filterStr = "bicubic"
#            # End Optimizations
            
        return PILCtx(subImg.resize(size, filtr))
    
    def Transition(self, kind, ctx1, ctx2, percentage):
        if kind == Picture.TRANS_FADE:
            img = Image.blend(ctx1.data, ctx2.data, percentage)
        elif kind == Picture.TRANS_ROLL:
            img = self._Roll(ctx1.data, ctx2.data, percentage)
            
        return PILCtx(img)

    def _Roll(self, img1, img2, proc):
        xsize, ysize = img1.size
        delta = int(xsize * proc)
        part1 = img2.crop((0, 0, delta, ysize))
        part2 = img1.crop((delta, 0, xsize, ysize))
        image = img2.copy()
        image.paste(part2, (0, 0, xsize-delta, ysize))
        image.paste(part1, (xsize-delta, 0, xsize, ysize))
        return image

    @staticmethod
    def __CreateDummyImage(message):
        width = 400
        height = 300
        img = Image.new("RGB", (width, height), (255, 255, 255))

        draw = ImageDraw.Draw(img)
        textWidth, textHeight = draw.textsize(message)
        x = (width - textWidth) / 2
        y = (height - textHeight * 2)
        draw.text((x, y), message, fill=(0, 0, 0))

        sz = width / 2
        draw.ellipse(((width - sz) / 2, (height - sz) / 2, 
                      (width + sz) / 2, (height + sz) / 2), 
                      fill=(255, 0, 0))

        sz = width / 7
        draw.line((width / 2 - sz, height / 2 - sz, width / 2 + sz, height / 2 + sz), fill=(255, 255, 255), width=20)
        draw.line((width / 2 + sz, height / 2 - sz, width / 2 - sz, height / 2 + sz), fill=(255, 255, 255), width=20)

        del draw
        
        return img

    @staticmethod
    def GetImageSize(img):
        return img.size[0], img.size[1]
    
    @classmethod
    def __GetImage(cls, picture):
        try:
            img = Image.open(picture.GetFilename())
            picture.SetDummy(False)
        except StandardError, err:
            logging.debug("PILBackend.GetImage(%s): %s", picture.GetFilename(), err, exc_info=1)
            img = cls.__CreateDummyImage(str(err))
            picture.SetDummy(True)
        return img
    
    @classmethod
    def __ProcessImage(cls, img, picture):
        if not picture.IsDummy():
            img = cls.RotateExif(img)
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
                    ramp.extend((r*i/255, g*i/255, b*i/255))
                return ramp

            # make sepia ramp (tweak color as necessary)
            sepia = make_linear_ramp((255, 240, 192))
            img = img.convert("L")
            img.putpalette(sepia)

        return img.convert("RGB")
    
    @classmethod
    def GetImage(cls, picture):
        img = cls.__GetImage(picture)
        return cls.__ProcessImage(img, picture)
        
    @classmethod
    def GetThumbnail(cls, picture, width=None, height=None):
        img = cls.__GetImage(picture)

        aspect = float(img.size[0]) / float(img.size[1])
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
        img = cls.__ProcessImage(img, picture)
        
        # make the real thumbnail
        img.thumbnail((thumbWidth, thumbHeight), Image.NEAREST)
        
#        newImg = Image.new("RGB", (thumbWidth, thumbHeight), 0)
#        newImg.paste(img, (abs(thumbWidth - img.size[0]) / 2, 
#                           abs(thumbHeight - img.size[1]) / 2))
#        img = newImg
        
        return img


class PILCtx(BaseCtx):
    
    def __init__(self, obj):
        BaseCtx.__init__(self, obj.size, obj)
    
    def Serialize(self):
        self.data = self.data.convert("RGB").tostring()

    def Unserialize(self, stream):
        stream = self.data
        self.data = Image.fromstring("RGB", self.size, stream)

    def ToStream(self, writer, imgFormat, *args, **kwargs):
        if imgFormat in ["JPEG", "PPM"]:
            self.data.save(writer, imgFormat, *args, **kwargs)
        else:
            raise RuntimeError("unsupported format: %s", imgFormat)
