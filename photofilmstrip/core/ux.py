# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2018 Jens Goepfert
#


class Ux:
    '''
    Entity for user experience information
    '''

    def __init__(self):
        self.uxEvents = []

    def AddUxEvent(self, uxEvent):
        self.uxEvents.append(uxEvent)

    def GetUxEvents(self):
        return self.uxEvents
