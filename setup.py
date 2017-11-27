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

import sys, os
import sqlite3
import site
import zipfile

from photofilmstrip import Constants

from distutils import log
from distutils.command.build import build
from distutils.command.clean import clean
from distutils.command.sdist import sdist
from distutils.core import setup
from distutils.core import Command
from distutils.dir_util import remove_tree

import glob
try:
    import py2exe
except ImportError:
    py2exe = None

WORKDIR = os.path.dirname(os.path.abspath(sys.argv[0]))
INNO = os.path.expandvars(r"%ProgramFiles(x86)%\Inno Setup 5\ISCC.exe")
MSGFMT = os.path.join(os.path.dirname(sys.executable),
                       "Tools", "i18n", "msgfmt.py")
if os.path.isfile(MSGFMT):
    MSGFMT = [sys.executable, MSGFMT]
else:
    MSGFMT = ["msgfmt"]


class pfs_clean(clean):

    def run(self):
        clean.run(self)

        for directory in (os.path.join(WORKDIR, "dist"),
                          os.path.join(WORKDIR, "build"),
                          os.path.join(WORKDIR, "release"),
                          ):
            if os.path.exists(directory):
                remove_tree(directory, 1)

        for fname in (os.path.join(WORKDIR, "version.info"),
                      os.path.join(WORKDIR, "MANIFEST"),
                      ):
            if os.path.exists(fname):
                os.remove(fname)


class pfs_scm_info(Command):

    description = "generates _scmInfo.py in source folder"

    user_options = []
    sub_commands = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        scmRev = os.getenv("SCM_REV")
        if not scmRev:
            # if not set in environment it hopefully was generated earlier
            # building deb with fakeroot has no SCM_REV var anymore
            try:
                import photofilmstrip._scmInfo
                scmRev = photofilmstrip._scmInfo.SCM_REV
            except ImportError:
                scmRev = "src"

        for target in getattr(self.distribution, "windows", []) + \
                      getattr(self.distribution, "console", []):
            target.Update(scmRev)

        if scmRev != "src":
            fd = open(os.path.join("photofilmstrip", "_scmInfo.py"), "w")
            fd.write("SCM_REV = \"%s\"\n" % scmRev)
            fd.close()


class pfs_sdist(sdist):

    sub_commands = [
        ('scm_info', lambda x: True),
    ] + sdist.sub_commands


class pfs_build(build):

    sub_commands = [
        ('scm_info', lambda x: True),
    ] + build.sub_commands

    def run(self):
        self._make_resources()
        self._make_locale()

        build.run(self)

    def _make_resources(self):
        try:
            from wx.tools.img2py import img2py
        except ImportError:
            log.warn("Cannot update image resources! Using images.py from source")
            return

        if sys.platform.startswith("linux") and os.getenv("DISPLAY") is None:
            log.warn("Cannot update image resources! img2py needs X")
            return

        imgDir = os.path.abspath(os.path.join("res", "icons"))
        if not os.path.exists(imgDir):
            return

        target = os.path.join("photofilmstrip", "res", "images.py")
        target_mtime = os.path.getmtime(target)

        imgResources = (
                        ("ICON_16","photofilmstrip_16.png"),
                        ("ICON_24","photofilmstrip_24.png"),
                        ("ICON_32","photofilmstrip_32.png"),
                        ("ICON_48","photofilmstrip_48.png"),
                        ("ICON_64","photofilmstrip_64.png"),
                        ("ICON_128","photofilmstrip_128.png"),

                        ("PROJECT_NEW_16","project_new_16.png"),
                        ("PROJECT_NEW_24","project_new_24.png"),
                        ("PROJECT_NEW_64","project_new_64.png"),
                        ("PROJECT_OPEN_16","project_open_16.png"),
                        ("PROJECT_OPEN_24","project_open_24.png"),
                        ("PROJECT_OPEN_64","project_open_64.png"),
                        ("PROJECT_SAVE_16","project_save_16.png"),
                        ("PROJECT_SAVE_D_16","project_save_d_16.png"),
                        ("PROJECT_SAVE_24","project_save_24.png"),
                        ("PROJECT_SAVE_D_24","project_save_d_24.png"),
                        ("PROJECT_CLOSE_16","project_close_16.png"),
                        ("PROJECT_CLOSE_D_16","project_close_d_16.png"),
                        ("FOLDER_OPEN_16","folder_open_16.png"),
                        ("FOLDER_OPEN_24","folder_open_24.png"),

                        ("MOTION_START_TO_END_24","motion_start_to_end_24.png"),
                        ("MOTION_END_TO_START_24","motion_end_to_start_24.png"),
                        ("MOTION_SWAP_24","motion_swap_24.png"),
                        ("MOTION_MANUAL_24","motion_manual_24.png"),
                        ("MOTION_MANUAL_32","motion_manual_32.png"),
                        ("MOTION_RANDOM_16","motion_random_16.png"),
                        ("MOTION_RANDOM_D_16","motion_random_d_16.png"),
                        ("MOTION_RANDOM_24","motion_random_24.png"),
                        ("MOTION_CENTER_16","motion_center_16.png"),
                        ("MOTION_CENTER_D_16","motion_center_d_16.png"),
                        ("LOCK_24","lock_24.png"),
                        ("UNLOCK_24","unlock_24.png"),

                        ("MENU_24","menu_24.png"),
                        ("ABORT_16","abort_16.png"),
                        ("ABORT_24","abort_24.png"),
                        ("LIST_REMOVE_16","list_remove_16.png"),
                        ("LIST_REMOVE_24","list_remove_24.png"),

                        ("RENDER_16","render_16.png"),
                        ("RENDER_D_16","render_d_16.png"),
                        ("RENDER_24","render_24.png"),
                        ("RENDER_D_24","render_d_24.png"),
                        ("RENDER_32","render_32.png"),
                        ("IMPORT_PICTURES_16","import_pictures_16.png"),
                        ("IMPORT_PICTURES_D_16","import_pictures_d_16.png"),
                        ("IMPORT_PICTURES_24","import_pictures_24.png"),
                        ("IMPORT_PICTURES_D_24","import_pictures_d_24.png"),
                        ("IMPORT_PICTURES_32","import_pictures_32.png"),
                        ("JOB_QUEUE_16","job_queue_16.png"),
                        ("JOB_QUEUE_D_16","job_queue_d_16.png"),
                        ("JOB_QUEUE_24","job_queue_24.png"),
                        ("JOB_QUEUE_D_24","job_queue_d_24.png"),

                        ("IMAGE_ROTATION_LEFT_16","image_rotation_left_16.png"),
                        ("IMAGE_ROTATION_LEFT_D_16","image_rotation_left_d_16.png"),
                        ("IMAGE_ROTATION_RIGHT_16","image_rotation_right_16.png"),
                        ("IMAGE_ROTATION_RIGHT_D_16","image_rotation_right_d_16.png"),
                        ("IMAGE_MOVING_LEFT_16","image_moving_left_16.png"),
                        ("IMAGE_MOVING_LEFT_D_16","image_moving_left_d_16.png"),
                        ("IMAGE_MOVING_LEFT_32","image_moving_left_32.png"),
                        ("IMAGE_MOVING_LEFT_D_32","image_moving_left_d_32.png"),
                        ("IMAGE_MOVING_RIGHT_16","image_moving_right_16.png"),
                        ("IMAGE_MOVING_RIGHT_D_16","image_moving_right_d_16.png"),
                        ("IMAGE_MOVING_RIGHT_32","image_moving_right_32.png"),
                        ("IMAGE_MOVING_RIGHT_D_32","image_moving_right_d_32.png"),
                        ("IMAGE_REMOVE_16","image_remove_16.png"),
                        ("IMAGE_REMOVE_D_16","image_remove_d_16.png"),
                        ("IMAGE_REMOVE_32","image_remove_32.png"),
                        ("IMAGE_REMOVE_D_32","image_remove_d_32.png"),

                        ("MUSIC_16","music_16.png"),
                        ("PLAY_16","play_16.png"),
                        ("PLAY_24","play_24.png"),
                        ("PLAY_PAUSE_16","play_pause_16.png"),
                        ("PLAY_PAUSE_d_16","play_pause_d_16.png"),
                        ("ARROW_UP_16","arrow_up_16.png"),
                        ("ARROW_UP_D_16","arrow_up_d_16.png"),
                        ("ARROW_DOWN_16","arrow_down_16.png"),
                        ("ARROW_DOWN_D_16","arrow_down_d_16.png"),
                        ("REMOVE_16","remove_16.png"),
                        ("REMOVE_D_16","remove_d_16.png"),
                        ("VIDEO_FORMAT_16","video_format_16.png"),
                        ("VIDEO_FORMAT_32","video_format_32.png"),

                        ("ALERT_16","alert_16.png"),
                        ("PROPERTIES_16","properties_16.png"),
                        ("EXIT_16","exit_16.png"),
                        ("HELP_16","help_16.png"),
                        ("ABOUT_16","about_16.png"),

                        ("FILMSTRIP","filmstrip.png"),
                        ("DIA","dia.png"),
                        ("DIA_S","dia_s.png"),

                       )

        for idx, (imgName, imgFile) in enumerate(imgResources):
            img2py(os.path.join(imgDir, imgFile),
                   target, append=idx > 0,
                   imgName=imgName,
                   icon=True,
                   compressed=True,
                   catalog=True)

    def _make_locale(self):
        for filename in os.listdir("po"):
            lang, ext = os.path.splitext(filename)
            if ext.lower() == ".po":
                moDir = os.path.join("build", "mo", lang, "LC_MESSAGES")
                moFile = os.path.join(moDir, "%s.mo" % Constants.APP_NAME)
                if not os.path.exists(moDir):
                    os.makedirs(moDir)

                self.spawn(MSGFMT + ["-o",
                                     moFile,
                                     os.path.join("po", filename)])

                targetPath = os.path.join("share", "locale", lang, "LC_MESSAGES")
                self.distribution.data_files.append(
                    (targetPath, (moFile,))
                )


class pfs_exe(Command):

    description = "create an executable dist for MS Windows (py2exe)"

    user_options = []
    sub_commands = [('py2exe', lambda x: True if py2exe else False)
                   ]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        self.distribution.windows = [
                 Target(script="photofilmstrip/GUI.py",
                        dest_base="bin/" + Constants.APP_NAME
                        ),
        ]
        self.distribution.console = [
                 Target(script="photofilmstrip/CLI.py",
                        dest_base="bin/" + Constants.APP_NAME + "-cli"
                        )
        ]
        self.distribution.zipfile = "lib/photofilmstrip/modules"

        # Run all sub-commands (at least those that need to be run)
        for cmdName in self.get_sub_commands():
            self.run_command(cmdName)

        targetDir = os.path.join("build", "dist", "bin")
        dllDirCairo = os.path.join(site.getsitepackages()[-1], "wx-3.0-msw", "wx")
        for dll in ["freetype6.dll", "libcairo-2.dll", "libpng14-14.dll"]:
            self.copy_file(os.path.join(dllDirCairo, dll),
                           os.path.join(targetDir, dll))

        dllDirGnome = os.path.join(site.getsitepackages()[-1], "gnome")
        for dll in glob.glob(os.path.join(dllDirGnome, "*.dll")):
            self.copy_file(os.path.join(dllDirGnome, dll),
                           os.path.join(targetDir, os.path.basename(dll)))

        targetDir = os.path.join("build", "dist", "lib", "gstreamer-1.0")
        self.copy_tree(os.path.join(dllDirGnome, "lib", "gstreamer-1.0"),
                       targetDir)

        targetDir = os.path.join("build", "dist", "lib", "girepository-1.0")
        self.mkpath(targetDir)
        for giTypeLib in ["GLib-2.0.typelib",
                          "GModule-2.0.typelib",
                          "GObject-2.0.typelib",
                          "Gst-1.0.typelib"]:
            self.copy_file(os.path.join(dllDirGnome, "lib", "girepository-1.0", giTypeLib),
                           os.path.join(targetDir, giTypeLib))


class pfs_win_setup(Command):

    description = "create an executable installer for MS Windows (InnoSetup)"

    user_options = []
    sub_commands = [('bdist_win', lambda x: True),
                   ]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # Run all sub-commands (at least those that need to be run)
        for cmdName in self.get_sub_commands():
            self.run_command(cmdName)

        ver = Constants.APP_VERSION
        open(os.path.join(WORKDIR, "version.info"), "w").write(ver)

        is64Bit = sys.maxsize > 2 ** 32
        if is64Bit:
            bitSuffix = "win64"
        else:
            bitSuffix = "win32"

        log.info("building installer...")
        self.spawn([INNO, "/Q",
                    "/F%s-%s-%s" % ("setup_photofilmstrip", ver, bitSuffix),
                    os.path.join("windows", "photofilmstrip_%s.iss" % bitSuffix)])
        log.info("    done.")


class pfs_win_portable(Command):

    description = "create a portable executable for MS Windows"

    user_options = []
    sub_commands = [('bdist_win', lambda x: True),
                   ]

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        # Run all sub-commands (at least those that need to be run)
        for cmdName in self.get_sub_commands():
            self.run_command(cmdName)

        ver = Constants.APP_VERSION

        is64Bit = sys.maxsize > 2 ** 32
        if is64Bit:
            bitSuffix = "win64"
        else:
            bitSuffix = "win32"

        log.info("building portable zip...")
        if not os.path.exists("release"):
            os.makedirs("release")

        Zip(os.path.join("dist", "photofilmstrip-{0}-{1}.zip".format(ver, bitSuffix)),
            "build/dist",
            virtualFolder="PhotoFilmStrip-%s" % ver,
            stripFolders=2)
        log.info("    done.")


class Target:

    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.product_version = "%s-%s" % (Constants.APP_VERSION, "src")
        self.version = "%s.%s" % (Constants.APP_VERSION, 0)
        self.company_name = ""
        self.copyright = "(c) 2017"
        self.name = "%s %s" % (Constants.APP_NAME, Constants.APP_VERSION)
        self.description = self.name
#        self.other_resources = [(RT_MANIFEST, 1, MANIFEST % dict(prog=Constants.APP_NAME))]

        logo = os.path.join("res", "icon", "photofilmstrip.ico")
        self.icon_resources = [(1, logo)]

    def Update(self, scmRev):
        self.product_version = "%s-%s" % (Constants.APP_VERSION, scmRev)


def Zip(zipFile, srcDir, stripFolders=0, virtualFolder=None):
    log.info("zip %s to %s" % (srcDir, zipFile))
    if not os.path.isdir(os.path.dirname(zipFile)):
        os.makedirs(os.path.dirname(zipFile))

    zf = zipfile.ZipFile(zipFile, "w", zipfile.ZIP_DEFLATED)
    for dirpath, dirnames, filenames in os.walk(srcDir):
        fldr = dirpath
        if stripFolders > 0:
            fldrs = os.path.normpath(fldr).split(os.sep)[stripFolders:]
            if fldrs:
                fldr = os.path.join(*fldrs)
            else:
                fldr = ""
        for fname in filenames:
            if virtualFolder is None:
                zipTarget = os.path.join(fldr, fname)
            else:
                zipTarget = os.path.join(virtualFolder, fldr, fname)
            log.info("  deflate %s" % zipTarget)
            zf.write(os.path.join(dirpath, fname), zipTarget)
    zf.close()


def Unzip(zipFile, targetDir, stripFolders=0):
    log.info("unzip %s to %s" % (zipFile, targetDir))
    if not os.path.isdir(targetDir):
        os.makedirs(targetDir)

    zf = zipfile.ZipFile(zipFile, "r")
    for ele in zf.namelist():
        eleInfo = zf.getinfo(ele)
        if eleInfo.file_size == 0:
            continue

        log.info("  inflate %s (%s)" % (ele, eleInfo.file_size))
        fldr, fname = os.path.split(ele)

        if stripFolders > 0:
            fldrs = os.path.normpath(fldr).split(os.sep)[stripFolders:]
            if fldrs:
                fldr = os.path.join(*fldrs)
            else:
                fldr = ""

        eleFldr = os.path.join(targetDir, fldr)
        if not os.path.isdir(eleFldr):
            os.makedirs(eleFldr)

        data = zf.read(ele)
        fd = open(os.path.join(eleFldr, fname), "wb")
        fd.write(data)
        fd.close()


platform_scripts = []
platform_data = []
if os.name == "nt":
    platform_scripts.append("windows/photofilmstrip.bat")
    platform_scripts.append("windows/photofilmstrip-cli.bat")
    platform_data.append((os.path.join("share", "doc", "photofilmstrip"), ["windows/photofilmstrip.chm"]))
else:
    platform_data.append(("share/applications", ["data/photofilmstrip.desktop"]))
    platform_data.append(("share/pixmaps", ["data/photofilmstrip.xpm"]))

    for size in glob.glob(os.path.join("data/icons", "*")):
        for category in glob.glob(os.path.join(size, "*")):
            icons = []
            for icon in glob.glob(os.path.join(category, "*")):
                icons.append(icon)
                platform_data.append(("share/icons/hicolor/%s/%s" % \
                                      (os.path.basename(size), \
                                       os.path.basename(category)), \
                                       icons))

setup(
    cmdclass={
                "clean"         : pfs_clean,
                "sdist"         : pfs_sdist,
                "build"         : pfs_build,
                "bdist_win"     : pfs_exe,
                "bdist_wininst" : pfs_win_setup,
                "bdist_winport" : pfs_win_portable,
                "scm_info"      : pfs_scm_info,
              },
    verbose=False,
    options={"py2exe": {"compressed": 2,
#                          "bundle_files":1,
                          "optimize": 2,
                          "dist_dir": "build/dist",
                          "dll_excludes": ["msvcr90.dll", "msvcp90.dll",
                                           "libcairo-gobject-2.dll",
                                           "libffi-6.dll",
                                           "libfontconfig-1.dll",
                                           "libfreetype-6.dll",
                                           "libgio-2.0-0.dll",
                                           "libgirepository-1.0-1.dll",
                                           "libglib-2.0-0.dll",
                                           "libgmodule-2.0-0.dll",
                                           "libgobject-2.0-0.dll",
                                           "libintl-8.dll",
                                           "libpng16-16.dll",
                                           "libwinpthread-1.dll",
                                           "libzzz.dll]"],
                          "packages": ["gi"],
                          "includes": ["gi",
                                       "PIL.Image",
                                       "PIL.BmpImagePlugin",
                                       "PIL.BufrStubImagePlugin",
                                       "PIL.CurImagePlugin",
                                       "PIL.DcxImagePlugin",
                                       "PIL.EpsImagePlugin",
                                       "PIL.FitsStubImagePlugin",
                                       "PIL.FliImagePlugin",
                                       "PIL.FpxImagePlugin",
                                       "PIL.GbrImagePlugin",
                                       "PIL.GifImagePlugin",
                                       "PIL.GribStubImagePlugin",
                                       "PIL.Hdf5StubImagePlugin",
                                       "PIL.IcnsImagePlugin",
                                       "PIL.IcoImagePlugin",
                                       "PIL.ImImagePlugin",
                                       "PIL.ImtImagePlugin",
                                       "PIL.IptcImagePlugin",
                                       "PIL.JpegImagePlugin",
                                       "PIL.McIdasImagePlugin",
                                       "PIL.MicImagePlugin",
                                       "PIL.MpegImagePlugin",
                                       "PIL.MspImagePlugin",
                                       "PIL.PalmImagePlugin",
                                       "PIL.PcdImagePlugin",
                                       "PIL.PcxImagePlugin",
                                       "PIL.PdfImagePlugin",
                                       "PIL.PixarImagePlugin",
                                       "PIL.PngImagePlugin",
                                       "PIL.PpmImagePlugin",
                                       "PIL.PsdImagePlugin",
                                       "PIL.SgiImagePlugin",
                                       "PIL.SpiderImagePlugin",
                                       "PIL.SunImagePlugin",
                                       "PIL.TgaImagePlugin",
                                       "PIL.TiffImagePlugin",
                                       "PIL.WmfImagePlugin",
                                       "PIL.XbmImagePlugin",
                                       "PIL.XpmImagePlugin",
                                       "PIL.XVThumbImagePlugin"
                                       ],
                          "excludes": ["Tkconstants", "Tkinter", "tcl",
                                       "PIL._imagingtk", "PIL.ImageTk",
                                       "_ssl"]
                          },
               "sdist": {"formats": ["gztar"]}
    },
    data_files=[
                (os.path.join("share", "doc", "photofilmstrip"), glob.glob("docs/*.*")),
                (os.path.join("share", "doc", "photofilmstrip", "html"), glob.glob("docs/html/*.*")),
#                (os.path.join("share", "photofilmstrip", "audio"), glob.glob("data/audio/*.mp3")),
    ] + platform_data,
    scripts=[
             "scripts/photofilmstrip",
             "scripts/photofilmstrip-cli",
    ] + platform_scripts,

    name=Constants.APP_NAME.lower(),
    version=Constants.APP_VERSION,
    license="GPLv2",
    description=Constants.APP_SLOGAN,
    long_description=Constants.APP_DESCRIPTION,
    author=Constants.DEVELOPERS[0],
    author_email="info@photofilmstrip.org",
    url=Constants.APP_URL,

    packages=['photofilmstrip',
                'photofilmstrip.action', 'photofilmstrip.cli',
                'photofilmstrip.core', 'photofilmstrip.core.renderer',
                'photofilmstrip.gui', 'photofilmstrip.gui.ctrls', 'photofilmstrip.gui.util',
                'photofilmstrip.lib', 'photofilmstrip.lib.common', 'photofilmstrip.lib.jobimpl',
                'photofilmstrip.res'],
    )
