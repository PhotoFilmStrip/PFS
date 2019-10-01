# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2018 Jens Goepfert
#

import logging

from photofilmstrip.lib.DestructionManager import Destroyable
import importlib


class UxService(Destroyable):

    __instance = None

    @classmethod
    def GetInstance(cls):
        if cls.__instance is None:
            cls.__instance = UxService()
        return cls.__instance

    def __init__(self):
        Destroyable.__init__(self)

        self.uxAdapters = []

        for modname in ("gnome", "uwp"):
            try:
                ux_module = importlib.import_module("photofilmstrip.ux." + modname)
            except:
                logging.getLogger('UxService').debug(
                    "importing UxAdapter '%s' failed", modname, exc_info=1)
                continue

            if hasattr(ux_module, "ux_init"):
                try:
                    uxAdapter = getattr(ux_module, "ux_init")()
                    if isinstance(uxAdapter, UxAdapter):
                        self.uxAdapters.append(uxAdapter)
                except:
                    logging.getLogger('UxService').error(
                        "initializing UxAdapter '%s' failed", ux_module, exc_info=1)

    def Initialize(self):
        for uxAdapter in self.uxAdapters:
            uxAdapter.OnInit()

    def Start(self):
        for uxAdapter in self.uxAdapters:
            uxAdapter.OnStart()

    def Destroy(self):
        for uxAdapter in self.uxAdapters:
            uxAdapter.OnDestroy()


class UxAdapter:

    def OnInit(self):
        '''
        Triggers on right before GUI is started.
        '''
        raise NotImplementedError()

    def OnStart(self):
        '''
        Triggers right after the process has started. Raise 
        PreventStartupSignal if startup may be prevented
        '''
        pass

    def OnDestroy(self):
        '''
        Triggers on shut down to clean up stuff.
        '''
        pass


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


class UxPreventStartupSignal(Exception):
    pass

