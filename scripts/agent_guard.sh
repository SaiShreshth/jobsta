#!/bin/bash

TASK_NAME=$1

if [ -z "$TASK_NAME" ]; then
  echo "❌ Task name missing"
  exit 1
fi

PYTHON=/mnt/c/Users/saish/Documents/projs/jobsta/.venv/Scripts/python.exe

echo "🔍 Running guard for $TASK_NAME"

# 1. Python syntax check
$PYTHON -m compileall app/ || exit 1

# 2. Flask import check
$PYTHON - <<EOF
from app import create_app
app = create_app()
print("Flask app loaded successfully")
EOF

if [ $? -ne 0 ]; then
  echo "❌ App failed to load"
  exit 1
fi

# 3. Tests (if present)
if [ -d "tests" ] && [ "$(ls -A tests)" ]; then
  $PYTHON -m pytest || exit 1
fi

# 4. Checklist update check
grep -q "$TASK_NAME" CHECKLIST.md || {
  echo "❌ Checklist not updated"
  exit 1
}

# 5. Auto-commit
bash scripts/auto_commit.sh "$TASK_NAME"

echo "✅ Guard passed for $TASK_NAME"
