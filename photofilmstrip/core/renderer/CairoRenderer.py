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

import array
import time

try:
    import wx
    import cairo
except (ImportError, RuntimeError):
    cairo = None

from photofilmstrip.core.OutputProfile import OutputProfile
from photofilmstrip.core.BaseRenderer import BaseRenderer, FinalizeHandler


class CairoRenderer(BaseRenderer):

    def __init__(self):
        BaseRenderer.__init__(self)
        self._ctx = None
        self._mainClock = Clock()
        self._framerate = None

        self._screen = wx.Frame(wx.GetApp().GetTopWindow(),
                                style=wx.DEFAULT_FRAME_STYLE | wx.RESIZE_BORDER)
        self._screen.Bind(wx.EVT_PAINT, self.OnPaint)
        self._screen.Show()

    @staticmethod
    def GetName():
        return _(u"Preview")

    @staticmethod
    def CheckDependencies(msgList):
        BaseRenderer.CheckDependencies(msgList)
        if cairo is None:
            msgList.append("cairo not installed!")

    def GetFinalizeHandler(self):
        '''
        :rtype: FinalizeHandler
        '''
        return PilToCairoFinalizeHandler()

    def ToSink(self, data):
        self._ctx = data
        self._mainClock.tick(self._framerate)

        wx.CallAfter(self._screen.Refresh)

    def ProcessAbort(self):
        wx.CallAfter(self._screen.Destroy)

    def Prepare(self):
        self._screen.SetClientSize(*self.GetProfile().GetResolution())

        self._framerate = self.GetProfile().GetFrameRate().AsFloat()
        self._mainClock.reset()

    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self._screen)
#        dc.SetBackground(wx.Brush('black'))
#        dc.Clear()

        if self._ctx:
            w = self._ctx.get_width()
            h = self._ctx.get_height()
            data = self._ctx.get_data()
            wxbmp = wx.Bitmap.FromBufferRGBA(w, h, data)
            dc.DrawBitmap(wxbmp, 0, 0)

        event.Skip()

    def Finalize(self):
        wx.CallAfter(self._screen.Destroy)


class PilToCairoFinalizeHandler(FinalizeHandler):

    def UseSmartFinalize(self):
        return True

    def ProcessFinalize(self, pilImg):
        pilImg = pilImg.copy()
        w, h = pilImg.size
        data = pilImg.convert('RGBA').tobytes()
        buff = array.array('B', data)
        cairoImage = cairo.ImageSurface.create_for_data(# pylint: disable=no-member
            buff, cairo.FORMAT_ARGB32, w, h)  # pylint: disable=no-member
#        cairoImage = cairo.ImageSurface.create_for_data(buff, cairo.FORMAT_RGB24, w, h)
        return cairoImage


class Clock:

    def __init__(self):
        self.fps = 0.0
        self.fps_count = 0
        self.start = 0

    def reset(self):
        self.start = time.time()

    def tick(self, framerate):
        nowtime = time.time()
        self.fps_count += 1

        timepassed = nowtime - self.start

        self.fps = 1.0 / (timepassed / self.fps_count)

        endtime = (1.0 / framerate) * self.fps_count
        delay = endtime - timepassed
        if delay < 0:
            delay = 0
        time.sleep(delay)

    def get_fps(self):
        return self.fps


def get_fps(clock, value):
    fps = clock.get_fps()
    tol = 0.1
#    print fps, abs(fps - value), abs(fps * tol)
    return not (fps > 1 and abs(fps - value) <= abs(fps * tol))

