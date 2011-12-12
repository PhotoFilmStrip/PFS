# encoding: UTF-8

import logging
import os
import random
import sqlite3

from photofilmstrip.lib.util import Encode

from photofilmstrip.lib.jobimpl.VisualJob import VisualJob
from photofilmstrip.core import PILBackend
from photofilmstrip.core.Aspect import Aspect
from photofilmstrip.core.Picture import Picture

from photofilmstrip.gui.util.ImageCache import ImageCache
from photofilmstrip.core.Project import Project
from photofilmstrip.lib.jobimpl.WxVisualJobHandler import WxInteractionEvent


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


def CheckProject(filename):
    try:
        conn = sqlite3.connect(Encode(filename), detect_types=sqlite3.PARSE_DECLTYPES)
        cur = conn.cursor()
        cur.execute("SELECT * FROM `picture`")
    except sqlite3.DatabaseError, err:
        logging.debug("IsOk(%s): %s", filename, err)
        return False
    except BaseException, err:
        logging.debug("IsOk(%s): %s", filename, err)
        return False
    return True


def QuickInfo(filename):
    return 0, None
    prj = Project()
    prj.Load(filename)
    imgCount = len(prj.GetPictures())
    if imgCount > 0:
        picIdx   = random.randint(0, imgCount - 1)
    
    pic = prj.GetPictures()[picIdx]
    if os.path.exists(pic.GetFilename()):
        img = PILBackend.GetThumbnail(pic, 64, 64)
        if pic.IsDummy():
            img = None
    else:
        img = None

    return imgCount, img


class LoadJob(VisualJob):
    def __init__(self, project):
        VisualJob.__init__(self, "",
                           target=self.__Load)
        self.SetName(_("Loading project %s") % project.GetFilename())
        self.__project = project
        self.__altPaths = {}
        
    def _SelectAlternatePath(self, imgPath):
        sapEvent = SelectAlternatePathEvent(imgPath)
        self._Interact(sapEvent)

    def __Load(self, importPath=None, job=None):
        filename = self.__project.GetFilename()
        if not os.path.isfile(filename):
            return False
        
        conn = sqlite3.connect(Encode(filename), detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = conn.cursor()
        cur.row_factory = sqlite3.Row

        try:
            cur.execute("SELECT COUNT(*) FROM `picture`")
        except sqlite3.DatabaseError:
            return False
        picCount = cur.fetchone()[0]
        self.SetMaxProgress(picCount)
        
        fileRev = 1
        try:
            # at the beginning we had no property table
            cur.execute("SELECT value FROM `property` WHERE name=?", ("rev", ))
            result = cur.fetchone()
            if result:
                fileRev = int(result[0])
        except sqlite3.DatabaseError:
            pass
        
        if fileRev >= 2:
            self.__audioFile = self.__LoadProperty(cur, "audiofile", unicode)
            self.__duration  = self.__LoadProperty(cur, "duration", float)
            self.__aspect    = self.__LoadProperty(cur, "aspect", unicode, Aspect.ASPECT_16_9)
        
        try:
            cur.execute("SELECT * FROM `picture`")
        except sqlite3.DatabaseError:
            return False
        
        picList = []
        for row in cur:
            imgFile = row["filename"]
            imgPath = os.path.dirname(imgFile)
            self.StepProgress(_(u"Loading '%s' ...") % (os.path.basename(imgFile)))

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
            
            self.__LoadThumbnail(conn, fileRev, pic, row["picture_id"])
            
            picList.append(pic)

        cur.close()
        self.__project.SetPictures(picList)
        return True
    
    def __LoadThumbnail(self, conn, fileRev, pic, picId):
        ImageCache().RegisterPicture(pic)
        return
        thumbNail = None
        if fileRev >= 3:
            cur = conn.cursor()
            cur.row_factory = sqlite3.Row
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
    
    def GetProject(self):
        return self.__project
    
    def SetAltPath(self, imgPath, path):
        self.__altPaths[imgPath] = path

        
class SaveJob(VisualJob):

    def __init__(self, project, includePics=False):
        VisualJob.__init__(self, _("Saving project %s") % project.GetFilename(),
                           target=self.__Save)
        self.__project = project
        self.__filename = project.GetFilename()
        self.__pictures = project.GetPictures()
        self.__includePics = includePics
        
        self.SetMaxProgress(len(self.__pictures))
        
    def GetProject(self):
        return self.__project
    def GetIncludePics(self):
        return self.__includePics
        
    def __PicToQuery(self, pic):
        if self.__includePics:
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
                   pic.GetTransition(), pic.GetTransitionDuration(), 
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

    def __CreateSchema(self, conn):
        conn.executescript(SCHEMA)    
    
    def __Save(self, job=None):
        dirname = os.path.dirname(self.__filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        if os.path.exists(self.__filename):
            os.remove(self.__filename)
        
        conn = sqlite3.connect(Encode(self.__filename), 
                               detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        self.__CreateSchema(conn)

        cur = conn.cursor()
        for pic in self.__pictures:
            self.StepProgress(_(u"Saving '%s' ...") % pic.GetFilename())
            query, values = self.__PicToQuery(pic)
            cur.execute(query, values)
            
            query, values = self.__ThumbToQuery(cur.lastrowid, pic)
            cur.execute(query, values)
        
        query = "INSERT INTO `property` (name, value) VALUES (?, ?);"
        for name, value in [('rev', SCHEMA_REV),
                            ('audiofile', self.__project.GetAudioFile()),
                            ('aspect', self.__project.GetAspect()),
                            ('duration', self.__project.GetDuration(False))]:
            if value is not None:
                cur.execute(query, (name, value))
        
        conn.commit()
        cur.close()

#        self.__project.SetFilename(self.__filename)

import wx
from photofilmstrip.lib.Settings import Settings

class SelectAlternatePathEvent(WxInteractionEvent):
    
    def __init__(self, imgPath):
        WxInteractionEvent.__init__(self)
        self.__imgPath = imgPath
        
    def OnProcess(self, wxParent):
        dlg = wx.MessageDialog(wxParent,
                               _(u"Some images does not exist in the folder '%s' anymore. If the files has moved you can select the new path. Do you want to select a new path?") % self.__imgPath, 
                               _(u"Question"),
                               wx.YES_NO | wx.ICON_QUESTION)
        try:
            if dlg.ShowModal() == wx.ID_NO:
                self.GetJob().SetAltPath(self.__imgPath, self.__imgPath)
                return
        finally:
            dlg.Destroy()

        dlg = wx.DirDialog(wxParent, defaultPath=Settings().GetImagePath())
        try:
            if dlg.ShowModal() == wx.ID_OK:
                path = dlg.GetPath()
                self.GetJob().SetAltPath(self.__imgPath, path)
                return
            else:
                self.Skip()
        finally:
            dlg.Destroy()

