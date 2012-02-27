# encoding: UTF-8

import logging
import os
import random
import sqlite3

from photofilmstrip.lib.util import Encode

from photofilmstrip.core import PILBackend
from photofilmstrip.core.Aspect import Aspect
from photofilmstrip.core.Picture import Picture

from photofilmstrip.gui.util.ImageCache import ImageCache # FIXME: no gui import here
from photofilmstrip.core.Project import Project


SCHEMA_REV = 3
"""
3:
- added thumbnail table
2:
- added property table
1:
- initial
"""


SCHEMA = """
CREATE TABLE `picture` (
    picture_id INTEGER PRIMARY KEY AUTOINCREMENT,
    filename TEXT,
    width INTEGER,
    height INTEGER,
    start_left INTEGER, 
    start_top INTEGER,
    start_width INTEGER,
    start_height INTEGER,
    target_left INTEGER,
    target_top INTEGER,
    target_width INTEGER,
    target_height INTEGER,
    rotation INTEGER,
    duration DOUBLE,
    comment TEXT,
    effect INTEGER,
    transition INTEGER,
    transition_duration DOUBLE,
    data BLOB
);

CREATE TABLE `property` (
    property_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    value TEXT
);

CREATE TABLE `thumbnail` (
    thumbnail_id INTEGER PRIMARY KEY AUTOINCREMENT,
    picture_id INTEGER,
    width INTEGER,
    height INTEGER,
    data BLOB,
    FOREIGN KEY(picture_id) REFERENCES picture(picture_id) ON DELETE CASCADE
);
"""

class ProjectFile(object):
    def __init__(self, project=None, filename=None):
        self._project = project
        self._filename = filename
#        project.GetFilename()
        
        self.__conn = None
        self.__altPaths = {}
        
    def __del__(self):
        if self.__conn is not None:
            logging.debug("database not closed properly: %s", self._filename)
            self.__conn.close()

    def GetProject(self):
        return self._project
    
    def __Connect(self):
        if self.__conn is None:
            self.__conn = sqlite3.connect(Encode(self._filename),
                                          detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
            
    def __Close(self, commit=False):
        if self.__conn is None:
            raise RuntimeError("not connected")
        if commit:
            self.__conn.commit()
        self.__conn.close()
        self.__conn = None
    
    def __GetCursor(self):
        if self.__conn is None:
            raise RuntimeError("not connected")
        cur = self.__conn.cursor()
        cur.row_factory = sqlite3.Row
        return cur
    
    def GetPicCount(self):
        self.IsOk()
        self.__Connect()
        try:
            try:
                cur = self.__GetCursor()
                cur.execute("SELECT COUNT(*) FROM `picture`")
                return cur.fetchone()[0]
            except sqlite3.DatabaseError:
                return 0
        finally:
            self.__Close()
        return -1
    
    def GetPreviewThumb(self):
        if not self.Load():
            return None
        
        img = None
        pics = self._project.GetPictures()
        imgCount = len(pics)
        if imgCount > 0:
            picIdx = random.randint(0, imgCount - 1)
            pic = pics[picIdx]
            if os.path.exists(pic.GetFilename()):
                img = PILBackend.GetThumbnail(pic, 64, 64)
                if pic.IsDummy():
                    img = None
        return img
    
    def IsOk(self):
        self.__Connect()
        try:
            try:
                cur = self.__GetCursor()
                cur.execute("SELECT * FROM `picture`")
                return True
            except sqlite3.DatabaseError:
                return False
            except sqlite3.DatabaseError, err:
                logging.debug("IsOk(%s): %s", self._filename, err)
                return False
            except BaseException, err:
                logging.debug("IsOk(%s): %s", self._filename, err)
                return False
            return False
        finally:
            self.__Close()

# save methods
    def __PicToQuery(self, pic, includePics):
        if includePics:
            fd = open(pic.GetFilename(), 'rb')
            picData = buffer(fd.read())
            fd.close()
        else:
            picData = None
            
        query = "INSERT INTO `picture` (" \
                    "filename, width, height, " \
                    "start_left, start_top, start_width, start_height, " \
                    "target_left, target_top, target_width, target_height, " \
                    "rotation, duration, comment, effect, " \
                    "transition, transition_duration, data" \
                ") VALUES (" \
                    "?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?" \
                ");"

        values =  (pic.GetFilename(), pic.GetWidth(), pic.GetHeight(),
                   pic.GetStartRect()[0], pic.GetStartRect()[1], pic.GetStartRect()[2], pic.GetStartRect()[3],
                   pic.GetTargetRect()[0], pic.GetTargetRect()[1], pic.GetTargetRect()[2], pic.GetTargetRect()[3],
                   pic.GetRotation(), pic.GetDuration(), pic.GetComment(), pic.GetEffect(), 
                   pic.GetTransition(), pic.GetTransitionDuration(rawValue=True), 
                   picData)
        return query, values
    
    def __ThumbToQuery(self, picId, pic):
        pilThumb = PILBackend.GetThumbnail(pic, height=120)
        thumbWidth, thumbHeight = pilThumb.size
        thumbData = buffer(pilThumb.tostring())
        
        query = "INSERT INTO `thumbnail` (" \
                    "picture_id, width, height, data" \
                ") VALUES (" \
                    "?, ?, ?, ?" \
                ");"
        values = (picId, thumbWidth, thumbHeight, thumbData)
        return query, values 
    
    def _StepProgress(self, msg):
        pass

    def Save(self, includePics=False):
        dirname = os.path.dirname(self._filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        if os.path.exists(self._filename):
            os.remove(self._filename)
        
        self.__Connect()
        cur = self.__GetCursor()
        cur.executescript(SCHEMA)    

        cur = self.__GetCursor()
        for pic in self._project.GetPictures():
            self._StepProgress(_(u"Saving '%s' ...") % pic.GetFilename())
            query, values = self.__PicToQuery(pic, includePics)
            cur.execute(query, values)
            
            query, values = self.__ThumbToQuery(cur.lastrowid, pic)
            cur.execute(query, values)
        
        query = "INSERT INTO `property` (name, value) VALUES (?, ?);"
        for name, value in [('rev', SCHEMA_REV),
                            ('audiofile', self._project.GetAudioFile()),
                            ('aspect', self._project.GetAspect()),
                            ('duration', self._project.GetDuration(False))]:
            if value is not None:
                cur.execute(query, (name, value))
        
        self.__Close(commit=True)
        
        self._project.SetFilename(self._filename)

# load methods
    def _SelectAlternatePath(self, imgPath):
        pass

    def Load(self, importPath=None):
        filename = self._filename
        if not os.path.isfile(filename):
            return False
        
        self.__Connect()
        cur = self.__GetCursor()

        fileRev = 1
        try:
            # at the beginning we had no property table
            cur.execute("SELECT value FROM `property` WHERE name=?", ("rev", ))
            result = cur.fetchone()
            if result:
                fileRev = int(result[0])
        except sqlite3.DatabaseError:
            pass
        
        try:
            cur.execute("SELECT * FROM `picture`")
        except sqlite3.DatabaseError:
            self.__Close()
            return False
        
        picList = []
        for row in cur:
            imgFile = row["filename"]
            imgPath = os.path.dirname(imgFile)
            self._StepProgress(_(u"Loading '%s' ...") % (os.path.basename(imgFile)))

            picData = self.__LoadSafe(row, 'data', None)
            if picData is None:
                if not (os.path.exists(imgPath) and os.path.isfile(imgFile)):
                    if not self.__altPaths.has_key(imgPath):
                        self._SelectAlternatePath(imgPath)
                        
                    imgFile = os.path.join(self.__altPaths.get(imgPath, imgPath), 
                                           os.path.basename(imgFile))
                
                pic = Picture(imgFile)

            else:
                if importPath is None:
                    importPath = os.path.dirname(filename)
                    
                tmpImg = os.path.join(importPath, os.path.basename(imgFile))
                if os.path.isfile(tmpImg):
                    logging.debug('file exists: %s', tmpImg)
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

            pic.SetTransition(self.__LoadSafe(row, 'transition', Picture.TRANS_FADE))
            pic.SetTransitionDuration(self.__LoadSafe(row, 'transition_duration', 1.0))
            
            self.__LoadThumbnail(fileRev, pic, row["picture_id"])
            
            picList.append(pic)

        project = Project(self._filename)
        project.SetPictures(picList)
        if fileRev >= 2:
            project.SetAudioFile(self.__LoadProperty(cur, "audiofile", unicode))
            project.SetDuration(self.__LoadProperty(cur, "duration", float))
            project.SetAspect(self.__LoadProperty(cur, "aspect", unicode, Aspect.ASPECT_16_9))
        
        self.__Close()
        
        self._project = project
        return True
    
    def __LoadThumbnail(self, fileRev, pic, picId):
        ImageCache().RegisterPicture(pic)
        return
        thumbNail = None
        if fileRev >= 3:
            cur = self.__GetCursor()
            cur.execute("SELECT * FROM `thumbnail` WHERE picture_id=?", (picId, ))
            row = cur.fetchone()
            if row:
                thumbWidth = row["width"]
                thumbHeight = row["height"] 
                thumbData = row["data"]
                thumbNail = PILBackend.ImageFromBuffer((thumbWidth, thumbHeight), thumbData)
        if thumbNail is None:
            thumbNail = PILBackend.GetThumbnail(pic, height=120)
        ImageCache().RegisterPicture(pic, thumbNail)

    def __LoadSafe(self, row, colName, default):
        try:
            return row[colName]
        except IndexError:
            return default
        
    def __LoadProperty(self, cur, propName, typ, default=None):
        cur.execute("SELECT value FROM `property` WHERE name=?", (propName, ))
        result = cur.fetchone()
        if result:
            return typ(result[0])
        else:
            return default
    
    def SetAltPath(self, imgPath, path):
        self.__altPaths[imgPath] = path
