# encoding: UTF-8

import logging

from photofilmstrip.lib.common.Singleton import Singleton


class DestructionManager(Singleton):
    
    def __init__(self):
        self.__destroyables = []
        
    def AddDestroyable(self, destroyable):
        assert isinstance(destroyable, IDestroyable)
        self.__destroyables.append(destroyable)
        
    def Destroy(self):
        while self.__destroyables:
            dest = self.__destroyables.pop(0)
            try:
                dest.Destroy()
            except BaseException, exc:
                logging.debug("could not destroy '%s': %s", dest, exc, exc_info=True)
        

class IDestroyable(object):
    
    def Destroy(self):
        raise NotImplementedError()
    
    
class Destroyable(IDestroyable):
    
    def __init__(self):
        DestructionManager().AddDestroyable(self)
