#!/usr/bin/bash

dotnet bin/ARM64/App.dll grab -f config -o ./ -l 0

git pull
git status
git add -A
git commit -m "Scheduled update"
git push
git status
