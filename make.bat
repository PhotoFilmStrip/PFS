@echo off

rd /s /q dist
rd /s /q build\bdist.win32
C:\Python25\python.exe setup.py py2exe

"C:\Programme\Inno Setup 5\ISCC.exe" /Q photofilmstrip.iss