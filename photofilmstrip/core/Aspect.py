# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2010 Jens Goepfert
#


class Aspect:

    ASPECT_4_3 = "4:3"
    ASPECT_3_2 = "3:2"
    ASPECT_16_9 = "16:9"
    ASPECT_16_10 = "16:10"

    @classmethod
    def ToFloat(cls, aspect):
        if aspect == cls.ASPECT_16_10:
            return 16.0 / 10.0
        if aspect == cls.ASPECT_16_9:
            return 16.0 / 9.0
        if aspect == cls.ASPECT_4_3:
            return 4.0 / 3.0
        if aspect == cls.ASPECT_3_2:
            return 3.0 / 2.0
