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

import gettext
import locale
import logging
import os
import sys
import tempfile
import subprocess

from ConfigParser import ConfigParser
from lib.common.Singleton import Singleton
from lib.util import Encode, Decode, IsPathWritable


APP_DIR = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "..")


if sys.platform == "win32":
    _path = os.getenv("PATH", "").split(";")
    _path.append(os.path.join(APP_DIR, "extBin", "mplayer"))
    os.putenv("PATH", ";".join(_path)) 

    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    subprocess.STARTUPINFO = lambda: startupinfo


class Settings(Singleton):
    
    APP_NAME        = "PhotoFilmStrip"
    APP_VERSION     = "1.3.99"
    APP_DESCRIPTION = ""
    APP_URL         = "http://www.photofilmstrip.org"
    DEVELOPERS      = [u"Jens Göpfert", 
                       u"Markus Wintermann"] 
    
    def __init__(self):
        self.__isFirstStart = False
        self.cp = None
        
        if IsPathWritable(APP_DIR):
            setPath = APP_DIR
        else:
            userpath = os.path.expanduser("~")
            if userpath == "~":
                userpath = tempfile.gettempdir()
            setPath = userpath

        self.filename = os.path.join(setPath, '.%s' % Settings.APP_NAME)
        if not os.path.isfile(self.filename):
            self.__isFirstStart = True

        logging.debug("settings file: %s", self.filename)

        self.Load()
        
    def Load(self):
        if self.cp is None:
            self.cp = ConfigParser()

        if os.path.isfile(self.filename):
            self.cp.read(self.filename)

        if not self.cp.has_section("General"):
            self.cp.add_section("General")
            
        if not self.cp.has_section("History"):
            self.cp.add_section("History")
            
        if not self.cp.has_section("Profiles"):
            self.cp.add_section("Profiles")
        
    def Save(self):
        try:
            fd = open(self.filename, 'w')
            self.cp.write(fd)
            fd.close()
        except IOError:
            pass

    def IsFirstStart(self):
        return self.__isFirstStart
    
    def SetLanguage(self, lang):
        self.Load()
        self.cp.set("General", "Language", Encode(lang))
        self.Save()

    def GetLanguage(self):
        self.Load()
        if self.cp.has_option("General", "Language"):
            return Decode(self.cp.get("General", "Language"))
        return locale.getdefaultlocale()[0]

    def SetFileHistory(self, fileList):
        self.Load()
        self.cp.remove_section("History")
        self.cp.add_section("History")
        for idx, filename in enumerate(fileList):
            if idx < 10 and os.path.exists(filename):
                self.cp.set("History", "%d" % idx, Encode(os.path.abspath(filename)))
        self.Save()
        
    def GetFileHistory(self):
        self.Load()
        fileList = []
        for idx in range(10):
            if self.cp.has_option("History", str(idx)):
                filename = Decode(self.cp.get("History", str(idx)))
                if os.path.exists(filename) and filename not in fileList:
                    fileList.append(filename)

        return fileList
    
    def SetProjectPath(self, path):
        self.Load()
        self.cp.set("General", "ProjectPath", Encode(path))
        self.Save()

    def GetProjectPath(self):
        self.Load()
        if self.cp.has_option("General", "ProjectPath"):
            return Decode(self.cp.get("General", "ProjectPath"))
        return u""

    def SetImagePath(self, path):
        self.Load()
        self.cp.set("General", "ImagePath", Encode(path))
        self.Save()

    def GetImagePath(self):
        self.Load()
        if self.cp.has_option("General", "ImagePath"):
            return Decode(self.cp.get("General", "ImagePath"))
        return u""

    def SetAudioPath(self, path):
        self.Load()
        self.cp.set("General", "AudioPath", Encode(path))
        self.Save()

    def GetAudioPath(self):
        self.Load()
        if self.cp.has_option("General", "AudioPath"):
            return Decode(self.cp.get("General", "AudioPath"))
        return u""

    def SetLastProfile(self, profile):
        self.Load()
        self.cp.set("General", "LastProfile", str(profile))
        self.Save()

    def GetLastProfile(self):
        self.Load()
        if self.cp.has_option("General", "LastProfile"):
            return self.cp.getint("General", "LastProfile")
        return 0

    def SetVideoType(self, typ):
        self.Load()
        self.cp.set("General", "VideoType", str(typ))
        self.Save()

    def GetVideoType(self):
        self.Load()
        if self.cp.has_option("General", "VideoType"):
            return self.cp.getint("General", "VideoType")
        return 0

    def SetUsedRenderer(self, renderer):
        self.Load()
        self.cp.set("General", "Renderer", str(renderer))
        self.Save()

    def GetUsedRenderer(self):
        self.Load()
        if self.cp.has_option("General", "Renderer"):
            return self.cp.getint("General", "Renderer")
        return 1
    
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
            try:
                result[prop] = eval(value)
            except:
                result[prop] = value
        
        return result

    def InitLanguage(self):
        curLang = self.GetLanguage()
        localeDir = os.path.join(os.path.dirname(os.path.abspath(sys.argv[0])), "../locale")
        
        if not os.path.isdir(localeDir):
            gettext.install(self.APP_NAME)
            return 
    
        lang = gettext.translation(self.APP_NAME, 
                                   localeDir, 
                                   languages=[curLang, "en"])
        lang.install(True)
        