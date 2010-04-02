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
import random
import sqlite3

import Image

from lib.util import Encode

from core.util import RotateExif
from core.Picture import Picture
from core.ProgressHandler import ProgressHandler


class PhotoFilmStrip(object):
    
    REV = 2
    
    @staticmethod
    def IsOk(filename):
        conn = sqlite3.connect(Encode(filename), detect_types=sqlite3.PARSE_DECLTYPES)
        cur = conn.cursor()
        
        try:
            cur.execute("select * from `picture`")
        except sqlite3.DatabaseError, dberr:
            return False
        return True
    
    @staticmethod
    def QuickInfo(filename):
        conn = sqlite3.connect(Encode(filename), 
                               detect_types=sqlite3.PARSE_DECLTYPES)
        cur = conn.cursor()
        
        cur.execute("select count(*) from `picture`")
        imgCount = cur.fetchone()[0]
        picIdx   = random.randint(0, imgCount - 1)
        
        cur.execute("select filename, rotation from `picture` limit ?,1", (picIdx, ))
        imgFile, rotation = cur.fetchone()
        
        if os.path.exists(imgFile):
            img = Image.open(imgFile)
            img = RotateExif(img)
            img = img.rotate(rotation * -90)
            img.thumbnail((64, 64), Image.NEAREST)
        else:
            img = None

        return imgCount, img
        
    def __init__(self, filename=None):
        self.__pictures = []
        self.__uiHandler = UserInteractionHandler()
        self.__progressHandler = ProgressHandler()
        self.__filename = filename
        
        self.__audioFile = None
        self.__aspect = 16.0 / 9.0
        self.__duration = None
        
    def GetFilename(self):
        return self.__filename
    
    def GetPictures(self):
        return self.__pictures
    
    def SetPictures(self, picList):
        self.__pictures = picList
        
    def SetUserInteractionHandler(self, uiHdl):
        self.__uiHandler = uiHdl
        
    def SetProgressHandler(self, progressHandler):
        self.__progressHandler = progressHandler
    
    def SetAudioFile(self, audioFile):
        self.__audioFile = audioFile
    def GetAudioFile(self):
        return self.__audioFile
    
    def SetAspect(self, aspect):
        self.__aspect = aspect
    def GetAspect(self):
        return self.__aspect
    
    def SetDuration(self, duration):
        self.__duration = duration
    def GetDuration(self, calc=True):
        if self.__duration is None:
            if not calc:
                return None
            totalTime = 0
            for pic in self.__pictures:
                totalTime += pic.GetDuration()
        else:
            totalTime = self.__duration
        return totalTime
    
    def Load(self, filename, importPath=None):
        if not os.path.isfile(filename):
            return False
        
        conn = sqlite3.connect(Encode(filename), detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = conn.cursor()
        cur.row_factory = sqlite3.Row
        
        try:
            cur.execute("select * from `picture`")
        except sqlite3.DatabaseError, dberr:
            return False
        resultSet = cur.fetchall()
        
        self.__progressHandler.SetMaxProgress(len(resultSet))
        
        picList = []
        altPaths = {}
        for row in resultSet:
            imgFile = row["filename"]
            imgPath = os.path.dirname(imgFile)
            self.__progressHandler.Step(_(u"Loading '%s' ...") % (os.path.basename(imgFile)))
            
            picData = self.__LoadSafe(row, 'data', None)
            if picData is None:
                if not (os.path.exists(imgPath) and os.path.isfile(imgFile)):
                    if altPaths.has_key(imgPath):
                        altPath = altPaths[imgPath]
                    else:
                        altPath = self.__uiHandler.GetAltPath(imgPath)
                        altPaths[imgPath] = altPath
                        
                    imgFile = os.path.join(altPaths[imgPath], os.path.basename(imgFile))
                
                pic = Picture(imgFile)

            else:
                if importPath is None:
                    importPath = os.path.dirname(filename)
                    
                tmpImg = os.path.join(importPath, os.path.basename(imgFile))
                if os.path.isfile(tmpImg):
                    print 'file exists', tmpImg
                fd = open(tmpImg, 'wb')
                fd.write(picData)
                fd.close()
                pic = Picture(tmpImg)
            
            pic.SetWidth(self.__LoadSafe(row, 'width', -1))
            pic.SetHeight(self.__LoadSafe(row, 'height', -1))
            rect = (row["start_left"], row["start_top"], row["start_width"], row["start_height"])
            pic.SetStartRect(rect)
            rect = (row["target_left"], row["target_top"], row["target_width"], row["target_height"])
            pic.SetTargetRect(rect)
            pic.SetDuration(row["duration"])
            pic.SetComment(row["comment"])
            pic.SetRotation(row['rotation'])
            pic.SetEffect(self.__LoadSafe(row, 'effect', Picture.EFFECT_NONE))

            picList.append(pic)

        fileRev = 1
        try:
            cur.execute("select value from `property` where name=?", ("rev", ))
            result = cur.fetchone()
            if result:
                fileRev = int(result[0])
        except sqlite3.DatabaseError, dberr:
            pass
        
        if fileRev >= 2:
            self.__audioFile = self.__LoadProperty(cur, "audiofile", unicode)
            self.__duration  = self.__LoadProperty(cur, "duration", float)
            self.__aspect    = self.__LoadProperty(cur, "aspect", float, 16.0 / 9.0)
        
        cur.close()
        self.__pictures = picList
        self.__filename = filename
        return True
    
    def __LoadSafe(self, row, colName, default):
        try:
            return row[colName]
        except IndexError:
            return default
        
    def __LoadProperty(self, cur, propName, typ, default=None):
        cur.execute("select value from `property` where name=?", (propName, ))
        result = cur.fetchone()
        if result:
            return typ(result[0])
        else:
            return default
        
    def __PicToQuery(self, tableName, pic, includePic):
        if includePic:
            fd = open(pic.GetFilename(), 'rb')
            picData = buffer(fd.read())
            fd.close()
        else:
            picData = None
        
        query = "INSERT INTO `%s` (filename, width, height, " \
                                  "start_left, start_top, start_width, start_height, " \
                                  "target_left, target_top, target_width, target_height, " \
                                  "rotation, duration, comment, effect, data) " \
                                  "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);" % tableName

        values =  (pic.GetFilename(), pic.GetWidth(), pic.GetHeight(),
                   pic.GetStartRect()[0], pic.GetStartRect()[1], pic.GetStartRect()[2], pic.GetStartRect()[3],
                   pic.GetTargetRect()[0], pic.GetTargetRect()[1], pic.GetTargetRect()[2], pic.GetTargetRect()[3],
                   pic.GetRotation(), pic.GetDuration(), pic.GetComment(), pic.GetEffect(), picData)
        return query, values

    def __CreateSchema(self, conn):
        query = "CREATE TABLE `picture` (picture_id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                                        "filename TEXT," \
                                        "width INTEGER," \
                                        "height INTEGER," \
                                        "start_left INTEGER, " \
                                        "start_top INTEGER, " \
                                        "start_width INTEGER, " \
                                        "start_height INTEGER, " \
                                        "target_left INTEGER, " \
                                        "target_top INTEGER, " \
                                        "target_width INTEGER, " \
                                        "target_height INTEGER, " \
                                        "rotation INTEGER, " \
                                        "duration DOUBLE, " \
                                        "comment TEXT, " \
                                        "effect INTEGER, "\
                                        "data BLOB);\n" \
                "CREATE TABLE `property` (property_id INTEGER PRIMARY KEY AUTOINCREMENT, "\
                                         "name TEXT," \
                                         "value TEXT);\n"
        conn.executescript(query)
        
    
    def Save(self, filename, includePics=False):
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        if os.path.exists(filename):
            os.remove(filename)
        
        conn = sqlite3.connect(Encode(filename), detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.__CreateSchema(conn)

        cur = conn.cursor()
        for pic in self.__pictures:
            query, values = self.__PicToQuery('picture', pic, includePics)
            cur.execute(query, values)
        
        query = "INSERT INTO `property` (name, value) VALUES (?, ?);"
        for name, value in [('rev', self.REV),
                            ('audiofile', self.__audioFile),
                            ('aspect', self.__aspect),
                            ('duration', self.__duration)]:
            if value is not None:
                cur.execute(query, (name, value))
        
        conn.commit()
        cur.close()

        self.__filename = filename


class UserInteractionHandler(object):
    
    def GetAltPath(self, imgPath):
        return imgPath
    