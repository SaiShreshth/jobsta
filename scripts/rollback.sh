#!/bin/bash

echo "🚨 ROLLBACK INITIATED"

LAST_GOOD_COMMIT=$(git log --grep="✅" -n 1 --pretty=format:%H)

if [ -z "$LAST_GOOD_COMMIT" ]; then
  echo "❌ No safe commit found"
  exit 1
fi

git reset --hard $LAST_GOOD_COMMIT

echo "♻️ Rolled back to last safe commit: $LAST_GOOD_COMMIT"
