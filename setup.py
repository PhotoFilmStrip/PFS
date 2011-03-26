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
import subprocess

import zipfile

if len(sys.argv) == 1:
    sys.argv.append("Compile")

from photofilmstrip.lib.Settings import Settings

from distutils import log
from distutils.command.build import build
from distutils.core import setup
from distutils.core import Command
from distutils.errors import DistutilsExecError
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
if not os.path.isfile(MSGFMT):
    MSGFMT = "msgfmt"


class Clean(Command):
        
    user_options = []

    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    
    def run(self):
        log.info("cleaning...")

        for directory in (os.path.join(WORKDIR, "dist"),
                          os.path.join(WORKDIR, "build", "bdist.win32"),
                          os.path.join(WORKDIR, "release"),
                          os.path.join(WORKDIR, "locale"),
                          ):
            if os.path.exists(directory):
                remove_tree(directory, 1)

        for fname in (os.path.join(WORKDIR, "version.info"),
                      os.path.join(WORKDIR, "_svnInfo.py"),
                      os.path.join(WORKDIR, "_svnInfo.pyc"),
                      os.path.join(WORKDIR, "_svnInfo.pyo")):
            if os.path.exists(fname):
               os.remove(fname)
           
        log.info("    done.")


class Test(Command):
        
    user_options = []

    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        pass

class pfs_build(build):
    def initialize_options(self):
        build.initialize_options(self)
    def finalize_options(self):
        build.finalize_options(self)
        
        self.sub_commands.append(("Compile", None))


class Compile(Command):
    user_options = []
    sub_commands = [('Clean',   lambda x: True),
#                    ('Test',    lambda x: True),
                   ]
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        # Run all sub-commands (at least those that need to be run)
        for cmdName in self.get_sub_commands():
            self.run_command(cmdName)
    
        self._make_svn_info()
        self._make_resources()
        self._make_locale()
        
    def _make_svn_info(self):
        if os.path.isfile(".svn/entries"):
            svnRev = open(".svn/entries", "r").readlines()[3].strip()
        else:
            svnRev = 0

        for target in getattr(self.distribution, "windows", []) + \
                      getattr(self.distribution, "console", []):
            target.Update(svnRev)
        
        fd = open("_svnInfo.py", "w")
        fd.write("SVN_REV = \"%s\"\n" % svnRev)
        fd.close()
        
    def _make_resources(self):
        from wx.tools.img2py import img2py
        imgDir = os.path.abspath(os.path.join("res", "icons"))
        target = os.path.join("photofilmstrip", "res", "images.py")
        
        idx = 0
        for imgName, imgFile in (
#                                 ("ALIGN_BOTTOM", "align_bottom.png"),
#                                 ("ALIGN_MIDDLE", "align_middle.png"),
#                                 ("ALIGN_TOP", "align_top.png"),
#                                 ("ALIGN_LEFT", "align_left.png"),
#                                 ("ALIGN_CENTER", "align_center.png"),
#                                 ("ALIGN_RIGHT", "align_right.png"),
                                 ("PLAY_PAUSE", "play_pause_16.png"),
                                 ("MOTION_RIGHT", "motion_right_24.png"),
                                 ("MOTION_LEFT", "motion_left_24.png"),
                                 ("MOTION_INPUT", "motion_input_24.png"),
                                 ("MOTION_RANDOM", "motion_random_24.png"),
                                 ("ICON_32", "photofilmstrip_32.png"),
                                 ("ICON_48", "photofilmstrip_48.png")
                                 ):
            
            img2py(os.path.join(imgDir, imgFile), 
                   target, append=idx>0, imgName=imgName, icon=True, compressed=True, catalog=True)
            idx += 1
            
    def _make_locale(self):
        for filename in os.listdir("po"):
            lang, ext = os.path.splitext(filename)
            if ext.lower() == ".po":
                moDir =  os.path.join("build", "mo", lang, "LC_MESSAGES")
                moFile = os.path.join(moDir, "%s.mo" % Settings.APP_NAME)
                if not os.path.exists(moDir):
                    os.makedirs(moDir)
                code = subprocess.call([MSGFMT, "-o",
                                        moFile,
                                        os.path.join("po", lang)])
                if code != 0:
                    raise RuntimeError("msgfmt %s: %s" % (lang, code))
                
                targetPath = os.path.join("share", "locale", lang, "LC_MESSAGES")
                self.distribution.data_files.append(
                    (targetPath, (moFile,))
                )


class WinRelease(Command):
    user_options = []
    sub_commands = [('Compile', lambda x: True),
                    ('py2exe',  lambda x: True if py2exe else False)                    
                   ]

    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        # Run all sub-commands (at least those that need to be run)
        for cmdName in self.get_sub_commands():
            self.run_command(cmdName)
            
        targetDir = os.path.join("dist", "extBin", "mplayer")
        Unzip(os.path.join("windows", "MPlayer-mingw32-1.0rc2.zip"),
              targetDir, 
              stripFolders=1)
        

class WinSetup(Command):
    
    user_options = []
    sub_commands = [('WinRelease', lambda x: True),
                   ]

    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        # Run all sub-commands (at least those that need to be run)
        for cmdName in self.get_sub_commands():
            self.run_command(cmdName)
    
        ver = Settings.APP_VERSION
        open(os.path.join(WORKDIR, "version.info"), "w").write(ver)
        
        log.info("building installer...")
        code = subprocess.call([INNO, "/Q", 
                                "/F%s-%s" % ("setup_photofilmstrip", ver), 
                                "windows\\photofilmstrip.iss"])
        if code != 0:
            raise DistutilsExecError("InnoSetup")
        log.info("    done.")


class WinPortable(Command):
    user_options = []
    sub_commands = [('WinRelease', lambda x: True),
                   ]

    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        # Run all sub-commands (at least those that need to be run)
        for cmdName in self.get_sub_commands():
            self.run_command(cmdName)
            
        ver = Settings.APP_VERSION
        log.info("building portable zip...")
        if not os.path.exists("release"):
            os.makedirs("release")
            
        Zip(os.path.join("release", "photofilmstrip-%s.zip" % ver), 
            "dist", 
            virtualFolder="PhotoFilmStrip-%s" % ver,
            stripFolders=1)
        log.info("    done.")


class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.product_version = Settings.APP_VERSION
        self.version = "%s.%s" % (self.product_version, 0)
        self.company_name = ""
        self.copyright = "(c) 2011"
        self.name = "%s %s" % (Settings.APP_NAME, self.product_version)
        self.description = self.name
        self.other_resources = [(RT_MANIFEST, 1, MANIFEST % dict(prog=Settings.APP_NAME))]
        
        logo = os.path.join("res", "icon", "photofilmstrip.ico")
        self.icon_resources = [(1, logo)]
        
    def Update(self, svnVer):
        self.version = "%s.%s" % (self.product_version, svnVer)


def Zip(zipFile, srcDir, stripFolders=0, virtualFolder=None):
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
            log.debug("  zipping %s" % zipTarget)
            zf.write(os.path.join(dirpath, fname), zipTarget)
    zf.close()


def Unzip(zipFile, targetDir, stripFolders=0):
    log.info("extracting %s to %s" % (zipFile, targetDir))
    if not os.path.isdir(targetDir):
        os.makedirs(targetDir)

    zf = zipfile.ZipFile(zipFile, "r")
    for ele in zf.namelist():
        eleInfo = zf.getinfo(ele)
        if eleInfo.file_size == 0:
            continue

        log.debug("  extracting %s (%s)" % (ele, eleInfo.file_size))
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



RT_MANIFEST = 24
MANIFEST = '''<assembly xmlns="urn:schemas-microsoft-com:asm.v1"
manifestVersion="1.0">
  <assemblyIdentity
    version="0.6.8.0"
    processorArchitecture="x86"
    name="%(prog)s"
    type="win32"
  />
  <description>%(prog)s Program</description>
  <trustInfo xmlns="urn:schemas-microsoft-com:asm.v3">
    <security>
      <requestedPrivileges>
        <requestedExecutionLevel
          level="asInvoker"
          uiAccess="false"
        />
      </requestedPrivileges>
    </security>
  </trustInfo>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
        type="win32"
        name="Microsoft.VC90.CRT"
        version="9.0.21022.8"
        processorArchitecture="x86"
        publicKeyToken="1fc8b3b9a1e18e3b"
      />
    </dependentAssembly>
  </dependency>
  <dependency>
    <dependentAssembly>
      <assemblyIdentity
        type="win32"
        name="Microsoft.Windows.Common-Controls"
        version="6.0.0.0"
        processorArchitecture="x86"
        publicKeyToken="6595b64144ccf1df"
        language="*"
      />
    </dependentAssembly>
  </dependency>
</assembly>'''


DESCRIPTION = """\
PhotoFilmStrip creates movies out of your pictures in just 3 steps. First select your photos, customize the motion path and render the video. There are several output possibilities for VCD, SVCD, DVD up to FULL-HD.
"""


setup(
    cmdclass={
                "Clean"      : Clean,
                "Test"       : Test,
                "build"      : pfs_build,
                "Compile"    : Compile,
                "WinRelease" : WinRelease,
                "WinSetup"   : WinSetup,
                "WinPortable": WinPortable,
              },
    verbose=False,
    options = {"py2exe": {"compressed": 2,
#                          "bundle_files":1,
                          "optimize": 2,
                          "dll_excludes": ["msvcr90.dll", "msvcp90.dll"],
                          "excludes": ["Tkconstants", "Tkinter", "tcl", 
                                       "_imagingtk", "PIL._imagingtk", "ImageTk", "PIL.ImageTk", "FixTk", 
                                       "_ssl"]
                          }
    },
    windows=[Target(script = "src/photofilmstrip-gui.py",
                    dest_base = "bin/" + Settings.APP_NAME
                    ),
    ],
    console=[Target(script = "src/photofilmstrip-cli.py",
                    dest_base = "bin/" + Settings.APP_NAME + "-cli"
                    )
    ],
    zipfile = "lib/modules",
    data_files=[("doc\\photofilmstrip", glob.glob("doc\\photofilmstrip\\*.*")),
                ("share\\music", glob.glob("res\\audio\\*.mp3")),
    ],

    name = Settings.APP_NAME,
    version = Settings.APP_VERSION,
    license = "GPLv2",
    description = "PhotoFilmStrip - Creates movies out of your pictures.",
    long_description = DESCRIPTION,
    author = "Jens Goepfert",
    author_email = "info@photofilmstrip.org",
    url = Settings.APP_URL,
       
    packages = ['photofilmstrip', 
                'photofilmstrip.cli', 
                'photofilmstrip.core', 'photofilmstrip.core.backend', 'photofilmstrip.core.renderer',
                'photofilmstrip.gui', 'photofilmstrip.gui.ctrls', 'photofilmstrip.gui.util',
                'photofilmstrip.lib', 'photofilmstrip.lib.common',
                'photofilmstrip.res'],
#    package_dir={'pfs': 'src'},
    )
