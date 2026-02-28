#!/bin/bash

./bin/osx-x64/App grab -f config/ -o ./ -l 0

git pull
git status
git add -A
git commit -m "Scheduled update on MacOS"
git push
git status
