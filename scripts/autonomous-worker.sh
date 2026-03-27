#!/bin/bash
cd /var/www/myapp
TASK=$(python3 -c "
import json, os
try:
    d = json.load(open('WORK_STATE.json'))
    task = d['pendingTasks'][0] if d['pendingTasks'] else '检查服务状态并优化'
except: task = '检查服务状态并优化'
print(task)
" 2>/dev/null || echo "检查服务状态")

CONTEXT="项目目录: /var/www/myapp | 服务: PM2 myapp 端口3000 | 域名: https://jlupdb.me | GitHub: https://github.com/knight-zmz/biostructure-db"

openclaw agent \
  --message "你是 BioStructure DB 自主工作助手。$CONTEXT | 当前任务: $TASK | 要求: (1)直接在 /var/www/myapp 工作 (2)完成后更新 WORK_STATE.json 移除已完成任务 (3)git add + commit + push (4)不要汇报，直接干活 (5)遇到问题自行解决" \
  --channel qqbot \
  --to "6947BF9A4C6F62D7A8CA6B5574566A78" \
  --deliver \
  --thinking off
