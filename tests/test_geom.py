# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2018 Jens Goepfert
#

import unittest

from photofilmstrip.core.geom import Point, Rect


class TestGeom(unittest.TestCase):

    def setUp(self):
        self.tgt = Rect(1280, 720)
        self.point = Point(10, 20)
        self.src = Rect(1080, 1920)

    def testRectIter(self):
        w, h = self.tgt
        self.assertEqual(w, self.tgt.width)
        self.assertEqual(h, self.tgt.height)

    def testRectInvert(self):
        inv = self.tgt.Invert()
        self.assertEqual(inv.width, self.tgt.height)
        self.assertEqual(inv.height, self.tgt.width)

    def testPointIter(self):
        x, y = self.point
        self.assertEqual(x, self.point.x)
        self.assertEqual(y, self.point.y)

    def testRectApplyWidth(self):
        src_scale = self.src.ApplyWidth(self.tgt)
        self.assertEqual(src_scale.width, self.tgt.width)
        self.assertEqual(int(src_scale.height), 2275)

    def testRectApplyHeight(self):
        src_scale = self.src.ApplyHeight(self.tgt)
        self.assertEqual(src_scale.height, self.tgt.height)
        self.assertEqual(int(src_scale.width), 405)

    def testRectAlignCenter(self):
        r = Rect(1024, 768)
        src_pos = r.AlignCenter(self.tgt)
        self.assertEqual(src_pos.x, 128)
        self.assertEqual(int(src_pos.y), -24)

    def testRectFitInside(self):
        src_fit = self.src.FitInside(self.tgt)
        self.assertEqual(src_fit.width, 405)
        self.assertEqual(src_fit.height, 720)


if __name__ == "__main__":
    unittest.main()
