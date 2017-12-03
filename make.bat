@echo off

if %1!==! goto usage

set PYTHON=python.exe

git rev-parse --short HEAD > scm_rev.txt
set /p SCM_REV=<scm_rev.txt
del scm_rev.txt

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
%PYTHON% -c "from photofilmstrip import Constants;print Constants.APP_VERSION"
goto end

:package
%PYTHON% setup.py bdist_winport bdist_wininst
move dist\*.* release\
goto end


:usage
echo usage:
echo   make clean
echo   make compile
echo   make versioninfo
echo   make package

:end
