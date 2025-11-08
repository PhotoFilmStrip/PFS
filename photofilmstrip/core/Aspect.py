# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2010 Jens Goepfert
#


class Aspect:

    ASPECT_5_4 = "5:4"
    ASPECT_4_3 = "4:3"
    ASPECT_3_2 = "3:2"
    ASPECT_16_9 = "16:9"
    ASPECT_16_10 = "16:10"
    ASPECT_21_9 = "21:9"
    ASPECT_4_5 = "4:5"
    ASPECT_3_4 = "3:4"
    ASPECT_2_3 = "2:3"
    ASPECT_9_16 = "9:16"
    ASPECT_10_16 = "10:16"
    ASPECT_1_1 = "1:1"

    @classmethod
    def ToFloat(cls, aspect):
        if aspect == cls.ASPECT_21_9:
            return 21.0 / 9.0
        if aspect == cls.ASPECT_16_10:
            return 16.0 / 10.0
        if aspect == cls.ASPECT_16_9:
            return 16.0 / 9.0
        if aspect == cls.ASPECT_5_4:
            return 5.0 / 4.0
        if aspect == cls.ASPECT_4_3:
            return 4.0 / 3.0
        if aspect == cls.ASPECT_3_2:
            return 3.0 / 2.0
        if aspect == cls.ASPECT_1_1:
            return 1.0
        if aspect == cls.ASPECT_10_16:
            return 10.0 / 16.0
        if aspect == cls.ASPECT_9_16:
            return 9.0 / 16.0
        if aspect == cls.ASPECT_4_5:
            return 4.0 / 5.0
        if aspect == cls.ASPECT_3_4:
            return 3.0 / 4.0
        if aspect == cls.ASPECT_2_3:
            return 2.0 / 3.0

    @classmethod
    def AsStr(cls, aspect):
        if aspect == cls.ASPECT_21_9:
            return "21/9"
        if aspect == cls.ASPECT_16_10:
            return "16/10"
        if aspect == cls.ASPECT_16_9:
            return "16/9"
        if aspect == cls.ASPECT_5_4:
            return "5/4"
        if aspect == cls.ASPECT_4_3:
            return "4/3"
        if aspect == cls.ASPECT_3_2:
            return "3/2"
        if aspect == cls.ASPECT_10_16:
            return "10/16"
        if aspect == cls.ASPECT_9_16:
            return "9/16"
        if aspect == cls.ASPECT_4_5:
            return "4/5"
        if aspect == cls.ASPECT_3_4:
            return "3/4"
        if aspect == cls.ASPECT_2_3:
            return "2/3"

    @classmethod
    def ToPortraitMode(cls, aspect):
        if aspect == cls.ASPECT_16_10:
            return cls.ASPECT_10_16
        if aspect == cls.ASPECT_16_9:
            return cls.ASPECT_9_16
        if aspect == cls.ASPECT_5_4:
            return cls.ASPECT_4_5
        if aspect == cls.ASPECT_4_3:
            return cls.ASPECT_3_4
        if aspect == cls.ASPECT_3_2:
            return cls.ASPECT_2_3
        raise ValueError("Not a valid landscape aspect string!")

    @classmethod
    def IsPortraitMode(cls, aspect):
        return aspect in (cls.ASPECT_10_16, cls.ASPECT_9_16,
                          cls.ASPECT_4_5,
                          cls.ASPECT_3_4, cls.ASPECT_2_3)
