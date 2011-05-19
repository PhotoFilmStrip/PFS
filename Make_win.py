#
# PhotoFilmStrip - Creates movies out of your pictures.
#
# Copyright (C) 2008 Jens Goepfert
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

import logging
logging.basicConfig(level=logging.INFO,
                    format='%(message)s')

import os
import sys
import subprocess
import shutil
import zipfile


WORKDIR = os.path.dirname(os.path.abspath(sys.argv[0]))
PYTHON  = r"C:\Python25\python.exe"
INNO    = r"C:\Programme\Inno Setup 5\ISCC.exe"
MSGFMT  = r"C:\Python25\Tools\i18n\msgfmt.py"

class Args:
    PY2EXE = []


def check():
    logging.info("checking for PIL...")
    try:
        import Image
    except ImportError:
        logging.error("Please install python-imaging-library (PIL) - http://www.pythonware.com/products/pil/")
        sys.exit(1)
    logging.info("    ok.")

    logging.info("checking for wxPython...")
    try:
        import wx
        logging.info("    ok.")
    except ImportError:
        Args.PY2EXE.append("nogui")
        logging.warn("    not found! No GUI will be available.")
        logging.error("Please install wxPython - http://www.wxpython.org/")

    logging.info("checking for py2exe...")
    try:
        import py2exe
    except ImportError:
        logging.error("Please install py2exe - http://www.py2exe.org/")
        sys.exit(1)
    logging.info("    ok.")

    logging.info("checking for python executable...")
    if not os.path.exists(PYTHON):
        logging.error("Please setup the python executable in this script!")
        sys.exit(1)
    logging.info("    ok.")

    logging.info("checking for Inno Setup Compiler...")
    if not os.path.exists(INNO):
        logging.error("Please install Inno Setup Compiler - http://www.innosetup.com/")
        logging.error("Please setup the Inno Setup Compiler executable in this script!")
        sys.exit(1)
    logging.info("    ok.")


def getVersion(silent=False):
    if not silent:
        logging.info("determine PhotoFilmStrip version...")
    sys.path.insert(0, os.path.abspath("src"))
    import lib.Settings
    ver = lib.Settings.Settings.APP_VERSION
    sys.path.pop(0)
    if not silent:
        logging.info("    found version: %s", ver)
    return ver

def clean():
    logging.info("cleaning...")
    if os.path.exists(os.path.join(WORKDIR, "dist")):
        shutil.rmtree(os.path.join(WORKDIR, "dist"), True)
       
    if os.path.exists(os.path.join(WORKDIR, "build", "bdist.win32")):
        shutil.rmtree(os.path.join(WORKDIR, "build", "bdist.win32"), True)

    if os.path.exists(os.path.join(WORKDIR, "release")):
        shutil.rmtree(os.path.join(WORKDIR, "release"), True)

    if os.path.exists(os.path.join(WORKDIR, "locale")):
        shutil.rmtree(os.path.join(WORKDIR, "locale"), True)

    if os.path.exists(os.path.join(WORKDIR, "version.info")):
        os.remove(os.path.join(WORKDIR, "version.info"))

    logging.info("    done.")

def compile():
    clean()
    os.chdir(WORKDIR)

    for filename in os.listdir("po"):
        base, ext = os.path.splitext(filename)
        if ext.lower() == ".po":
            path = "locale\\%s\\LC_MESSAGES" % base
            if not os.path.exists(path):
                os.makedirs(path)
            
            code = subprocess.call([MSGFMT, "-o",
                                    os.path.join(path, "PhotoFilmStrip.mo"),
                                    os.path.join("po", base)], shell=True)
            if code != 0:
                sys.exit(code)
    logging.info("running py2exe...")
    code = subprocess.call([PYTHON, "setup.py", "py2exe"] +Args.PY2EXE, shell=True)
    if code != 0:
        sys.exit(code)

    targetDir = os.path.join("dist", "extBin", "mplayer")
    Unzip(os.path.join("win32extBin", "MPlayer-mingw32-1.0rc2.zip"),
          targetDir, 
          stripFolders=1)

    logging.info("    done.")

def package():
    if not os.path.exists(os.path.join(WORKDIR, "dist")):
        compile()
    ver = getVersion()
    logging.info("building installer...")
    code = subprocess.call([INNO, "/Q", "/F%s-%s" % ("setup_photofilmstrip", ver), "photofilmstrip.iss"])
    if code != 0:
        sys.exit(code)
    logging.info("    done.")

    logging.info("building portable zip...")
    if not os.path.exists("release"):
        os.makedirs("release")
    Zip(os.path.join("release", "photofilmstrip-%s.zip" % ver), 
        "dist", 
        virtualFolder="PhotoFilmStrip-%s" % ver,
        stripFolders=1)
    logging.info("    done.")


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
            logging.debug("  zipping %s" % zipTarget)
            zf.write(os.path.join(dirpath, fname), zipTarget)
    zf.close()


def Unzip(zipFile, targetDir, stripFolders=0):
    logging.info("extracting %s to %s" % (zipFile, targetDir))
    if not os.path.isdir(targetDir):
        os.makedirs(targetDir)

    zf = zipfile.ZipFile(zipFile, "r")
    for ele in zf.namelist():
        eleInfo = zf.getinfo(ele)
        if eleInfo.file_size == 0:
            continue

        logging.debug("  extracting %s (%s)" % (ele, eleInfo.file_size))
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


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "versioninfo":
            print getVersion(True)
            sys.exit(0)

    logging.info("PhotoFilmStrip Microsoft Windows builder")
    check()

    if len(sys.argv) > 1:
        if sys.argv[1] == "clean":
            clean()
        elif sys.argv[1] == "compile":
            compile()
        elif sys.argv[1] == "package":
            package()
        sys.exit(0)

    package()
    logging.info("all done.")
