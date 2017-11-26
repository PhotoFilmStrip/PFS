# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2010 Jens Goepfert
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

import codecs
import os


class SubtitleSrt(object):

    def __init__(self, outputPath, factor=1.0):
        self.__outputPath = outputPath
        self.__index = 0
        self.__curTime = 0.0
        self.__factor = factor

    def __FormatTime(self, totalSecs):
        minutes = int(totalSecs / 60.0)
        hours = int(minutes / 60.0)
        seconds = int(totalSecs) % 60
        frac = int((totalSecs - int(totalSecs)) * 1000.0)
        return "%02d:%02d:%02d,%03d" % (hours, minutes, seconds, frac)

    def __GetPicDuration(self, pic):
        return pic.GetDuration() * self.__factor

    def __ProcessPic(self, pic):
        start = self.__FormatTime(self.__curTime)
        end = self.__FormatTime(self.__curTime + self.__GetPicDuration(pic))

        result = u"%(idx)d\n" \
                 u"%(start)s --> %(end)s\n" \
                 u"%(text)s\n" \
                 u"\n" % {'idx': self.__index,
                          'start': start,
                          'end': end,
                          'text': pic.GetComment().strip()}

        return result

    def Start(self, pics):
        if self.__outputPath is None:
            return
        fd = codecs.open(os.path.join(self.__outputPath, "output.srt"), 'w', "utf-8", "replace")
        fd.write(codecs.BOM_UTF8.decode("utf-8"))
        for pic in pics:
            self.__index += 1

            data = self.__ProcessPic(pic)
            fd.write(data)

            self.__curTime += self.__GetPicDuration(pic) + \
                              (pic.GetTransitionDuration() * self.__factor)

        fd.close()


class SrtParser(object):

    def __init__(self, path, framerate):
        self.__path = path
        self.__framerate = framerate

        self.__data = []

        if os.path.exists(self.__path):
            self.Parse()

    def Parse(self):
        fd = codecs.open(self.__path, 'r', "utf-8")
        fd.read(len(codecs.BOM_UTF8.decode("utf-8")))
        try:
            while 1:
                lineIdx = fd.readline()
                try:
                    _idx = int(lineIdx.strip())
                except:
                    break

                lineTime = fd.readline()
                start = self.__ParseTime(lineTime[:12])
                end = self.__ParseTime(lineTime[17:])
                lineTxt = []
                while 1:
                    _line = fd.readline().rstrip()
                    if _line:
                        lineTxt.append(_line)
                    else:
                        break

                self.__data.append((start, end, "\n".join(lineTxt)))
        finally:
            fd.close()

    def __ParseTime(self, text):
        hours = int(text[:2])
        minutes = int(text[3:5])
        seconds = float(text[6:].replace(",", "."))

        millis = ((((hours * 60) + minutes) * 60) + seconds * 1000.0)

        return millis

    def Get(self, pic):
        msec = pic * (1.0 / self.__framerate) * 1000.0
        for start, end, text in self.__data:
            if msec >= start and msec <= end:
                return text
        return ""


def testWrite():
    from photofilmstrip.core.Picture import Picture
    p1 = Picture(None)
    p1.SetComment("this is my first picture")
    p1.SetDuration(7)

    p2 = Picture(None)
    p2.SetComment("this is my second picture")
    p2.SetDuration(12)

    p3 = Picture(None)
    p3.SetComment("this is my third picture")
    p3.SetDuration(2)

    s = SubtitleSrt(".")
    s.Start([p1, p2, p3])


def testRead():
    stp = SrtParser('output.srt', 25.0)

    for f in xrange(800):
        print f, stp.Get(f)


if __name__ == "__main__":
    testRead()
