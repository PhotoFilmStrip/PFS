Render a slideshow
==================

If you are done designing your PhotoFilmStrip you can create a movie file. The possibilities to set up the movie are described here.


.. _render_settings:

Settings
--------

.. _output:

Output
------

.. _output_format:

Format
~~~~~~

This option allows you to specify the desired output format. 
The following table shows which formats are available with their default properties.


Single pictures
```````````````
The output is rendered as single picture files to the output folder. 
Notice, with the videonorm NTSC (~30 fps) and a PhotoFilmStrip with a total length of 10 seconds results to 300 pictures. 
Each with a size of approximatally 2 MB results to 600 MB.

Properties
''''''''''

- ResampleFilter (Nearest, Bilinear, Bicubic, Antialias)


VCD (MPG)
`````````

Creates movie files for Video-CDs.

Properties
''''''''''

- Bitrate (overrides profile specific)
- Subtitle (file, render)
- SubtitleSettings


SVCD, DVD (MPG)
```````````````

Creates MPEG-2 conform movie files.

Properties
''''''''''

- Bitrate (overrides profile specific)
- Subtitle (file, render)
- SubtitleSettings


Theora/Vorbis (OGV)
```````````````````

Creates OGV movie files.

Properties
''''''''''

- Bitrate (overrides profile specific)
- Subtitle (file, render, embed)
- SubtitleLanguage
- SubtitleSettings


x264 (MKV, MP4)
```````````````

Creates H.264 or MPEG-4 part 10 video files.

Properties
''''''''''

- Bitrate (overrides profile specific)
- Subtitle (file, render, embed)
- SubtitleLanguage
- SubtitleSettings
- SpeedPreset: default is medium (6)
- Profile (main, **high**, baseline, constrained-baseline)


x265 (MKV)
``````````

Creates H.265 or MPEG-H part 2 video files.

Properties
''''''''''

- Bitrate (overrides profile specific)
- Subtitle (file, render, embed)
- SubtitleLanguage
- SubtitleSettings
- SpeedPreset: default is medium (6)


Common properties
~~~~~~~~~~~~~~~~~

- SpeedPreset:

  - (0): None
  - (1): ultrafast
  - (2): superfast
  - (3): veryfast
  - (4): faster
  - (5): fast
  - (6): medium
  - (7): slow
  - (8): slower
  - (9): veryslow
  - (10): placebo


- Subtitle:

  - file: to save the subtitles as a separte srt-file
  - render: bo burn the subtitle into the video
  - embed: to embed the subtitle into the video container, if supported


- SubtitleLanguage:

  Use language code like de, en, etc., to specify the language if mode embed is used.


- SubtitleSettings:

  Use several settings splitted via semicolon. Some useful settings are:
  
  - shaded-background=1
  - valignment=bottom|top
  - font-desc=<font-name> <size> (font-desc=Arial 12)
  - color=0xAARRGGBB (color=0xff00ff00 for green without transparancy)

  A full list of properties can be found `here <https://gstreamer.freedesktop.org/data/doc/gstreamer/head/gst-plugins-base-plugins/html/gst-plugins-base-plugins-textoverlay.html>`_. 

  The following value shows a green subtitle at the top of the screen:

  ``shaded-background=1;valignment=top;font-desc=Arial 12;color=0xff00ff00``


.. _render_profile:

Profile
~~~~~~~

The profile field allows you to select the desired video type. 
The following table shows which types are available with their default properties.


+---------+---------------------+--------------+-------------+
| Name    | Resolution          | Bitrate      | Compression |
+=========+=====================+==============+=============+
| VCD     | 352x288 (PAL)       | 1150 kBit/s  | MPEG-1      |
|         | 352x240 (NTSC)      |              |             |
+---------+---------------------+--------------+-------------+
| SVCD    | 576x480 (PAL)       | 2500 kBit/s  | MPEG-2      |
|         | 480x480 (NTSC)      |              |             |
+---------+---------------------+--------------+-------------+
| DVD     | 720x576 (PAL)       | 8000 kBit/s  | MPEG-2      |
|         | 720x480 (NTSC)      |              |             |
+---------+---------------------+--------------+-------------+
| Medium  | 640x360 (360p)      | 1000 kBit/s  | various     |
+---------+---------------------+--------------+-------------+
| Medium  | 854x480 (480p)      | 2500 kBit/s  | various     |
+---------+---------------------+--------------+-------------+
| HD      | 1280x720 (720p)     | 7500 kBit/s  | various     |
+---------+---------------------+--------------+-------------+
| Full-HD | 1920x1080 (1080p)   | 12000 kBit/s | various     |
+---------+---------------------+--------------+-------------+
| UHD     | 3840x2160 (2160p)   | 50000 kBit/s | various     |
+---------+---------------------+--------------+-------------+
| UHD-2   | 7600x4320 (4320p)   | 60000 kBit/s | various     |
+---------+---------------------+--------------+-------------+

