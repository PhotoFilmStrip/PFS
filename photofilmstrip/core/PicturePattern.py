# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2017 Jens Goepfert
#

import os
import re


class PicturePattern:

    @staticmethod
    def Create(path):
        result = None
        getnum = re.compile(r"(.*?)(\d+)([.].*)")
        match = getnum.match(os.path.basename(path))
        if match is None:
            result = PicturePattern()
        else:
            prefix = match.groups()[0]
            num = int(match.groups()[1])
            postfix = match.groups()[2]
            digits = len(match.groups()[1])
            result = PicturePattern(prefix, num, postfix, digits)
        return result

    def __init__(self, prefix=None, num=None, postfix=None, digits=None):
        self.prefix = prefix
        self.num = num
        self.postfix = postfix
        self.digits = digits

    def IsOk(self):
        return self.num is not None

