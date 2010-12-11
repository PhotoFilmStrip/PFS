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

import sys, os

sys.path.insert(0, "src")

from lib.Settings import Settings
open("version.info", "w").write(Settings.APP_VERSION)

# If run without args, build executables, in quiet mode.
if len(sys.argv) == 1:
    sys.argv.append("py2exe")
#    sys.argv.append("-q")
#    sys.argv.append("-b 2")

NO_GUI = False
if "nogui" in sys.argv:
    NO_GUI = True
    sys.argv.remove("nogui")


from distutils.core import setup
import py2exe
import glob


class Target:
    def __init__(self, **kw):
        self.__dict__.update(kw)
        self.version = Settings.APP_VERSION
        self.product_version = Settings.APP_VERSION
        self.company_name = ""
        self.copyright = "(c) 2008"
        self.name = "%s %s" % (Settings.APP_NAME, Settings.APP_VERSION)
        self.description = self.name


manifest_template = '''
<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<assembly xmlns="urn:schemas-microsoft-com:asm.v1" manifestVersion="1.0">
<assemblyIdentity
    version="5.0.0.0"
    processorArchitecture="x86"
    name="%(prog)s"
    type="win32"
/>
<description>%(prog)s Program</description>
<dependency>
    <dependentAssembly>
        <assemblyIdentity
            type="win32"
            name="Microsoft.Windows.Common-Controls"
            version="6.0.0.0"
            processorArchitecture="X86"
            publicKeyToken="6595b64144ccf1df"
            language="*"
        />
    </dependentAssembly>
</dependency>
</assembly>
'''

logo = os.path.join("res","icon", "photofilmstrip.ico")

RT_MANIFEST = 24

pfs_gui = Target(
    script = "src/photofilmstrip-cli.py" if NO_GUI else "src/photofilmstrip-gui.py",
    other_resources = [(RT_MANIFEST, 1, manifest_template % dict(prog=Settings.APP_NAME))],
    icon_resources = [(1, logo)],
    dest_base = "bin/" + Settings.APP_NAME,
    )

pfs_cli = Target(
    script = "src/photofilmstrip-cli.py",
    other_resources = [(RT_MANIFEST, 1, manifest_template % dict(prog=Settings.APP_NAME))],
    icon_resources = [(1, logo)],
    dest_base = "bin/" + Settings.APP_NAME + "-cli",
    )

setup(
    verbose = False,
    options = {"py2exe": {
        "compressed": 2,
#        "bundle_files":1,
        "optimize": 2
    }},
    console = [pfs_cli, pfs_gui] if NO_GUI else [pfs_cli],
    windows = [] if NO_GUI else [pfs_gui],
    zipfile = "lib/modules",
    data_files=[("doc\\photofilmstrip", glob.glob("doc\\photofilmstrip\\*.*")),
                ("share\\music", glob.glob("res\\audio\\*.mp3")),
                ("locale\\de\\LC_MESSAGES", glob.glob("locale\\de\\LC_MESSAGES\\*.mo")),
                ("locale\\fr\\LC_MESSAGES", glob.glob("locale\\fr\\LC_MESSAGES\\*.mo")),
                ("locale\\en\\LC_MESSAGES", glob.glob("locale\\en\\LC_MESSAGES\\*.mo")),
                ("locale\\cs\\LC_MESSAGES", glob.glob("locale\\cs\\LC_MESSAGES\\*.mo")),
                ("locale\\pt\\LC_MESSAGES", glob.glob("locale\\pt\\LC_MESSAGES\\*.mo")),
                ("locale\\it\\LC_MESSAGES", glob.glob("locale\\it\\LC_MESSAGES\\*.mo")),
                ("lib", ["C:\\Python25\\lib\\site-packages\\wx-2.8-msw-unicode\\wx\MSVCP71.dll"]),
    ]
    )
