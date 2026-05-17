#!/usr/bin/env bash

set -euo pipefail

# Get the directory where the script is located
APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Set the working location to the script directory
cd "$APP_DIR"

# Define the path to the executable
EXE_PATH="$APP_DIR/bin/App.dll"

# Execute the application with arguments
dotnet "$EXE_PATH" grab -f "$APP_DIR/config" -o "$APP_DIR" -l 0

echo "[LOG] Execution of app.exe completed."

# --- Configuration ---
TODAY=$(date +"%d.%m.%Y")
YESTERDAY=$(date -d "yesterday" +"%d.%m.%Y")

TAG_TODAY="v$TODAY"
TAG_YESTERDAY="v$YESTERDAY"

# Your full list of files
FILE_LIST=(
    "epg.xml.gz"
    "all-2days.basic.epg.xml.gz"
    "all-2days.details.epg.xml.gz"
    "all-2days.full.epg.xml.gz"
    "all-3days.basic.epg.xml.gz"
    "all-3days.details.epg.xml.gz"
    "all-3days.full.epg.xml.gz"
    "bulgarian.3days.full.epg.xml.gz"
    "sport.epg.xml.gz"
    "tivibg.xml.gz"
    "vivacom.xml.gz"
    "a1.xml.gz"
)

TITLE="EPG Bundle ($TODAY)"
NOTES="Automated upload of Bulgarian and Global EPG files. Updated at $(date +"%H:%M:%S")."

echo "[LOG] Starting Process: $(date)"
echo "[LOG] Today's Tag: $TAG_TODAY"
echo "[LOG] Yesterday's Tag for cleanup: $TAG_YESTERDAY"


# --- 1. Process Today's Release ---
echo "[LOG] Checking if today's release ($TAG_TODAY) exists..."

if gh release view "$TAG_TODAY" &>/dev/null; then
    echo "[LOG] MATCH FOUND: Updating existing release with ${#FILE_LIST[@]} files..."
    
    gh release upload "$TAG_TODAY" "${FILE_LIST[@]}" --clobber
    gh release edit "$TAG_TODAY" --title "$TITLE" --notes "$NOTES"
else
    echo "[LOG] NO MATCH: Creating new release with ${#FILE_LIST[@]} files..."
    
    gh release create "$TAG_TODAY" "${FILE_LIST[@]}" --title "$TITLE" --notes "$NOTES"
fi

# --- 2. Cleanup Yesterday's Release ---
echo "[LOG] Checking for yesterday's release ($TAG_YESTERDAY)..."

if gh release view "$TAG_YESTERDAY" &>/dev/null; then
    echo "[LOG] Found yesterday's release. Deleting $TAG_YESTERDAY ..."
    
    DELETE_RESULT=$(gh release delete "$TAG_YESTERDAY" --yes --cleanup-tag)
    
    echo "GitHub Response: $DELETE_RESULT"
else
    echo "[LOG] No release found for yesterday. Skipping cleanup."
fi

echo "[SUCCESS] Operation completed at $(date)"

# Copy report.js
cp "report.js" "../harrygg.github.io/EPG/report.js"

echo "[LOG] Copied report.js to repository dir"

# Navigate to the sibling directory
REPO_DIR="$APP_DIR/../harrygg.github.io"

echo "[LOG] Moving to repository dir: $REPO_DIR"

cd "$REPO_DIR"

# Execute Git commands
echo "[LOG] Pulling latest changes..."
git pull

echo "[LOG] Current status before update:"
git status

echo "[LOG] Staging all changes..."
git add -A

echo "[LOG] Committing changes..."
git commit -m "Scheduled daily update" || echo "[LOG] No changes to commit."

echo "[LOG] Pushing to GitHub..."
git push

echo "[LOG] Final repository status:"
git status

# Return to the original application directory
echo "[LOG] Returning to $APP_DIR"

cd "$APP_DIR"



