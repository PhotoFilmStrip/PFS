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
import logging
import sqlite3

from lib.common.ObserverPattern import Observable

from core.Picture import Picture, DummyPicture
from core.ProgressHandler import ProgressHandler


class PhotoFilmStrip(Observable):
    
    def __init__(self):
        Observable.__init__(self)
        
        self.__pictures = []
        self.__uiHandler = UserInteractionHandler()
        self.__progressHandler = ProgressHandler()
        
    def GetPictures(self):
        return self.__pictures
    
    def SetPictures(self, picList):
        self.__pictures = picList
        
    def SetUserInteractionHandler(self, uiHdl):
        self.__uiHandler = uiHdl
        
    def SetProgressHandler(self, progressHandler):
        self.__progressHandler = progressHandler
    
    def Load(self, filename, importPath=None):
        if not os.path.isfile(filename):
            return False
        conn = sqlite3.connect(filename, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = conn.cursor()
        cur.row_factory = sqlite3.Row
        cur.execute("select * from `picture`")
        resultSet = cur.fetchall()
        
        self.__progressHandler.SetMaxProgress(len(resultSet))
        
        import wx
        picList = []
        altPaths = {}
        for row in resultSet:
            imgFile = row["filename"]
            imgPath = os.path.dirname(imgFile)
            self.__progressHandler.Step(_(u"Loading '%s' ...") % (os.path.basename(imgFile)))
            
            picData = row['data']
            if picData is None:
                if not (os.path.exists(imgPath) and os.path.isfile(imgFile)):
                    if altPaths.has_key(imgPath):
                        altPath = altPaths[imgPath]
                    else:
                        altPath = self.__uiHandler.GetAltPath(imgPath)
                        altPaths[imgPath] = altPath
                        
                    imgFile = os.path.join(altPaths[imgPath], os.path.basename(imgFile))
                
                if os.path.isfile(imgFile):
                    pic = Picture(imgFile)
                else:
                    logging.warn("Imagefile '%s' not found:", imgFile)
                    pic = DummyPicture(row["filename"])
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
            
            rect = wx.Rect(row["start_left"], row["start_top"], row["start_width"], row["start_height"])
            pic.SetStartRect(rect)
            rect = wx.Rect(row["target_left"], row["target_top"], row["target_width"], row["target_height"])
            pic.SetTargetRect(rect)
            pic.SetDuration(row["duration"])
            pic.SetComment(row["comment"])
            pic.SetRotation(row['rotation'])
            
            pic.SetEffect(self.__LoadSafe(row, 'effect', Picture.EFFECT_NONE))
            pic.SetWidth(self.__LoadSafe(row, 'width', -1))
            pic.SetHeight(self.__LoadSafe(row, 'height', -1))

            picList.append(pic)
        
        cur.close()
        self.__pictures = picList
        
        return True
    
    def __LoadSafe(self, row, colName, default):
        try:
            return row[colName]
        except IndexError:
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
                                        "data BLOB);\n"
        conn.executescript(query)
        
    
    def Save(self, filename, includePics=False):
        if os.path.exists(filename):
            os.remove(filename)
        
        conn = sqlite3.connect(filename, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.__CreateSchema(conn)

        cur = conn.cursor()
        for pic in self.__pictures:
            query, values = self.__PicToQuery('picture', pic, includePics)
            cur.execute(query, values)
        conn.commit()
        cur.close()


class UserInteractionHandler(object):
    
    def GetAltPath(self, imgPath):
        return imgPath
    