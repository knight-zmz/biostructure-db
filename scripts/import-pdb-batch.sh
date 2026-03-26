#!/bin/bash
# 批量导入 PDB 结构脚本
# 从 RCSB PDB 数据库导入真实的蛋白质结构

set -e

API_URL="${API_URL:-http://localhost}"
MAX_ATOMS="${MAX_ATOMS:-50000}"  # 每个结构最大原子数

echo "🧬 PDB 批量导入工具"
echo "===================="
echo ""

# 经典的蛋白质结构列表 (来自 RCSB PDB)
PDB_IDS=(
    # 经典小蛋白
    "1CRN"  # Crambin - 植物蛋白
    "1UBQ"  # Ubiquitin - 泛素
    "1TIM"  # TIM Barrel - 磷酸丙糖异构酶
    
    # 重要功能蛋白
    "4HHB"  # Hemoglobin - 血红蛋白
    "1MBN"  # Myoglobin - 肌红蛋白
    "2SOD"  # Superoxide Dismutase - 超氧化物歧化酶
    
    # 酶类
    "1LYZ"  # Lysozyme - 溶菌酶
    "2CHA"  # Chymotrypsin - 胰凝乳蛋白酶
    "3TRY"  # Trypsin - 胰蛋白酶
    
    # 核酸相关
    "1BNA"  # B-DNA dodecamer
    "1ANA"  # A-DNA
    "5V7C"  # CRISPR-Cas9
    
    # 膜蛋白
    "1F88"  # Bacteriorhodopsin
    "2RH1"  # Beta-2 adrenergic receptor
    
    # 病毒蛋白
    "1R6Q"  # HIV-1 protease
    "6M0J"  # SARS-CoV-2 spike protein
    
    # 人类疾病相关
    "1TUP"  # Tumor suppressor p53
    "1JSP"  # BRCA1
    "5U8D"  # KRAS
    
    # 药物靶点
    "1IEP"  # HCV protease
    "3HT4"  # BACE1
    "5EN2"  # PARP1
    
    # 其他重要结构
    "1A4Y"  # Cytochrome c
    "7ZNT"  # Insulin
    "6VXX"  # Coronavirus main protease
)

echo "准备导入 ${#PDB_IDS[@]} 个 PDB 结构..."
echo "最大原子数限制：$MAX_ATOMS"
echo ""

success=0
failed=0

for pdb_id in "${PDB_IDS[@]}"; do
    echo -n "[$((success + failed + 1))/${#PDB_IDS[@]}] 导入 $pdb_id ... "
    
    result=$(curl -s -X POST "$API_URL/api/import/$pdb_id" \
        -H "Content-Type: application/json" \
        -d "{\"maxAtoms\": $MAX_ATOMS}")
    
    if echo "$result" | grep -q '"success":true'; then
        atoms=$(echo "$result" | grep -o '"atomsImported":[0-9]*' | cut -d: -f2)
        total=$(echo "$result" | grep -o '"totalAtoms":[0-9]*' | cut -d: -f2)
        echo "✅ ($atoms/$total 原子)"
        ((success++))
    else
        error=$(echo "$result" | grep -o '"error":"[^"]*"' | cut -d'"' -f4)
        echo "❌ $error"
        ((failed++))
    fi
    
    # 避免请求过快
    sleep 1
done

echo ""
echo "===================="
echo "导入完成！"
echo ""
echo "成功：$success"
echo "失败：$failed"
echo "总计：$((success + failed))"
echo ""
echo "访问 $API_URL 查看结果"
