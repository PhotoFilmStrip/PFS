"""
this is a cx_freeze init script
"""

import os
import sys

def run(name):
    os.environ["PYGI_DLL_DIRS"] = os.path.dirname(sys.executable)

    from freeze_core.initscripts import console
    console.run(name)
