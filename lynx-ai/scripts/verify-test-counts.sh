#!/bin/bash
# Verify Test Counts Match SSOT
#
# This script verifies test counts match the SSOT document.
# Run in CI to ensure counts haven't drifted.

set -e

echo "🔍 Verifying test counts match SSOT..."
echo ""

cd "$(dirname "$0")/.." || exit 1

# Expected counts from SSOT
EXPECTED_TOTAL=329
EXPECTED_PR_GATE=292
EXPECTED_PERFORMANCE=15
EXPECTED_STRESS=22

# Get actual counts
TOTAL=$(python -m pytest --collect-only -q 2>/dev/null | grep -oP '\d+(?= selected)' | tail -1 || echo "0")
PR_GATE=$(python -m pytest --collect-only -m "not performance and not stress" -q 2>/dev/null | grep -oP '\d+(?= selected)' | tail -1 || echo "0")
PERFORMANCE=$(python -m pytest --collect-only -m performance -q 2>/dev/null | grep -oP '\d+(?= selected)' | tail -1 || echo "0")
STRESS=$(python -m pytest --collect-only -m stress -q 2>/dev/null | grep -oP '\d+(?= selected)' | tail -1 || echo "0")

echo "📊 Test Count Verification:"
echo "   Total:      Expected ${EXPECTED_TOTAL}, Got ${TOTAL}"
echo "   PR Gate:    Expected ${EXPECTED_PR_GATE}, Got ${PR_GATE}"
echo "   Performance: Expected ${EXPECTED_PERFORMANCE}, Got ${PERFORMANCE}"
echo "   Stress:     Expected ${EXPECTED_STRESS}, Got ${STRESS}"
echo ""

ERRORS=0

if [ "$TOTAL" != "$EXPECTED_TOTAL" ]; then
    echo "❌ ERROR: Total test count mismatch!"
    echo "   Expected: ${EXPECTED_TOTAL}, Got: ${TOTAL}"
    echo "   Update docs/DEPLOYMENT/MCP-TEST-EXECUTION-STRATEGY.md if this is intentional"
    ERRORS=$((ERRORS + 1))
fi

if [ "$PR_GATE" != "$EXPECTED_PR_GATE" ]; then
    echo "❌ ERROR: PR Gate test count mismatch!"
    echo "   Expected: ${EXPECTED_PR_GATE}, Got: ${PR_GATE}"
    echo "   Update docs/DEPLOYMENT/MCP-TEST-EXECUTION-STRATEGY.md if this is intentional"
    ERRORS=$((ERRORS + 1))
fi

if [ "$PERFORMANCE" != "$EXPECTED_PERFORMANCE" ]; then
    echo "❌ ERROR: Performance test count mismatch!"
    echo "   Expected: ${EXPECTED_PERFORMANCE}, Got: ${PERFORMANCE}"
    echo "   Update docs/DEPLOYMENT/MCP-TEST-EXECUTION-STRATEGY.md if this is intentional"
    ERRORS=$((ERRORS + 1))
fi

if [ "$STRESS" != "$EXPECTED_STRESS" ]; then
    echo "❌ ERROR: Stress test count mismatch!"
    echo "   Expected: ${EXPECTED_STRESS}, Got: ${STRESS}"
    echo "   Update docs/DEPLOYMENT/MCP-TEST-EXECUTION-STRATEGY.md if this is intentional"
    ERRORS=$((ERRORS + 1))
fi

if [ $ERRORS -eq 0 ]; then
    echo "✅ All test counts match SSOT!"
    exit 0
else
    echo ""
    echo "❌ Test count drift detected! Fix the issues above."
    echo "   SSOT: docs/DEPLOYMENT/MCP-TEST-EXECUTION-STRATEGY.md"
    exit 1
fi

