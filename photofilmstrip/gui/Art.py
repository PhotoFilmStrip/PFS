# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2024 Jens Goepfert
#
import base64
import io
import logging

import wx
import wx.svg

import photofilmstrip.res.images


class Art:

    artIdPrefix = "PFS_"
    isDark = False

    @classmethod
    def Init(cls):
        cls.catalog = photofilmstrip.res.images.catalog
        cls.UpdateFromSystem()

    @classmethod
    def UpdateFromSystem(cls, which=None):
        osDescr = wx.GetOsDescription()
        logging.debug("UpdateFromSystem: %s", osDescr)
        if not osDescr.lower().startswith("windows"):
            cls.isDark = wx.SystemSettings.GetAppearance().IsDark()

    @classmethod
    def GetBitmap(cls, artId, artClient=wx.ART_OTHER, size=(-1, -1)):
        logging.debug("Art.GetBitmap(%s, %s, %s)", artId, artClient, size)
        artClient = cls.PrepareArtClient(artClient)
        data = cls.GetData(artId)

        if size == (-1, -1):
            size = wx.ArtProvider.GetSizeHint(artClient)

        result = wx.NullBitmap
        if cls.IsSvg(data):
            data = cls.PrepareSvg(data)
            svgImg = wx.svg.SVGimage.CreateFromBytes(data, units='px', dpi=96)
            result = svgImg.ConvertToScaledBitmap(size)
        elif data:
            stream = io.BytesIO(data)
            wxImg = wx.Image(stream)
            if wxImg.IsOk():
                result = wx.Bitmap(wxImg)
        else:
            result = wx.ArtProvider.GetBitmap(artId, artClient, size)

#        if result.IsOk():
#            scale = wx.Display(0).GetScaleFactor()
#            result.SetScaleFactor(scale)
        return result

    @classmethod
    def GetBitmapBundle(cls, artId, artClient=wx.ART_OTHER, size=(-1, -1)):
        logging.debug("Art.GetBitmapBundle(%s, %s, %s)", artId, artClient, size)
        artClient = cls.PrepareArtClient(artClient)
        data = cls.GetData(artId)

        if size == (-1, -1):
            size = wx.ArtProvider.GetSizeHint(artClient)

        result = wx.NullBitmap
        if cls.IsSvg(data):
            data = cls.PrepareSvg(data)
            result = wx.BitmapBundle.FromSVG(data, size)
        else:
            result = wx.ArtProvider.GetBitmapBundle(artId, artClient, size)
        return result

    @classmethod
    def GetIcon(cls, artId, artClient=wx.ART_OTHER, size=(-1, -1)):
        assert size != (-1, -1)
        bmp = Art.GetBitmap(artId, artClient, size)
        icon = wx.Icon()
        icon.CopyFromBitmap(bmp)
        return icon

    @classmethod
    def GetIconBundle(cls, artId, artClient=wx.ART_OTHER, size=(-1, -1)):
        assert artClient == wx.ART_OTHER
        assert size == (-1, -1)
        iconBundle = wx.IconBundle()
        iconBundle.AddIcon(Art.GetIcon(artId, wx.ART_OTHER, (16, 16)))
        iconBundle.AddIcon(Art.GetIcon(artId, wx.ART_OTHER, (24, 24)))
        iconBundle.AddIcon(Art.GetIcon(artId, wx.ART_OTHER, (32, 32)))
        iconBundle.AddIcon(Art.GetIcon(artId, wx.ART_OTHER, (48, 48)))
        iconBundle.AddIcon(Art.GetIcon(artId, wx.ART_OTHER, (64, 64)))
        iconBundle.AddIcon(Art.GetIcon(artId, wx.ART_OTHER, (128, 128)))
        return iconBundle

    @classmethod
    def GetData(cls, artId):
        if isinstance(artId, bytes):
            artId = artId.decode()
        result = None
        if artId.startswith(cls.artIdPrefix):
            name = artId[len(cls.artIdPrefix):]
            if name in cls.catalog:
                result = base64.b64decode(cls.catalog[name])
        return result

    @classmethod
    def PrepareArtClient(cls, artClient):
        if isinstance(artClient, bytes):
            artClient = artClient.decode()
        if artClient == wx.ART_TOOLBAR.decode():
            logging.debug("Art.PrepareArtClient(%s) -> wx.ART_MENU", artClient)
#            artClient = wx.ART_MENU
        return artClient

    @staticmethod
    def IsSvg(data):
        return data and (data.startswith(b"<?xml") or data.startswith(b"<svg"))

    @classmethod
    def PrepareSvg(cls, data):
        result = data
        if cls.isDark:
            result = result.replace(b"#34495e", b"#ffffff")
            result = result.replace(b"#34495f", b"#34495e") # accent color is slighty different
        return result

    @classmethod
    def ThemeColor(cls, color):
        if ((255 - color.Red()) +
            (255 - color.Green()) +
            (255 - color.Blue()) < 60):
            color = color.ChangeLightness(92)
        if cls.isDark:
            gradient = color.ChangeLightness(70);
            return gradient
        return color

    @classmethod
    def GetColour(cls, client='wx'):
        if client == 'wx':
            return wx.Colour(52, 73, 94) # #34495e
        elif client == 'html':
            return "#34495e"