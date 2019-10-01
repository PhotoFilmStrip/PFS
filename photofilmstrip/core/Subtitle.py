# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2010 Jens Goepfert
#

import codecs
import os


class SubtitleSrt(object):

    def __init__(self, outFile, factor=1.0):
        self.__outFile = outFile
        self.__index = 0
        self.__curTime = 0.0
        self.__factor = factor

    def __FormatTime(self, totalSecs):
        hours = int(totalSecs / 3600.0)
        minutes = int(totalSecs / 60.0) % 60
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
        if self.__outFile is None:
            return
        fd = codecs.open(self.__outFile + ".srt", 'w', "utf-8", "replace")
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
    p1.SetDuration(25)

    p2 = Picture(None)
    p2.SetComment("this is my second picture")
    p2.SetDuration(10)

    p3 = Picture(None)
    p3.SetComment("this is my third picture")
    p3.SetDuration(20)

    p4 = Picture(None)
    p4.SetComment("this is my third picture")
    p4.SetDuration(3740)

    s = SubtitleSrt("output")
    s.Start([p1, p2, p3, p4])


def testRead():
    stp = SrtParser('output.srt', 25.0)

    for f in range(800):
        print(f, stp.Get(f))


if __name__ == "__main__":
    testWrite()
    testRead()
