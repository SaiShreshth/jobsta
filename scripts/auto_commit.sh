#!/bin/bash

TASK_NAME=$1

if [ -z "$TASK_NAME" ]; then
  echo "❌ Task name required"
  exit 1
fi

GIT="/mnt/c/Program Files/Git/cmd/git.exe"

"$GIT" status --porcelain

if [ -z "$("$GIT" status --porcelain)" ]; then
  echo "⚠️ No changes to commit"
  exit 0
fi

"$GIT" add .
"$GIT" commit -m "✅ $TASK_NAME completed"

echo "✅ Auto-commit successful for $TASK_NAME"
