#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2019 Jens Goepfert
#

import unittest

import os
import io
import tempfile

from photofilmstrip.core.Subtitle import SrtParser

SRT_DATA = """
1
00:00:00,000 --> 00:00:17,309
Cooles Auto

2
00:00:19,781 --> 00:00:37,090
Kleine süße Schweine

3
00:00:39,563 --> 00:00:56,872
*Schnacksel*
*schnurksel*
+pieksel+

4
00:00:59,345 --> 00:01:16,654
Uuuh uuuh aaah

5
00:01:19,127 --> 00:01:36,436
Großstadtrevier

6
00:01:38,909 --> 00:01:56,218
!"§$%&/()=?
+++ cool ---

7
00:01:58,690 --> 00:02:16,000
14.08.2020
<b>fett</b>
*format*

"""


class TestGeom(unittest.TestCase):

    def setUp(self):
        td = tempfile.gettempdir()
        self.tmpFilename = os.path.join(td, "test.srt")

        tmpFile = io.open(self.tmpFilename, "w", encoding="utf-8", newline="\n")
        tmpFile.write(SRT_DATA)
        tmpFile.close()

    def tearDown(self):
        os.remove(self.tmpFilename)

    def test1(self):
        sp = SrtParser(self.tmpFilename, 25.0)
        sp.Parse()

        self.assertEqual(sp.Get(400), "Cooles Auto")
        self.assertEqual(sp.Get(432), "Cooles Auto")

        self.assertEqual(sp.Get(433), "")

        self.assertEqual(sp.Get(479), "")
        self.assertNotEqual(sp.Get(480), "Großstadtrevier")
        self.assertNotEqual(sp.Get(494), "Großstadtrevier")
        self.assertEqual(sp.Get(495), "Kleine süße Schweine")


if __name__ == "__main__":
    unittest.main()

