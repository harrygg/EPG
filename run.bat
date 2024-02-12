@echo off

set APPDIR=%~dp0
cd %APPDIR%
%APPDIR%\bin\app.exe grab -f %APPDIR%\config -o %APPDIR% -l 0

git pull
git status
git add -A
git commit -m "Scheduled daily update"
git push
git status
