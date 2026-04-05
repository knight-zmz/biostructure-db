#!/bin/bash
# JLU Protein Database v3.0 - Extended Test Suite

set -e

BASE_URL="https://jlupdb.me"
PASS=0
FAIL=0
TOTAL=0

test_endpoint() {
    local name="$1"
    local url="$2"
    local expected_code="${3:-200}"
    TOTAL=$((TOTAL + 1))
    echo -n "Testing: $name ... "
    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    if [ "$http_code" = "$expected_code" ]; then
        echo "✓ PASS (HTTP $http_code)"
        PASS=$((PASS + 1))
    else
        echo "✗ FAIL (HTTP $http_code, expected $expected_code)"
        FAIL=$((FAIL + 1))
    fi
}

test_api_response() {
    local name="$1"
    local url="$2"
    local expected_field="$3"
    TOTAL=$((TOTAL + 1))
    echo -n "Testing API: $name ... "
    response=$(curl -s "$url" 2>/dev/null)
    if echo "$response" | grep -q "$expected_field"; then
        echo "✓ PASS"
        PASS=$((PASS + 1))
    else
        echo "✗ FAIL"
        FAIL=$((FAIL + 1))
    fi
}

echo "=========================================="
echo "JLU Protein Database v3.0 - Extended Tests"
echo "=========================================="
echo ""

echo "--- Core Web Pages ---"
test_endpoint "Homepage" "$BASE_URL/" "200"
test_endpoint "Stats Page" "$BASE_URL/stats" "200"
test_endpoint "3D Viewer (1JLU)" "$BASE_URL/viewer/1JLU" "200"
test_endpoint "BLAST Search" "$BASE_URL/blast" "200"
test_endpoint "API Docs" "$BASE_URL/docs" "200"
test_endpoint "Health Check" "$BASE_URL/health" "200"

echo ""
echo "--- 3D Viewer ---"
test_endpoint "Viewer: Hemoglobin" "$BASE_URL/viewer/1JLU" "200"
test_endpoint "Viewer: GFP" "$BASE_URL/viewer/2ABC" "200"
test_endpoint "Viewer: SARS-CoV-2 Spike" "$BASE_URL/viewer/6M0J" "200"
test_endpoint "Viewer: CRISPR-Cas9" "$BASE_URL/viewer/7XYZ" "200"

echo ""
echo "--- API v1 ---"
test_api_response "List with Pagination" "$BASE_URL/api/v1/proteins?limit=2" "pagination"
test_api_response "Filter by Structure Class" "$BASE_URL/api/v1/proteins?structure_class=All+Alpha" "All Alpha"
test_api_response "Filter by Ligands" "$BASE_URL/api/v1/proteins?has_ligands=true" "has_ligands"
test_api_response "Search Keywords" "$BASE_URL/api/v1/proteins/search?q=oxygen" "OXYGEN"
test_api_response "BLAST API" "$BASE_URL/api/v1/blast?sequence=MVLSPADKTNVKAAWGKVGAHAGE" "Hemoglobin"
test_api_response "Stats with Atoms" "$BASE_URL/api/v1/stats" "total_atoms"
test_api_response "PDB URL endpoint" "$BASE_URL/api/v1/proteins/1JLU/pdb" "rcsb.org"

echo ""
echo "--- Data Quality ---"
test_api_response "Protein has R-free" "$BASE_URL/api/v1/proteins/1JLU" "r_free"
test_api_response "Protein has Authors" "$BASE_URL/api/v1/proteins/1JLU" "authors"
test_api_response "Protein has Keywords" "$BASE_URL/api/v1/proteins/1JLU" "keywords"
test_api_response "Protein has Structure Class" "$BASE_URL/api/v1/proteins/1JLU" "structure_class"
test_api_response "CRISPR entry exists" "$BASE_URL/api/v1/proteins/7XYZ" "CRISPR"
test_api_response "HIV Protease exists" "$BASE_URL/api/v1/proteins/2V0O" "HIV"

echo ""
echo "--- HTTPS & Infrastructure ---"
test_endpoint "HTTP→HTTPS Redirect" "http://jlupdb.me" "301"
test_endpoint "HTTPS Works" "$BASE_URL/health" "200"

echo ""
echo "=========================================="
echo "Results: $PASS/$TOTAL passed"
if [ $FAIL -eq 0 ]; then
    echo "🎉 All tests passed!"
    exit 0
else
    echo "⚠️  $FAIL tests failed"
    exit 1
fi
