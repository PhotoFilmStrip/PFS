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
from distutils.core import setup
from distutils.core import Command
from distutils.dir_util import remove_tree

import glob
try:
    import py2exe
except ImportError:
    py2exe = None

WORKDIR = os.path.dirname(os.path.abspath(sys.argv[0]))
INNO    = r"C:\Programme\Inno Setup 5\ISCC.exe"
MSGFMT  = os.path.join(os.path.dirname(sys.executable),
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
                      os.path.join(WORKDIR, "_svnInfo.py"),
                      os.path.join(WORKDIR, "_svnInfo.pyc"),
                      os.path.join(WORKDIR, "_svnInfo.pyo")):
            if os.path.exists(fname):
                os.remove(fname)
           

class pfs_build(build):
    def finalize_options(self):
        build.finalize_options(self)

    def run(self):
        self._make_svn_info()
        self._make_resources()
        self._make_locale()

        build.run(self)
        
    def _make_svn_info(self):
        svnRev = 0
        if os.path.isfile(".svn/wc.db"):
            # from svn 1.7
            try:
                dbConn = sqlite3.connect(".svn/wc.db")
                cur = dbConn.execute("select changed_revision from nodes where local_relpath=''")
                row = cur.fetchone()
                if row:
                    svnRev = row[0]
            except:
                raise
        elif os.path.isfile(".svn/entries"):
            # until svn 1.6
            try:
                svnRev = open(".svn/entries", "r").readlines()[3].strip()
            except:
                pass

        for target in getattr(self.distribution, "windows", []) + \
                      getattr(self.distribution, "console", []):
            target.Update(svnRev)
        
        fd = open("_svnInfo.py", "w")
        fd.write("SVN_REV = \"%s\"\n" % svnRev)
        fd.close()
        
    def _make_resources(self):
        try:
            from wx.tools.img2py import img2py
        except ImportError:
            log.warn("Cannot update image resources! Using images.py from svn")
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
#                        ("ALIGN_BOTTOM", "align_bottom.png"),
#                        ("ALIGN_MIDDLE", "align_middle.png"),
#                        ("ALIGN_TOP", "align_top.png"),
#                        ("ALIGN_LEFT", "align_left.png"),
#                        ("ALIGN_CENTER", "align_center.png"),
#                        ("ALIGN_RIGHT", "align_right.png"),
                        ("PLAY_PAUSE", "play_pause_16.png"),
                        ("MOTION_RIGHT", "motion_right_24.png"),
                        ("MOTION_LEFT", "motion_left_24.png"),
                        ("MOTION_SWAP", "motion_swap_24.png"),
                        ("MOTION_INPUT", "motion_input_24.png"),
                        ("MOTION_RANDOM", "motion_random_24.png"),
                        ("LOCK", "lock_24.png"),
                        ("UNLOCK", "unlock_24.png"),
                        ("ICON_32", "photofilmstrip_32.png"),
                        ("ICON_48", "photofilmstrip_48.png")
                       )
        
        for idx, (imgName, imgFile) in enumerate(imgResources):
            img2py(os.path.join(imgDir, imgFile), 
                   target, append=idx>0, 
                   imgName=imgName, 
                   icon=True, 
                   compressed=True, 
                   catalog=True)
            
    def _make_locale(self):
        for filename in os.listdir("po"):
            lang, ext = os.path.splitext(filename)
            if ext.lower() == ".po":
                moDir =  os.path.join("build", "mo", lang, "LC_MESSAGES")
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
    sub_commands = [('py2exe',  lambda x: True if py2exe else False)                    
                   ]

    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        self.distribution.windows = [
                 Target(script = "photofilmstrip/GUI.py",
                        dest_base = "bin/" + Constants.APP_NAME
                        ),
        ]
        self.distribution.console = [
                 Target(script = "photofilmstrip/CLI.py",
                        dest_base = "bin/" + Constants.APP_NAME + "-cli"
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
        
        log.info("building installer...")
        self.spawn([INNO, "/Q",
                    "/F%s-%s" % ("setup_photofilmstrip", ver), 
                    os.path.join("windows", "photofilmstrip.iss")])
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
        log.info("building portable zip...")
        if not os.path.exists("release"):
            os.makedirs("release")
            
        Zip(os.path.join("dist", "photofilmstrip-%s.zip" % ver), 
            "build/dist", 
            virtualFolder="PhotoFilmStrip-%s" % ver,
            stripFolders=2)
        log.info("    done.")


class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.product_version = Constants.APP_VERSION
        self.version = "%s.%s" % (self.product_version, 0)
        self.company_name = ""
        self.copyright = "(c) 2011"
        self.name = "%s %s" % (Constants.APP_NAME, self.product_version)
        self.description = self.name
#        self.other_resources = [(RT_MANIFEST, 1, MANIFEST % dict(prog=Constants.APP_NAME))]
        
        logo = os.path.join("res", "icon", "photofilmstrip.ico")
        self.icon_resources = [(1, logo)]
        
    def Update(self, svnVer):
        self.version = "%s.%s" % (self.product_version, svnVer)


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
            for icon in glob.glob(os.path.join(category,"*")):
                icons.append(icon)
                platform_data.append(("share/icons/hicolor/%s/%s" % \
                                      (os.path.basename(size), \
                                       os.path.basename(category)), \
                                       icons))


setup(
    cmdclass={
                "clean"         : pfs_clean,
                "build"         : pfs_build,
                "bdist_win"     : pfs_exe,
                "bdist_wininst" : pfs_win_setup,
                "bdist_winport" : pfs_win_portable,
              },
    verbose=False,
    options = {"py2exe": {"compressed": 2,
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

    name = Constants.APP_NAME.lower(),
    version = Constants.APP_VERSION,
    license = "GPLv2",
    description = Constants.APP_SLOGAN,
    long_description = Constants.APP_DESCRIPTION,
    author = Constants.DEVELOPERS[0],
    author_email = "info@photofilmstrip.org",
    url = Constants.APP_URL,
       
    packages = ['photofilmstrip', 
                'photofilmstrip.action', 'photofilmstrip.cli', 
                'photofilmstrip.core', 'photofilmstrip.core.renderer',
                'photofilmstrip.gui', 'photofilmstrip.gui.ctrls', 'photofilmstrip.gui.util',
                'photofilmstrip.lib', 'photofilmstrip.lib.common', 'photofilmstrip.lib.jobimpl',
                'photofilmstrip.res'],
    )
