Creating a new PhotoFilmStrip
=============================

Project properties
------------------

Total length
~~~~~~~~~~~~

If this option is activated you can override the duration of the single pictures and setup the total movie length..
This is useful if you want to integrate the PhotoFilmStrip in another video project.

Notice, the duration of the single pictures is multiplied with a factor, a ratio to the desired total length..
A PhotoFilmStrip containing two pictures with the durations of 2 and 4 seconds results to durations of.
3.3 and 6.7 seconds in a PhotoFilmStrip with a total length of 10 seconds. The ratio is 1.67 (10.0 / 6.0).

You have two options to specify the total length.

- Manual, to set the total length for yourself.

- Audio file, to set the total length to the length of an audio file.

Seamless loop
~~~~~~~~~~~~~

If you activate "Create seamless loop" in the slideshow properties, the last picture
transitions back to the first picture. The rendered movie can then be played in an
endless loop without a visible jump.


.. _add_pics:

Add pictures
------------

To add pictures to your PhotoFilmStrip you can use the entry in the main menu (Tools -> Import pictures), 
the toolbutton in the toolbar or by dropping some file in the imagelist at the bottom of the main window.
With "Import Directory..." (Ctrl+Shift+I) you can import a complete directory: all pictures
in the directory and its subdirectories are added to the PhotoFilmStrip.

Managing pictures
~~~~~~~~~~~~~~~~~

The picture list at the bottom of the main window supports several shortcuts and
toolbar buttons:

- Select All (Ctrl+A): selects all pictures in the list.
- Select previous/next picture (Alt+Left / Alt+Right): moves the selection one
  picture to the left or right.
- Shuffle Pictures (Alt+S): randomizes the order of the pictures.
- Remove duplicate pictures: removes pictures that look the same. The comparison is
  based on the image content (a perceptual hash), so duplicates are found even if
  file name, file size or modification date differ. The first picture of each group
  of duplicates is kept.
- Delete: removes the selected pictures from the PhotoFilmStrip.
- Quick Preview (Alt+Q): renders a fast draft preview of the selected pictures
  (or of all pictures if none are selected) and plays it looping in an external
  player (mplayer, mpv or vlc are tried in this order). Press Alt+Q again to stop
  the preview.


.. _motion_control:

Motion control
--------------

After selecting a picture you see it once on the left hand side and once on the right hand side. 
Now you can move a rectange on both pictures. To zoom the rectangle simply use the mousewheel. 
Move it by dragging it with the mouse. 
When resizing the rectangle by dragging a corner or edge, hold Ctrl to keep the center of the
rectangle fixed (the rectangle then grows/shrinks symmetrically around its center).
The rectangle on the left picture defines where the animated path of the picture starts. 
The ending point is defined with the rectangle on the right picture.

Instead of defining the motion path yourself you can let PhotoFilmStrip choose a
random one for the selected picture with the "Random motion" entry in the context
menu or by pressing Ctrl+D.


.. _settings:

Settings
--------

Below the two images you can see a panel to adjust some settings for the selected picture. 
It is possible to rotate it clockwise and counter clockwise. 
You have the choice between some nice effects like black and white etc.
Furthermore you can type in a comment to the picture. These comments will be generated into a subtitle file. 
This allows you to easily turn on/off the comments while playing your PhotoFilmStrip on a DVD-Player or with your favorite software player.
