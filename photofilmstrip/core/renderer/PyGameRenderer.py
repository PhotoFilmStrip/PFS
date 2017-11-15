# encoding: UTF-8
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2011 Jens Goepfert
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

try:
    import pygame
except ImportError:
    pygame = None

from photofilmstrip.core.OutputProfile import OutputProfile
from photofilmstrip.core.BaseRenderer import BaseRenderer


class PyGameRenderer(BaseRenderer):
    
    def __init__(self):
        BaseRenderer.__init__(self)
        self._black = 0, 0, 0
        self._screen = None
        self._mainClock = pygame.time.Clock()
        self._framerate = None
        
    @staticmethod
    def GetName():
        return u"PyGame"
    
    @staticmethod
    def CheckDependencies(msgList):
        BaseRenderer.CheckDependencies(msgList)
        if pygame is None:
            msgList.append("pygame not installed!")

    @staticmethod
    def GetProperties():
        return BaseRenderer.GetProperties() + ["RenderSubtitle"]

    @staticmethod
    def GetDefaultProperty(prop):
        if prop == "RenderSubtitle":
            return "false"
        return BaseRenderer.GetDefaultProperty(prop)

    def _GetFrameRate(self):
        if self.GetProfile().GetVideoNorm() == OutputProfile.PAL:
            framerate = 25.0
        elif self.GetProfile().GetVideoNorm() == OutputProfile.NTSC:
            framerate = 30000.0 / 1001.0
        else:
            framerate = 60.0
        return framerate
    
    def ProcessFinalize(self, pilImg):
        if pilImg:
            pygameImg = self._PilToPyGame(pilImg)
#            self._screen.fill(self._black)
            self._screen.blit(pygameImg, (0, 0))
            pygame.display.flip()
        self._mainClock.tick(self._framerate)
        print self._mainClock.get_fps()
    
    def ProcessAbort(self):
        pygame.mixer.music.stop()
        pygame.display.quit()

    def Prepare(self):
        self._framerate = self._GetFrameRate()
        
        self._screen = pygame.display.set_mode(self.GetProfile().GetResolution())
        pygame.mixer.init()
        pygame.mixer.music.load(self.GetAudioFile())
        pygame.mixer.music.play(1)
        
#        self._mainClock.reset()
        
    def Finalize(self):
        pygame.mixer.music.stop()
        pygame.display.quit()
        
    def EnsureFramerate(self):
        if get_fps(self._mainClock, self._framerate):
            return True
        else:
            return False

    def _PilToPyGame(self, pilImg):
        mode = pilImg.mode
        assert mode in "RGB", "RGBA"
        return pygame.image.fromstring(pilImg.tobytes(), pilImg.size, mode)


#    def CropAndResize(self, ctx, rect):
#        if get_fps(self._mainClock, self._framerate):
#            return None
#        
#        return BaseRenderer.CropAndResize(self, ctx, rect)
#        
#    def Transition(self, kind, ctx1, ctx2, percentage):
#        if ctx1 is None or ctx2 is None:
#            return None
#        if get_fps(self._mainClock, self._framerate):
#            return None
#        
#        return BaseRenderer.Transition(self, kind, ctx1, ctx2, percentage)


def get_fps(clock, value):
    fps = clock.get_fps()
    tol = 0.1
#    print fps, abs(fps - value), abs(fps * tol)
    return not (fps > 1 and abs(fps - value) <= abs(fps * tol))

