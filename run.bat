"bin\app.exe" grab -f "config" -o "\\" -l 2

git pull
git status
git add -A
git commit -m "Manual update"
git push
git status
