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
import sqlite3

from lib.common.ObserverPattern import Observable

from core.Picture import Picture


class PhotoFilmStrip(Observable):
    
    def __init__(self):
        Observable.__init__(self)
        
        self.__pictures = []
        
    def GetPictures(self):
        return self.__pictures
    
    def SetPictures(self, picList):
        self.__pictures = picList
    
    def Load(self, filename):
        conn = sqlite3.connect(filename, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = conn.cursor()
        cur.row_factory = sqlite3.Row
        cur.execute("select * from `picture`")
        resultSet = cur.fetchall()
        
        import wx
        picList = []
        for row in resultSet:
            if os.path.exists(row["filename"]):
                pic = Picture(row["filename"])
                rect = wx.Rect(row["start_left"], row["start_top"], row["start_width"], row["start_height"])
                pic.SetStartRect(rect)
                rect = wx.Rect(row["target_left"], row["target_top"], row["target_width"], row["target_height"])
                pic.SetTargetRect(rect)
                pic.SetDuration(row["duration"])
                pic.SetComment(row["comment"])
                pic.SetRotation(row['rotation'])
                picList.append(pic)
            else:
                # TODO: insert dummy-picture 
                print 'Imagefile not found:', row["filename"]
        
        cur.close()
        self.__pictures = picList
        
    def __PicToQuery(self, tableName, pic):
        query = "INSERT INTO `%s` (filename, " \
                                  "start_left, start_top, start_width, start_height, " \
                                  "target_left, target_top, target_width, target_height, " \
                                  "rotation, duration, comment) " \
                                  "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);" % tableName

        values =  (pic.GetFilename(), 
                   pic.GetStartRect()[0], pic.GetStartRect()[1], pic.GetStartRect()[2], pic.GetStartRect()[3],
                   pic.GetTargetRect()[0], pic.GetTargetRect()[1], pic.GetTargetRect()[2], pic.GetTargetRect()[3],
                   pic.GetRotation(), pic.GetDuration(), pic.GetComment())
        return query, values

    def __CreateSchema(self, conn):
        query = "CREATE TABLE `picture` (picture_id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                                        "filename TEXT," \
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
                                        "comment_align INTEGER);\n"
        query += "CREATE TABLE `effect` (effect_id INTEGER PRIMARY KEY AUTOINCREMENT, " \
                                        "picture_id INTEGER," \
                                        "effect INTEGER);\n"
        conn.executescript(query)
        
    
    def Save(self, filename, includePics=False):
        if os.path.exists(filename):
            os.remove(filename)
        
        conn = sqlite3.connect(filename, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.__CreateSchema(conn)

        cur = conn.cursor()
        for pic in self.__pictures:
            query, values = self.__PicToQuery('picture', pic)
            cur.execute(query, values)
        conn.commit()
        cur.close()
        
    def Render(self, renderer, path):
        renderer.Start(self.GetPictures(), path)
