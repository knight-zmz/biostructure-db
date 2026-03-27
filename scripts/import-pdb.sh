#!/bin/bash
# PDB 导入脚本
PDB_ID=$1
if [ -z "$PDB_ID" ]; then
  echo "用法: ./import-pdb.sh <PDB_ID>"
  exit 1
fi
echo "📥 导入 PDB: $PDB_ID"
curl -s "https://files.rcsb.org/download/${PDB_ID}.pdb" > /tmp/${PDB_ID}.pdb
if [ -s /tmp/${PDB_ID}.pdb ]; then
  node scripts/import-pdb.js /tmp/${PDB_ID}.pdb
  echo "✅ 导入完成: $PDB_ID"
else
  echo "❌ 下载失败: $PDB_ID"
fi
