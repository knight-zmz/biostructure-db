#!/bin/bash
# 批量导入热门 PDB 结构
PDB_LIST="2POR 1A2C 1A3C 1A4C 1A5C 1A6C 1A7C 1A8C 1A9C 1AAC"
for PDB_ID in $PDB_LIST; do
  ./scripts/import-pdb.sh $PDB_ID
  sleep 1
done
