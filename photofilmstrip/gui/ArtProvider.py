# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#

import wx
from wx.lib.art import img2pyartprov

import photofilmstrip.res.images


class ArtProvider:

    provider = None

    @classmethod
    def Init(cls):
        if cls.provider is None:
            cls.provider = img2pyartprov.Img2PyArtProvider(
                photofilmstrip.res.images,
                artIdPrefix='PFS_'
            )
            wx.ArtProvider.Push(cls.provider)
