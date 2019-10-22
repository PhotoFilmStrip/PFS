# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2019 Jens Goepfert
#

import json
import logging
import os
import sqlite3

from photofilmstrip.core.Story import Story
from photofilmstrip.core.Media import Media

SCHEMA_REV = 1
"""
1:
- initial
"""

SCHEMA = """
CREATE TABLE `media` (
    media_id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_media_id INTEGER,
    filename TEXT,
    settings TEXT
);

CREATE TABLE `property` (
    property_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    value TEXT
);
"""


class StoryFile(object):

    def __init__(self, story=None, filename=None):
        self._story = story
        self._filename = filename

        self.__conn = None
        self.__fileRev = 1

    def __del__(self):
        if self.__conn is not None:
            logging.debug("database not closed properly: %s", self._filename)
            self.__conn.close()

    def __Connect(self):
        if self.__conn is None:
            self.__conn = sqlite3.connect(self._filename,
                                          detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        cur = self.__GetCursor()
        try:
            cur.execute("SELECT value FROM `property` WHERE name=?", ("rev",))
            result = cur.fetchone()
            if result:
                self.__fileRev = int(result[0])
        except sqlite3.DatabaseError:
            pass

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

    def __MediaToQuery(self, parentId, media):
        query = "INSERT INTO `media` (" \
                    "parent_media_id, filename, settings" \
                ") VALUES (" \
                    "?, ?, ?" \
                ");"

        values = (parentId, media.GetFilename(),
                  json.dumps(media.GetProperties()))
        return query, values

    def __LoadProperty(self, cur, propName, typ, default=None):
        cur.execute("SELECT value FROM `property` WHERE name=?", (propName,))
        result = cur.fetchone()
        if result:
            return typ(result[0])
        else:
            return default

    def GetStory(self):
        return self._story

    def IsOk(self):
        self.__Connect()
        try:
            try:
                cur = self.__GetCursor()
                cur.execute("SELECT * FROM `media`")
                return True
            except BaseException as err:
                logging.debug("IsOk(%s): %s", self._filename, err)
                return False
        finally:
            self.__Close()

    def Save(self):
        dirname = os.path.dirname(self._filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        if os.path.exists(self._filename):
            os.remove(self._filename)

        self.__Connect()
        cur = self.__GetCursor()
        cur.executescript(SCHEMA)

        cur = self.__GetCursor()
        for media in self._story.GetMedias():
            query, values = self.__MediaToQuery(None, media)
            cur.execute(query, values)
            ident = cur.lastrowid

            for subMedia in media.GetChildren():
                query, values = self.__MediaToQuery(ident, subMedia)
                cur.execute(query, values)

        query = "INSERT INTO `property` (name, value) VALUES (?, ?);"
        for name, value in [('rev', SCHEMA_REV)]:
            cur.execute(query, (name, value))

        self.__Close(commit=True)

        self._story.SetFilename(self._filename)

    def Load(self):
        filename = self._filename
        if not os.path.isfile(filename):
            return False

        self.__Connect()
        cur = self.__GetCursor()

#         fileRev = self.__LoadProperty(cur, "rev", int, 1)

        try:
            cur.execute("SELECT * FROM `media` ORDER BY parent_media_id, media_id")
        except sqlite3.DatabaseError:
            self.__Close()
            return False

        medias = []
        idMediaMap = {}
        for row in cur:
            mediaFile = row["filename"]
            mediaSettings = row["settings"]

            media = Media(mediaFile)
            if mediaSettings:
                props = json.loads(mediaSettings)
                for key, value in props.items():
                    media.SetProperty(key, value)

            if row["parent_media_id"] is None:
                medias.append(media)
            else:
                parentMedia = idMediaMap[row["parent_media_id"]]
                parentMedia.AddChild(media)

            idMediaMap[row["media_id"]] = media

        story = Story(self._filename)
        story.SetMedias(medias)

        self.__Close()

        self._story = story
        return True
