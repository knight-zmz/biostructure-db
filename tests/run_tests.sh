#!/bin/bash
# JLU Protein Database - Comprehensive Test Suite

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
        echo "✗ FAIL - Expected field '$expected_field' not found"
        FAIL=$((FAIL + 1))
    fi
}

echo "=========================================="
echo "JLU Protein Database - Test Suite"
echo "=========================================="
echo ""

# Web Pages
echo "--- Web Pages ---"
test_endpoint "Homepage" "$BASE_URL/" "200"
test_endpoint "Stats Page" "$BASE_URL/stats" "200"
test_endpoint "Protein Detail (1JLU)" "$BASE_URL/pdb/1JLU" "200"
test_endpoint "Protein Not Found" "$BASE_URL/pdb/XXXX" "404"
test_endpoint "API Docs (Swagger)" "$BASE_URL/docs" "200"
test_endpoint "Health Check" "$BASE_URL/health" "200"

echo ""
echo "--- API Endpoints ---"
test_endpoint "API: List Proteins" "$BASE_URL/api/v1/proteins" "200"
test_endpoint "API: Get Single Protein" "$BASE_URL/api/v1/proteins/1JLU" "200"
test_endpoint "API: Get Non-existent" "$BASE_URL/api/v1/proteins/XXXX" "404"
test_endpoint "API: Statistics" "$BASE_URL/api/v1/stats" "200"
test_endpoint "API: Search" "$BASE_URL/api/v1/proteins/search?q=hemoglobin" "200"
test_endpoint "API: FASTA Export" "$BASE_URL/api/v1/download/fasta" "200"
test_endpoint "API: JSON Export" "$BASE_URL/api/v1/download/json" "200"
test_endpoint "API: Single FASTA" "$BASE_URL/api/v1/proteins/1JLU/fasta" "200"

echo ""
echo "--- API Filtering ---"
test_api_response "Filter by Method" "$BASE_URL/api/v1/proteins?method=X-RAY+DIFFRACTION&limit=1" "X-RAY DIFFRACTION"
test_api_response "Filter by Organism" "$BASE_URL/api/v1/proteins?organism=Homo+sapiens&limit=1" "Homo sapiens"
test_api_response "Filter by Resolution" "$BASE_URL/api/v1/proteins?max_resolution=2.0&limit=1" "resolution"
test_api_response "Search Query" "$BASE_URL/api/v1/proteins/search?q=insulin" "Insulin"

echo ""
echo "--- HTTPS & Redirects ---"
test_endpoint "HTTP Redirect" "http://jlupdb.me" "301"
test_endpoint "HTTPS Works" "$BASE_URL/health" "200"

echo ""
echo "=========================================="
echo "Test Results"
echo "=========================================="
echo "Total Tests: $TOTAL"
echo "Passed: $PASS ✓"
echo "Failed: $FAIL ✗"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "🎉 All tests passed!"
    exit 0
else
    echo "⚠️  Some tests failed."
    exit 1
fi
