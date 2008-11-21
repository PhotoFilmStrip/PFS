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

import os

from ConfigParser import ConfigParser
from lib.common.Singleton import Singleton

from core.OutputProfile import DEFAULT_PROFILES


class Settings(Singleton):
    
    APP_NAME = u"PhotoFilmStrip"
    APP_VERSION = "0.95"
    
    def Init(self):
        self.filename = os.path.join(os.path.expanduser("~"), '.%s' % Settings.APP_NAME)
        self.__isFirstStart = False
        self.cp = None
        if not os.path.isfile(self.filename):
            self.Create()
            self.__isFirstStart = True
        self.Load()
        
    def Create(self):
        self.cp = ConfigParser()
        self.cp.add_section("General")
        self.cp.add_section("History")
        self.cp.add_section("Profiles")
        self.Save()
        
    def Load(self):
        self.cp = ConfigParser()
        self.cp.read(self.filename)
        
    def Save(self):
        fd = open(self.filename, 'w')
        self.cp.write(fd)
        fd.close()

    def IsFirstStart(self):
        return self.__isFirstStart
    
    def SetFileHistory(self, fileList):
        self.Load()
        for idx, filename in enumerate(fileList):
            if os.path.exists(filename):
                self.cp.set("History", "%d" % idx, filename)
        self.Save()
        
    def GetFileHistory(self):
        self.Load()
        fileList = []
        for idx in range(9, -1, -1):
            if self.cp.has_option("History", str(idx)):
                filename = self.cp.get("History", str(idx))
                if os.path.exists(filename):
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
        return ""

    def SetImagePath(self, path):
        self.Load()
        self.cp.set("General", "ImagePath", path)
        self.Save()

    def GetImagePath(self):
        self.Load()
        if self.cp.has_option("General", "ImagePath"):
            return self.cp.get("General", "ImagePath")
        return ""

    def SetAudioPath(self, path):
        self.Load()
        self.cp.set("General", "AudioPath", path)
        self.Save()

    def GetAudioPath(self):
        self.Load()
        if self.cp.has_option("General", "AudioPath"):
            return self.cp.get("General", "AudioPath")
        return ""

    def SetLastProfile(self, profile):
        self.Load()
        self.cp.set("General", "LastProfile", profile)
        self.Save()

    def GetLastProfile(self):
        self.Load()
        if self.cp.has_option("General", "LastProfile"):
            return self.cp.getint("General", "LastProfile")
        return 0

    def SetVideoType(self, typ):
        self.Load()
        self.cp.set("General", "VideoType", typ)
        self.Save()

    def GetVideoType(self):
        self.Load()
        if self.cp.has_option("General", "VideoType"):
            return self.cp.getint("General", "VideoType")
        return 0

    def SetUsedRenderer(self, renderer):
        self.Load()
        self.cp.set("General", "Renderer", renderer)
        self.Save()

    def GetUsedRenderer(self):
        self.Load()
        if self.cp.has_option("General", "Renderer"):
            return self.cp.getint("General", "Renderer")
        return 1
    
    def SetLastOutputPath(self, path):
        self.Load()
        self.cp.set("General", "LastOutputPath", path)
        self.Save()

    def GetLastOutputPath(self):
        self.Load()
        if self.cp.has_option("General", "LastOutputPath"):
            return self.cp.get("General", "LastOutputPath")
        return os.getcwd()
    
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
    
    def GetOutputProfiles(self):
        return DEFAULT_PROFILES
