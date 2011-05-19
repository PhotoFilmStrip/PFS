@echo off

if %1!==! goto usage

set PYTHON=C:\Python27\python.exe

if "%1"=="compile" goto compile
if "%1"=="clean" goto clean
if "%1"=="package" goto package
if "%1"=="versioninfo" goto versioninfo
goto end

:compile
%PYTHON% setup.py build
goto end

:clean
%PYTHON% setup.py clean
goto end

:versioninfo
%PYTHON% -c "import photofilmstrip.lib.Settings;print photofilmstrip.lib.Settings.Settings.APP_VERSION"
goto end

:package
%PYTHON% setup.py bdist_winport bdist_wininst sdist
goto end


:usage
echo usage:
echo   make clean
echo   make compile
echo   make versioninfo
echo   make package

:end
