# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
#

import base64
import io

import wx
import wx.svg

import photofilmstrip.res.images


class ArtProvider:

    provider = None

    @classmethod
    def Init(cls):
        if cls.provider is None:
            cls.provider = Res2PyArtProvider(
                photofilmstrip.res.images,
                artIdPrefix='PFS_'
            )
            wx.ArtProvider.Push(cls.provider)


class Res2PyArtProvider(wx.ArtProvider):

    def __init__(self, imageModule, artIdPrefix='wxART_'):
        self.catalog = imageModule.catalog
        self.index = imageModule.index
        self.artIdPrefix = artIdPrefix

        wx.ArtProvider.__init__(self)

    def CreateBitmap(self, artId, artClient, size):
        if size[0] == -1 or size[1] == -1:
            size = wx.ArtProvider.GetSizeHint(artClient)

        if artId.startswith(self.artIdPrefix):
            name = artId[len(self.artIdPrefix):]
            if name in self.catalog:
                return self.DataToBitmap(self.catalog[name], size)

        return wx.NullBitmap

    def DataToBitmap(self, data, size):
        data = base64.b64decode(data)
        if data.startswith(b"<?xml"):
            svgImg = wx.svg.SVGimage.CreateFromBytes(data, units='px', dpi=96)
            bmp = svgImg.ConvertToScaledBitmap(size)
            if bmp.IsOk():
                return bmp
            else:
                return wx.NullBitmap
        else:
            stream = io.BytesIO(data)
            wxImg = wx.Image(stream)
            if wxImg.IsOk():
                return wx.Bitmap(wxImg)
            else:
                return wx.NullBitmap

