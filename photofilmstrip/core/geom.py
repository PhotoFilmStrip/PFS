# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2018 Jens Goepfert
#

class Point:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "Point({}, {})".format(self.x, self.y)

    def __repr__(self):
        return str(self)

    def __iter__(self):
        yield self.x
        yield self.y


class Rect:

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.ratio = width / height

    def __str__(self):
        return "Rect({}, {})".format(self.width, self.height)

    def __repr__(self):
        return str(self)

    def __iter__(self):
        yield self.width
        yield self.height

    def ApplyWidth(self, targetRect):
        return Rect(targetRect.width, targetRect.width / self.ratio)

    def ApplyHeight(self, targetRect):
        return Rect(targetRect.height * self.ratio, targetRect.height)

    def Invert(self):
        return Rect(self.height, self.width)

    def FitInside(self, targetRect):
        new_width = targetRect.height * self.ratio
        if new_width <= targetRect.width:
            result = Rect(new_width, targetRect.height)
        else:
            new_height = targetRect.width / self.ratio
            result = Rect(targetRect.width, new_height)
        return result

    def AlignCenter(self, targetRect):
        new_x = (targetRect.width - self.width) / 2
        new_y = (targetRect.height - self.height) / 2
        return Point(new_x, new_y)
