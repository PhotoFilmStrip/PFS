
import threading
import urllib
import traceback


class UpdateChecker(threading.Thread):

    URL = "http://photostoryx.sourceforge.net/update.txt"
    
    def __init__(self):
        threading.Thread.__init__(self, name="UpdateCheck")
        
        self._onlineVersion = None
        self._changes = []
        self._checkDone = False
        self._isOk = False
        
        self.start()
        
    def run(self):
        try:
            fd = urllib.urlopen(self.URL)
            data = fd.read()
        except:
            traceback.print_exc()
            self._checkDone = True
            self._isOk = False
            return
        
        lines = data.split('\n')
        self._onlineVersion = lines.pop(0)
        self._changes = lines
        
        self._checkDone = True
        self._isOk = True 
        
    def IsDone(self):
        return self._checkDone
    
    def IsOk(self):
        return self._isOk
    
    def IsNewer(self, currentVersion):
        if self.IsDone() and self.IsOk():
            curTup = currentVersion.split(".")
            newTup = self._onlineVersion.split(".")
            return newTup > curTup
        return False
    
    def GetChanges(self):
        return "\n".join(self._changes)
        
    def GetVersion(self):
        return self._onlineVersion
