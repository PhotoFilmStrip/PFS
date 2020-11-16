# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2011 Jens Goepfert
#

import base64
import datetime
import glob
import sys, os
import sqlite3
import unittest
import zipfile

from distutils import log
from distutils.command.build import build
from distutils.command.clean import clean
from distutils.command.sdist import sdist
from distutils.core import setup
from distutils.core import Command
from distutils.dir_util import remove_tree
from distutils.sysconfig import get_python_lib

try:
    from sphinx.application import Sphinx
except ImportError:
    Sphinx = None

try:
    from cx_Freeze.dist import build_exe
    from cx_Freeze import Executable
except ImportError:
    build_exe = None

from photofilmstrip import Constants

if os.getenv("ProgramFiles(x86)"):
    PROGRAMFILES = os.path.expandvars("%ProgramFiles(x86)%")
else:
    PROGRAMFILES = os.path.expandvars("%ProgramFiles%")

WORKDIR = os.path.dirname(os.path.abspath(sys.argv[0]))
INNO = os.path.join(PROGRAMFILES, "Inno Setup 5", "ISCC.exe")
MSGFMT = os.path.join(getattr(sys,
                              "base_prefix",
                              os.path.dirname(sys.executable)),
                      "Tools", "i18n", "msgfmt.py")
if os.path.isfile(MSGFMT):
    MSGFMT = [sys.executable, MSGFMT]
else:
    MSGFMT = ["msgfmt"]


class pfs_clean(clean):

    def run(self):
        clean.run(self)

        for directory in (os.path.join(WORKDIR, "build"),
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

    user_options = [
        ('scm-rev=', None, 'The SCM revision'),
    ]

    sub_commands = []

    def initialize_options(self):
        self.scm_rev = os.getenv("SCM_REV")

    def finalize_options(self):
        pass

    def run(self):
        if not self.scm_rev:
            # if not set in environment it hopefully was generated earlier
            # building deb with fakeroot has no SCM_REV var anymore
            try:
                import photofilmstrip._scmInfo
                self.scm_rev = photofilmstrip._scmInfo.SCM_REV  # pylint: disable=no-member, protected-access
            except ImportError:
                self.scm_rev = "src"

        if self.scm_rev != "src":
            fd = open(os.path.join("photofilmstrip", "_scmInfo.py"), "w")
            fd.write("SCM_REV = \"%s\"\n" % self.scm_rev)
            fd.close()


class pfs_sdist(sdist):

    sub_commands = [
        ('scm_info', lambda x: True),
    ] + sdist.sub_commands


class pfs_docs(Command):

    description = "generates sphinx docs"

    user_options = [
        ('config-dir=', 'c', 'Location of the configuration directory'),
        ('project=', None, 'The documented project\'s name'),
        ('version=', None, 'The short X.Y version'),
        ('release=', None, 'The full version, including alpha/beta/rc tags'),
        ('builder=', 'b', 'The builder (or builders) to use.')
    ]
    sub_commands = []

    def initialize_options(self):
        self.config_dir = None
        self.project = ''
        self.version = ''
        self.release = ''
        self.builder = ['html']

    def finalize_options(self):
        pass

    def run(self):
        build = self.get_finalized_command('build')
        build_dir = os.path.join(os.path.abspath(build.build_base), 'sphinx')
        doctree_dir = os.path.join(build_dir, 'doctrees')
        self.mkpath(build_dir)
        self.mkpath(doctree_dir)
        confoverrides = {}
        if self.project:
            confoverrides['project'] = self.project
        if self.version:
            confoverrides['version'] = self.version
        if self.release:
            confoverrides['release'] = self.release

        for builder in self.builder:
            builder_target_dir = os.path.join(build_dir, builder)
            self.mkpath(builder_target_dir)

            app = Sphinx(self.config_dir, self.config_dir,
                         builder_target_dir, doctree_dir,
                         builder, confoverrides)
            app.build()

        self.distribution.data_files.extend([
                (os.path.join("share", "doc", "photofilmstrip"), glob.glob("docs/*.*")),
                (os.path.join("share", "doc", "photofilmstrip", "html"), glob.glob("build/sphinx/html/*.*")),
                (os.path.join("share", "doc", "photofilmstrip", "html", "_sources"), glob.glob("build/sphinx/html/_sources/*.*")),
                (os.path.join("share", "doc", "photofilmstrip", "html", "_static"), glob.glob("build/sphinx/html/_static/*.*"))
        ])


class pfs_build(build):

    sub_commands = [
        ('scm_info', lambda x: True),
        ('build_sphinx', lambda x: True if Sphinx else False),
    ] + build.sub_commands

    user_options = [
        ('build-exe=', None, 'Location of the configuration directory'),
    ]

    def initialize_options(self):
        build.initialize_options(self)
        self.build_exe = None

    def finalize_options(self):
        build.finalize_options(self)
        self.build_exe = "build"

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
                        ("ICON", "photofilmstrip.svg"),

                        ("PROJECT_NEW_16", "project_new.svg"),
                        ("PROJECT_NEW_24", "project_new.svg"),
                        ("PROJECT_NEW_64", "project_new.svg"),
                        ("PROJECT_OPEN_16", "project_open.svg"),
                        ("PROJECT_OPEN_24", "project_open.svg"),
                        ("PROJECT_OPEN_64", "project_open.svg"),
                        ("PROJECT_SAVE_16", "project_save.svg"),
                        ("PROJECT_SAVE_D_16", "project_save_d_16.png"),
                        ("PROJECT_SAVE_24", "project_save.svg"),
                        ("PROJECT_SAVE_D_24", "project_save_d_24.png"),
                        ("PROJECT_CLOSE_16", "project_close.svg"),
                        ("PROJECT_CLOSE_D_16", "project_close_d_16.png"),
                        ("FOLDER_OPEN_16", "folder_open.svg"),
                        ("FOLDER_OPEN_24", "folder_open.svg"),

                        ("MOTION_START_TO_END_24", "motion_start_to_end.svg"),
                        ("MOTION_END_TO_START_24", "motion_end_to_start.svg"),
                        ("MOTION_SWAP_24", "motion_swap.svg"),
                        ("MOTION_MANUAL_24", "motion_manual.svg"),
                        ("MOTION_MANUAL_32", "motion_manual.svg"),
                        ("MOTION_RANDOM_16", "motion_random.svg"),
                        ("MOTION_RANDOM_D_16", "motion_random_d_16.png"),
                        ("MOTION_RANDOM_24", "motion_random.svg"),
                        ("MOTION_CENTER_16", "motion_center.svg"),
                        ("MOTION_CENTER_D_16", "motion_center_d_16.png"),
                        ("LOCK_24", "lock.svg"),
                        ("UNLOCK_24", "unlock.svg"),

                        ("MENU_24", "menu.svg"),
                        ("ABORT_16", "abort.svg"),
                        ("ABORT_24", "abort.svg"),
                        ("LIST_REMOVE_16", "list_remove.svg"),
                        ("LIST_REMOVE_24", "list_remove.svg"),

                        ("RENDER_16", "render.svg"),
                        ("RENDER_D_16", "render_d_16.png"),
                        ("RENDER_24", "render.svg"),
                        ("RENDER_D_24", "render_d_24.png"),
                        ("RENDER_32", "render.svg"),
                        ("IMPORT_PICTURES_16", "import_pictures.svg"),
                        ("IMPORT_PICTURES_D_16", "import_pictures_d_16.png"),
                        ("IMPORT_PICTURES_24", "import_pictures.svg"),
                        ("IMPORT_PICTURES_D_24", "import_pictures_d_24.png"),
                        ("IMPORT_PICTURES_32", "import_pictures.svg"),
                        ("JOB_QUEUE_16", "job_queue.svg"),
                        ("JOB_QUEUE_D_16", "job_queue_d_16.png"),
                        ("JOB_QUEUE_24", "job_queue.svg"),
                        ("JOB_QUEUE_D_24", "job_queue_d_24.png"),

                        ("IMAGE_ROTATION_LEFT_16", "image_rotation_left.svg"),
                        ("IMAGE_ROTATION_LEFT_D_16", "image_rotation_left_d_16.png"),
                        ("IMAGE_ROTATION_RIGHT_16", "image_rotation_right.svg"),
                        ("IMAGE_ROTATION_RIGHT_D_16", "image_rotation_right_d_16.png"),
                        ("IMAGE_MOVING_LEFT_16", "image_moving_left.svg"),
                        ("IMAGE_MOVING_LEFT_D_16", "image_moving_left_d_16.png"),
                        ("IMAGE_MOVING_LEFT_32", "image_moving_left.svg"),
                        ("IMAGE_MOVING_LEFT_D_32", "image_moving_left_d_32.png"),
                        ("IMAGE_MOVING_RIGHT_16", "image_moving_right.svg"),
                        ("IMAGE_MOVING_RIGHT_D_16", "image_moving_right_d_16.png"),
                        ("IMAGE_MOVING_RIGHT_32", "image_moving_right.svg"),
                        ("IMAGE_MOVING_RIGHT_D_32", "image_moving_right_d_32.png"),
                        ("IMAGE_REMOVE_16", "image_remove.svg"),
                        ("IMAGE_REMOVE_D_16", "image_remove_d_16.png"),
                        ("IMAGE_REMOVE_32", "image_remove.svg"),
                        ("IMAGE_REMOVE_D_32", "image_remove_d_32.png"),

                        ("MUSIC_16", "music.svg"),
                        ("MUSIC_24", "music.svg"),
                        ("MUSIC_32", "music.svg"),
                        ("MUSIC_DURATION_24", "music_duration.svg"),
                        ("MUSIC_DURATION_32", "music_duration.svg"),
                        ("PLAY_16", "play.svg"),
                        ("PLAY_24", "play.svg"),
                        ("PLAY_PAUSE_16", "play_pause.svg"),
                        ("PLAY_PAUSE_d_16", "play_pause_d_16.png"),
                        ("ARROW_UP_16", "arrow_up.svg"),
                        ("ARROW_UP_D_16", "arrow_up_d_16.png"),
                        ("ARROW_DOWN_16", "arrow_down.svg"),
                        ("ARROW_DOWN_D_16", "arrow_down_d_16.png"),
                        ("REMOVE_16", "remove.svg"),
                        ("REMOVE_D_16", "remove_d_16.png"),
                        ("VIDEO_FORMAT_16", "video_format.svg"),
                        ("VIDEO_FORMAT_24", "video_format.svg"),
                        ("VIDEO_FORMAT_32", "video_format.svg"),

                        ("ALERT_16", "alert.svg"),
                        ("ALERT_24", "alert.svg"),
                        ("PROPERTIES_16", "properties.svg"),
                        ("EXIT_16", "exit.svg"),
                        ("HELP_16", "help.svg"),
                        ("ABOUT_16", "about.svg"),

                        ("FILMSTRIP", "filmstrip.png"),
                        ("DIA", "dia.svg"),
                        ("DIA_S", "dia_s.svg"),

                       )

        for idx, (imgName, imgFile) in enumerate(imgResources):
            file2py(os.path.join(imgDir, imgFile),
                    target, append=idx > 0,
                    resName=imgName)

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


class pfs_test(Command):

    description = "runs unit tests"

    user_options = []
    sub_commands = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        loader = unittest.TestLoader()
        suite = loader.discover("tests")
        runner = unittest.TextTestRunner()
        runner.run(suite)


class pfs_exe(Command):

    description = "create an executable dist for MS Windows (py2exe)"

    user_options = [
        ('target-dir=', 't', 'target directory'),
    ]
    sub_commands = [
        ('build', lambda x: True),
        ('build_exe', lambda x: True if build_exe else False)
                   ]

    def initialize_options(self):
        self.target_dir = os.path.join("build", "dist")

    def finalize_options(self):
        self.mkpath(self.target_dir)

    def run(self):
        build_exe = self.get_finalized_command('build_exe')
        build_exe.build_exe = self.target_dir

        self.distribution.executables = [
                 Executable(os.path.join("photofilmstrip", "GUI.py"),
                            base="Win32GUI",
                            targetName=Constants.APP_NAME + ".exe",
                            icon=os.path.join("res", "icon", "photofilmstrip.ico")
                            )
        ]
        self.distribution.executables.append(
                 Executable(os.path.join("photofilmstrip", "CLI.py"),
                            targetName=Constants.APP_NAME + "-cli.exe",
                            icon=os.path.join("res", "icon", "photofilmstrip.ico")
                            )
        )

        # Run all sub-commands (at least those that need to be run)
        for cmdName in self.get_sub_commands():
            self.run_command(cmdName)

        for targetDir, filelist in self.distribution.data_files:
            targetDir = os.path.join(self.target_dir, targetDir)
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)

            for f in filelist:
                self.copy_file(f, targetDir)

        site_packages = get_python_lib()
        targetDir = self.target_dir
        dllDirGnome = os.path.join(site_packages, "gst-dist")
        for dll in glob.glob(os.path.join(dllDirGnome, "bin", "*")):
            self.copy_file(os.path.join(dllDirGnome, "bin", dll),
                           os.path.join(targetDir, os.path.basename(dll)))

        targetDir = os.path.join(self.target_dir, "etc")
        self.copy_tree(os.path.join(dllDirGnome, "etc"),
                       targetDir)

        targetDir = os.path.join(self.target_dir, "share")
        self.copy_tree(os.path.join(dllDirGnome, "share"),
                       targetDir)

        targetDir = os.path.join(self.target_dir, "lib", "gstreamer-1.0")
        self.copy_tree(os.path.join(dllDirGnome, "lib", "gstreamer-1.0"),
                       targetDir)

        targetDir = os.path.join(self.target_dir, "lib", "girepository-1.0")
        self.mkpath(targetDir)
        for giTypeLib in ["GLib-2.0.typelib",
                          "GModule-2.0.typelib",
                          "GObject-2.0.typelib",
                          "Gst-1.0.typelib",
                          "GES-1.0.typelib",
                          "Gio-2.0.typelib",
                          "GstAudio-1.0.typelib",
                          "GstBase-1.0.typelib",
                          "GstController-1.0.typelib",
                          "GstPbutils-1.0.typelib",
                          "GstTag-1.0.typelib",
                          "GstVideo-1.0.typelib",
                          "cairo-1.0.typelib",
                          "GdkPixbuf-2.0.typelib",
                          "Pango-1.0.typelib",
                         ]:
            self.copy_file(os.path.join(dllDirGnome, "lib", "girepository-1.0", giTypeLib),
                           os.path.join(targetDir, giTypeLib))

        for exe in self.distribution.executables:
            self.add_exe_resources(exe.targetName, exe.icon)

    def add_exe_resources(self, exe_file, exe_icon):
        scmInfo = self.get_finalized_command('scm_info')

        from py2exe.icons import BuildIcons
        from py2exe.resources import UpdateResources
        from py2exe.versioninfo import Version, RT_VERSION
        from py2exe.runtime import RT_MANIFEST

        version = Version(
            version="%s.%s" % (Constants.APP_VERSION, 0),
            file_description=self.distribution.metadata.description,
            company_name=self.distribution.metadata.author,
            legal_copyright="(c) {} by {}".format(datetime.datetime.now().year,
                                                  self.distribution.metadata.author),
            original_filename=os.path.basename(exe_file),
            product_name=Constants.APP_NAME,
            product_version="%s-%s" % (Constants.APP_VERSION_SUFFIX, scmInfo.scm_rev)
        )
        versionBytes = version.resource_bytes()

        with UpdateResources(exe_file, delete_existing=True) as resWriter:
            resWriter.add(type=RT_VERSION, name=1, value=versionBytes)
            resWriter.add(type=RT_MANIFEST, name=1, value=MANIFEST_TEMPLATE.encode("utf-8"))

            for res_type, res_name, res_data in BuildIcons([(1, exe_icon)]):
                resWriter.add(type=res_type, name=res_name, value=res_data)


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

        ver = Constants.APP_VERSION_SUFFIX
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

        ver = Constants.APP_VERSION_SUFFIX

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
#            virtualFolder="PhotoFilmStrip-%s" % ver,
            stripFolders=2)
        log.info("    done.")


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


def file2py(source, python_file, append, resName):
    lines = []
    with open(source, "rb") as fid:
        raw_data = fid.read()
        data = base64.b64encode(raw_data)
    while data:
        part = data[:72]
        data = data[72:]
        output = '    %s' % part
        if not data:
            output += ")"
        lines.append(output)
    data = "\n".join(lines)

    mode = "a" if append else "w"
    with open(python_file, mode) as out:
        if not append:
            out.write("# This file was generated by %s\n#\n" % sys.argv[0])
            out.write("catalog = {}\n")
            out.write("index = []\n\n")

        varName = resName
        out.write("%s = (\n%s\n" % (varName, data))
        out.write("index.append('%s')\n" % resName)
        out.write("catalog['%s'] = %s\n" % (resName, varName))
        out.write("\n")

    print("Embedded %s using %s into %s" % (source, resName, python_file))


MANIFEST_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0" xmlns:asmv3="urn:schemas-microsoft-com:asm.v3">
  <assemblyIdentity version="1.0.0.0" processorArchitecture="*" name="PhotoFilmStrip" type="win32"></assemblyIdentity>
  <description>PhotoFilmStrip</description>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity type="win32" name="Microsoft.Windows.Common-Controls" version="6.0.0.0" processorArchitecture="*" publicKeyToken="6595b64144ccf1df" language="*"/>
    </dependentAssembly>
  </dependency>
  <asmv3:application>
    <asmv3:windowsSettings xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">
      <ms_windowsSettings:dpiAware xmlns:ms_windowsSettings="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true</ms_windowsSettings:dpiAware>
    </asmv3:windowsSettings>
  </asmv3:application>
</assembly>
"""

platform_scripts = []
platform_data = []
if os.name == "nt":
    platform_scripts.append(os.path.join("windows", "photofilmstrip.bat"))
    platform_scripts.append(os.path.join("windows", "photofilmstrip-cli.bat"))
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
                'build_sphinx'  : pfs_docs,
                'test'          : pfs_test,
                "build_exe"     : build_exe,
              },
    verbose=False,
    options={"build_exe": {
#                          "bundle_files":1,
                          "optimize": 2,
                          "include_msvcr": False,
                          "packages": ["gi", "photofilmstrip"],
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
                          "excludes": ["Tkconstants", "tkinter", "tcl",
                                       "PIL._imagingtk", "PIL.ImageTk",
                                       "_ssl", "numpy"]
                          },
               "sdist": {"formats": ["gztar"]},
               'build_sphinx': {"project": Constants.APP_NAME,
                                "release": Constants.APP_VERSION_SUFFIX,
                                "config_dir": 'docs/help',
                                "builder": ["html"]}
    },
    data_files=[
                (os.path.join("share", "doc", "photofilmstrip"), glob.glob("docs/*.*")),
                (os.path.join("share", "photofilmstrip", "audio"), glob.glob("data/audio/*.mp3")),
    ] + platform_data,
    scripts=[
             "scripts/photofilmstrip",
             "scripts/photofilmstrip-cli",
    ] + platform_scripts,

    name=Constants.APP_NAME.lower(),
    version=Constants.APP_VERSION_SUFFIX,
    license="GPLv2",
    description=Constants.APP_SLOGAN,
    long_description=Constants.APP_DESCRIPTION,
    author=Constants.DEVELOPERS[0],
    author_email="info@photofilmstrip.org",
    url=Constants.APP_URL,

    packages=['photofilmstrip',
              'photofilmstrip.action', 'photofilmstrip.cli',
              'photofilmstrip.core', 'photofilmstrip.core.renderer',
              'photofilmstrip.gui', 'photofilmstrip.gui.ctrls',
              'photofilmstrip.gui.util',
              'photofilmstrip.lib', 'photofilmstrip.lib.common',
              'photofilmstrip.lib.jobimpl',
              'photofilmstrip.res',
              'photofilmstrip.ux'],
    )
