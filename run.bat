cd %USERPROFILE%\Git\EPG

bin\app.exe grab -f %USERPROFILE%\config -o %USERPROFILE%\Git\EPG -l 0

git pull
git status
git add -A
git commit -m "Manual update"
git push
git status
