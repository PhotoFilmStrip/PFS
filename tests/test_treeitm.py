# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2018 Jens Goepfert
#

import unittest

from photofilmstrip.gui.PnlStory import TreeItm


class TestGeom(unittest.TestCase):

    def setUp(self):
        self.root = TreeItm()

        self.child1 = TreeItm()
        self.child2 = TreeItm()
        self.child3 = TreeItm()

        for idx in range(3):
            self.child1.Insert(idx, TreeItm())
            self.child2.Insert(idx, TreeItm())
            self.child3.Insert(idx, TreeItm())

        self.root.Insert(0, self.child1)
        self.root.Insert(1, self.child2)
        self.root.Insert(2, self.child3)

    def testIndex3(self):
        idx = self.child3.Index()
        self.assertEqual(idx, 2)

    def testRow1(self):
        row = self.child1.Row()
        self.assertEqual(row, 1)

    def testRow2(self):
        row = self.child2.Row()
        self.assertEqual(row, 5)

    def testRow3(self):
        row = self.child3.Row()
        self.assertEqual(row, 9)

    def testRowLast(self):
        lastChild = self.child3.GetChildren()[-1]
        row = lastChild.Row()
        self.assertEqual(row, 12)


if __name__ == "__main__":
    unittest.main()
