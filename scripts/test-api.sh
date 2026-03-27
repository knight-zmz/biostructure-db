#!/bin/bash
# API 测试脚本
echo "=== API 测试 ==="
echo "1. 基础统计:"
curl -s http://localhost:3000/api/stats | head -c 100
echo ""
echo "2. 生物统计:"
curl -s http://localhost:3000/api/bio/stats | head -c 100
echo ""
echo "3. 数据库信息:"
curl -s http://localhost:3000/api/bio/info | head -c 100
echo ""
echo "4. 二级结构:"
curl -s http://localhost:3000/api/bio/secondary/1CRN | head -c 100
echo ""
echo "✅ 测试完成"
