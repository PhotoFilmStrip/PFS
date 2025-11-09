# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2019 Jens Goepfert
#

import wx
import wx.html


class PnlStoryGuide(wx.html.HtmlWindow):

    def __init__(self, parent):
        wx.html.HtmlWindow.__init__(self, parent, wx.ID_ANY, style=wx.NO_BORDER)

        self.SetBackgroundStyle(wx.BG_STYLE_SYSTEM)

        self.SetPage(self.GetHtmlContent())

    def GetHtmlContent(self):
        return """
<html>
  <body bgcolor="#EBEBEB" witdth="650px">
  <font color="#63666A" face="Tahoma">
    <h3 align="center">PhotoFilmStory</h3>
    
    <h5>Warning</h5>
    
    <font color="#FF666A">
    This feature is still under development.
    </font>
    
    <h5>What is this <i>PhotoFilmStory</i>?</h5>
    <p>
    Imagine your holidays. You most likely take a lot of pictures, record
    a video clip, maybe not only one, and then you take more pictures. And these
    steps will repeat a few times for every trip you do.
    </p>
    
    <p>
    You already know how to make a slideshow but what to do with the video clips?
    Right, here you go. In a <i>PhotoFilmStory</i> you can add your slideshows
    and videoclips, add some music in the background and render it into a single
    video file.
    </p>
    
    <h5>How to start</h5>
    
    <ul>
      <li>Add video clips and audio tracks by using the <i>Add media</i> tool button.</li>
      <li>Use the arrow tool buttons to organize your media files in your timeline.</li>
      <li>The timeline runs from top to bottom.</li> 
      <li>The timeline has two levels.</li>
      <li>The second level defines how long the media in the first level is played</li>
      <ul>
        <li>
          If you have a long video clip and you want to put multiple audio tracks as a background music.
          Put your video clip in the first level and the audio clips in the second level.
        </li>
        <li>
          If you have several short video clips but you want them all with the same background music.
          Put your audio clip in the first level and all the video clips in the second level. 
        </li>
      </ul>
    </ul>
    
    <a href="#">Hide this information</a>
    
  </font>
  </body>
</html>
"""
