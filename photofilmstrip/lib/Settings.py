# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2011 Jens Goepfert
#

import locale
import logging
import os
import tempfile

from configparser import ConfigParser
from photofilmstrip.lib.common.Singleton import Singleton
from photofilmstrip.lib.util import IsPathWritable

from photofilmstrip import Constants


class Settings(Singleton):

    def __init__(self):
        self.cp = None

        if IsPathWritable(Constants.APP_DIR):
            setPath = Constants.APP_DIR
        else:
            userpath = os.path.expanduser("~")
            if userpath == "~":
                userpath = tempfile.gettempdir()
            setPath = userpath

        self.filename = os.path.join(setPath, '.%s' % Constants.APP_NAME)

        logging.debug("settings file: %s", self.filename)

        self.Load()

    def Load(self):
        if self.cp is None:
            self.cp = ConfigParser()

        if os.path.isfile(self.filename):
            self.cp.read(self.filename, "utf-8")

        if not self.cp.has_section("General"):
            self.cp.add_section("General")

        if not self.cp.has_section("History"):
            self.cp.add_section("History")

        if not self.cp.has_section("Profiles"):
            self.cp.add_section("Profiles")

    def Save(self):
        try:
            fd = open(self.filename, 'w', encoding='utf-8')
            self.cp.write(fd)
            fd.close()
        except IOError:
            pass

    def SetLanguage(self, lang):
        self.Load()
        self.cp.set("General", "Language", lang)
        self.Save()

    def GetLanguage(self):
        self.Load()
        if self.cp.has_option("General", "Language"):
            return self.cp.get("General", "Language")
        defLang = locale.getdefaultlocale()[0]
        if defLang is None:
            defLang = ""
        return defLang

    def SetFileHistory(self, fileList):
        self.Load()
        self.cp.remove_section("History")
        self.cp.add_section("History")
        for idx, filename in enumerate(fileList):
            if idx < 10 and os.path.exists(filename):
                self.cp.set("History", "%d" % idx, os.path.abspath(filename))
        self.Save()

    def GetFileHistory(self):
        self.Load()
        fileList = []
        for idx in range(10):
            if self.cp.has_option("History", str(idx)):
                filename = self.cp.get("History", str(idx))
                if os.path.exists(filename) and filename not in fileList:
                    fileList.append(filename)

        return fileList

    def SetProjectPath(self, path):
        self.Load()
        self.cp.set("General", "ProjectPath", path)
        self.Save()

    def GetProjectPath(self):
        self.Load()
        if self.cp.has_option("General", "ProjectPath"):
            return self.cp.get("General", "ProjectPath")
        return u""

    def SetImagePath(self, path):
        self.Load()
        self.cp.set("General", "ImagePath", path)
        self.Save()

    def GetImagePath(self):
        self.Load()
        if self.cp.has_option("General", "ImagePath"):
            return self.cp.get("General", "ImagePath")
        return u""

    def SetAudioPath(self, path):
        self.Load()
        self.cp.set("General", "AudioPath", path)
        self.Save()

    def GetAudioPath(self):
        self.Load()
        if self.cp.has_option("General", "AudioPath"):
            return self.cp.get("General", "AudioPath")
        return u""

    def SetLastProfile(self, profile):
        self.Load()
        self.cp.set("General", "LastProfile", str(profile))
        self.Save()

    def GetLastProfile(self):
        self.Load()
        if self.cp.has_option("General", "LastProfile"):
            try:
                return self.cp.get("General", "LastProfile")
            except:
                pass
        return None

    def SetUsedRenderer(self, renderer):
        self.Load()
        self.cp.set("General", "Renderer", str(renderer))
        self.Save()

    def GetUsedRenderer(self):
        self.Load()
        if self.cp.has_option("General", "Renderer"):
            try:
                return self.cp.getint("General", "Renderer")
            except:
                pass
        return None

    def SetLastKnownVersion(self, version):
        self.Load()
        self.cp.set("General", "LastKnownVersion", version)
        self.Save()

    def GetLastKnownVersion(self):
        self.Load()
        if self.cp.has_option("General", "LastKnownVersion"):
            return self.cp.get("General", "LastKnownVersion")
        return "0.0.0"

    def SetRenderProperties(self, renderer, props):
        self.Load()
        if self.cp.has_section(renderer):
            self.cp.remove_section(renderer)
        self.cp.add_section(renderer)
        for prop, value in props.items():
            self.cp.set(renderer, prop, value)
        self.Save()

    def GetRenderProperties(self, renderer):
        self.Load()
        result = {}
        if not self.cp.has_section(renderer):
            return result
        for prop, value in self.cp.items(renderer):
            result[prop] = value

        return result
