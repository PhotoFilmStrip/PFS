'''
Created on 20.08.2011

@author: jens
'''

import logging
import sys


class AppMixin(object):
    
    def __init__(self):
        pass
    
    def InitLogging(self):
        if "-d" in sys.argv:
            lvl = logging.DEBUG
        else:
            lvl = logging.WARNING
        logging.basicConfig(level=lvl,
                            format=self._GetLogFormat(),
                            datefmt='%d.%m.%Y %H:%M:%S')

    def InitI18N(self):
        from photofilmstrip.lib.Settings import Settings
        Settings().InitLanguage()
        
    def Start(self):
        self.InitLogging()
        self.InitI18N()
        
        from photofilmstrip.lib.jobimpl.JobManager import JobManager
#        JobManager().Init()
        JobManager().Init("render")
        
        try:
            return self._OnStart()
        finally:
            JobManager().Destroy()
            
    def _GetLogFormat(self):
        return '%(asctime)s (%(levelname)s) %(name)s: %(message)s'

    def _OnStart(self):
        raise NotImplementedError()
