# encoding: UTF-8

import os

class SelectWait(object):
    
    def __init__(self):
        self.__fdR, self.__fdW = os.pipe()
        self.__isSet = False
    
    def fileno(self):
        return self.__fdR
    
    def isSet(self):
        return self.__isSet
    
    def set(self):
        os.write(self.__fdW, 'q')
        self.__isSet = True
    
    def reset(self):
        os.read(self.__fdR, 1)
        self.__isSet = False
