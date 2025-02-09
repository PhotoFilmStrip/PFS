# -*- coding: utf-8 -*-
#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2011 Jens Goepfert
#

import base64
import glob
import sys, os
import unittest
import zipfile
import logging

from setuptools import setup, Command
from setuptools.command.build import build
from setuptools.command.sdist import sdist

import pythongettext.msgfmt

try:
    from sphinx.application import Sphinx
except ImportError:
    Sphinx = None

try:
    from cx_Freeze.command.build_exe import build_exe
    from cx_Freeze import Executable
except ImportError:
    build_exe = None

from photofilmstrip import Constants

WORKDIR = os.path.dirname(os.path.abspath(sys.argv[0]))
log = logging.getLogger()


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
            with open(os.path.join("photofilmstrip", "_scmInfo.py"), "w") as fd:
                fd.write(f'SCM_REV = "{self.scm_rev}"\n')


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

        imgResources = (
                        ("ICON", "photofilmstrip.svg"),

                        ("PROJECT_NEW", "project_new.svg"),
                        ("PROJECT_OPEN", "project_open.svg"),
                        ("PROJECT_SAVE", "project_save.svg"),
                        ("PROJECT_SAVE_D", "project_save_d.svg"),
                        ("PROJECT_CLOSE", "project_close.svg"),
                        ("PROJECT_CLOSE_D", "project_close_d.svg"),
                        ("FOLDER_OPEN", "folder_open.svg"),

                        ("MOTION_START_TO_END", "motion_start_to_end.svg"),
                        ("MOTION_END_TO_START", "motion_end_to_start.svg"),
                        ("MOTION_SWAP", "motion_swap.svg"),
                        ("MOTION_MANUAL", "motion_manual.svg"),
                        ("MOTION_RANDOM", "motion_random.svg"),
                        ("MOTION_RANDOM_D", "motion_random_d.svg"),
                        ("MOTION_CENTER", "motion_center.svg"),
                        ("MOTION_CENTER_D", "motion_center_d.svg"),
                        ("LOCK", "lock.svg"),
                        ("UNLOCK", "unlock.svg"),

                        ("MENU", "menu.svg"),
                        ("ABORT", "abort.svg"),
                        ("LIST_REMOVE", "list_remove.svg"),

                        ("RENDER", "render.svg"),
                        ("RENDER_D", "render_d.svg"),
                        ("IMPORT_PICTURES", "import_pictures.svg"),
                        ("IMPORT_PICTURES_D", "import_pictures_d.svg"),
                        ("JOB_QUEUE", "job_queue.svg"),
                        ("JOB_QUEUE_D", "job_queue_d.svg"),

                        ("IMAGE_ROTATION_LEFT", "image_rotation_left.svg"),
                        ("IMAGE_ROTATION_LEFT_D", "image_rotation_left_d.svg"),
                        ("IMAGE_ROTATION_RIGHT", "image_rotation_right.svg"),
                        ("IMAGE_ROTATION_RIGHT_D", "image_rotation_right_d.svg"),
                        ("IMAGE_MOVING_LEFT", "image_moving_left.svg"),
                        ("IMAGE_MOVING_LEFT_D", "image_moving_left_d.svg"),
                        ("IMAGE_MOVING_RIGHT", "image_moving_right.svg"),
                        ("IMAGE_MOVING_RIGHT_D", "image_moving_right_d.svg"),
                        ("IMAGE_REMOVE", "image_remove.svg"),
                        ("IMAGE_REMOVE_D", "image_remove_d.svg"),

                        ("MUSIC", "music.svg"),
                        ("MUSIC_DURATION", "music_duration.svg"),
                        ("PLAY", "play.svg"),
                        ("PLAY_PAUSE", "play_pause.svg"),
                        ("PLAY_PAUSE_d", "play_pause_d.svg"),
                        ("ARROW_UP", "arrow_up.svg"),
                        ("ARROW_UP_D", "arrow_up_d.svg"),
                        ("ARROW_DOWN", "arrow_down.svg"),
                        ("ARROW_DOWN_D", "arrow_down_d.svg"),
                        ("REMOVE", "remove.svg"),
                        ("REMOVE_D", "remove_d.svg"),
                        ("VIDEO_FORMAT", "video_format.svg"),

                        ("ADD", "add.svg"),
                        ("ALERT", "alert.svg"),
                        ("PROPERTIES", "properties.svg"),
                        ("EXIT", "exit.svg"),
                        ("HELP", "help.svg"),
                        ("ABOUT", "about.svg"),

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

                msgfmt = pythongettext.msgfmt.Msgfmt(os.path.join("po", filename))
                with open(moFile, "wb") as moFd:
                    moFd.write(msgfmt.getAsFile().getbuffer())

                targetPath = os.path.join("share", "locale", lang, "LC_MESSAGES")
                self.distribution.data_files.append(
                    (targetPath, (moFile,))
                )


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
                            target_name=Constants.APP_NAME + ".exe",
                            icon=os.path.join("res", "icon", "photofilmstrip.ico")
                            )
        ]
        self.distribution.executables[0]._manifest = MANIFEST_TEMPLATE.encode("utf-8")
        self.distribution.executables.append(
                 Executable(os.path.join("photofilmstrip", "CLI.py"),
                            target_name=Constants.APP_NAME + "-cli.exe",
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

        exec_prefix = os.path.normpath(sys.exec_prefix)
        site_packages = os.path.join(exec_prefix, "Lib", "site-packages")
        targetDir = self.target_dir
        dllDirGnome = os.path.join(site_packages, "gst-dist")
        for dll in glob.glob(os.path.join(dllDirGnome, "bin", "*")):
            self.copy_file(os.path.join(dllDirGnome, "bin", dll),
                           os.path.join(targetDir, os.path.basename(dll)))

        for subFolder in ("etc", "share", "lib"):
            targetDir = os.path.join(self.target_dir, subFolder)
            self.copy_tree(os.path.join(dllDirGnome, subFolder),
                           targetDir)


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
            out.write("# This file was generated by %s\n#\n" % os.path.basename(sys.argv[0]))
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
    <asmv3:windowsSettings>
      <dpiAware xmlns="http://schemas.microsoft.com/SMI/2005/WindowsSettings">true</dpiAware>
      <dpiAwareness xmlns="http://schemas.microsoft.com/SMI/2016/WindowsSettings">PerMonitorV2</dpiAwareness>
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
                "sdist": pfs_sdist,
                "build": pfs_build,
                "bdist_win": pfs_exe,
                "bdist_winport": pfs_win_portable,
                "scm_info": pfs_scm_info,
                'build_sphinx': pfs_docs,
                "build_exe": build_exe,
              },
    verbose=False,
    options={"build_exe": {
#                          "bundle_files":1,
                          "optimize": 2,
                          "include_msvcr": False,
                          "packages": ["gi", "photofilmstrip"],
                          "includes": ["gi",
                                       "PIL.Image",
                                       "PIL.BlpImagePlugin",
                                       "PIL.BmpImagePlugin",
                                       "PIL.BufrStubImagePlugin",
                                       "PIL.CurImagePlugin",
                                       "PIL.DcxImagePlugin",
                                       "PIL.DdsImagePlugin",
                                       "PIL.EpsImagePlugin",
                                       "PIL.FitsImagePlugin",
                                       "PIL.FliImagePlugin",
                                       "PIL.FpxImagePlugin",
                                       "PIL.FtexImagePlugin",
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
                                       "PIL.Jpeg2KImagePlugin",
                                       "PIL.McIdasImagePlugin",
                                       "PIL.MicImagePlugin",
                                       "PIL.MpegImagePlugin",
                                       "PIL.MpoImagePlugin",
                                       "PIL.MspImagePlugin",
                                       "PIL.PalmImagePlugin",
                                       "PIL.PcdImagePlugin",
                                       "PIL.PcxImagePlugin",
                                       "PIL.PdfImagePlugin",
                                       "PIL.PixarImagePlugin",
                                       "PIL.PngImagePlugin",
                                       "PIL.PpmImagePlugin",
                                       "PIL.PsdImagePlugin",
                                       "PIL.QoiImagePlugin",
                                       "PIL.SgiImagePlugin",
                                       "PIL.SpiderImagePlugin",
                                       "PIL.SunImagePlugin",
                                       "PIL.TgaImagePlugin",
                                       "PIL.TiffImagePlugin",
                                       "PIL.WebPImagePlugin",
                                       "PIL.WmfImagePlugin",
                                       "PIL.XbmImagePlugin",
                                       "PIL.XpmImagePlugin",
                                       "PIL.XVThumbImagePlugin",
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
