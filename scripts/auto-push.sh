#!/bin/bash
# 自动推送 - 有网络时自动 push
cd /var/www/myapp
AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "0")
if [ "$AHEAD" -gt 0 ]; then
  echo "$(date): $AHEAD commits ahead, attempting push..."
  GIT_TERMINAL_PROMPT=0 timeout 20 git push origin main 2>/dev/null
  if [ $? -eq 0 ]; then
    echo "$(date): Push successful"
  else
    echo "$(date): Push failed (network issue)"
  fi
fi
