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

- UseResample (True or False, if False then filter Nearest is used)
- ResampleFilter (Nearest, Bilinear, Bicubic, Antialias)


MPEG2-Video
```````````````

Creates MPEG-2 (actually MPEG-1 too, if VCD-Profile is selected) conform movie files.

Properties
''''''''''

- UseResample (True or False, if False then filter Nearest is used)
- ResampleFilter (Nearest, Bilinear, Bicubic, Antialias)
- Bitrate (overrides profile specific)


MPEG4-Video
``````````````````````````````

Creates MPEG-4 videos in an AVI container.

Properties
''''''''''

- UseResample (True or False, if False then filter Nearest is used)
- ResampleFilter (Nearest, Bilinear, Bicubic, Antialias)
- Bitrate (overrides profile specific)
- FFOURCC (XVid/DIVX)


.. _render_profile:

Profile
~~~~~~~

The profile field allows you to select the desired video type. 
The following table shows which types are available with their default properties.


+---------+----------------+--------------+-------------+
| Name    | Resolution     | Bitrate      | Compression |
+=========+================+==============+=============+
| VCD     | 352x288 (PAL)  | 1150 kBit/s  | MPEG-1      |
|         | 352x240 (NTSC) |              |             |
+---------+----------------+--------------+-------------+
| SVCD    | 576x480 (PAL)  | 2500 kBit/s  | MPEG-2      |
|         | 480x480 (NTSC) |              |             |
+---------+----------------+--------------+-------------+
| DVD     | 720x576 (PAL)  | 8000 kBit/s  |  MPEG-2     |
|         | 720x480 (NTSC) |              |             |
+---------+----------------+--------------+-------------+
| Medium  | 640x360        | 8000 kBit/s  | MPEG-4 ()   |
+---------+----------------+--------------+-------------+
| HD      | 1280x720       | 10000 kBit/s | MPEG-4 ()   |
+---------+----------------+--------------+-------------+
| Full-HD | 1920x1080      | 12000 kBit/s | MPEG-4 ()   |
+---------+----------------+--------------+-------------+


.. _render_type:

Type
~~~~

Choose between PAL and NTSC. 

