#!/bin/bash
# Check Test Markers - Prevent Drift
# 
# This script enforces marker name consistency and prevents drift.
# Run in CI to ensure no legacy markers are used.

set -e

echo "🔍 Checking test markers for drift prevention..."

# Check for forbidden marker names
FORBIDDEN_MARKERS=("perf" "perf_test" "perf-test")

FOUND_FORBIDDEN=false

for marker in "${FORBIDDEN_MARKERS[@]}"; do
    if grep -r "@pytest.mark.${marker}" tests/ --include="*.py" 2>/dev/null; then
        echo "❌ ERROR: Found forbidden marker '@pytest.mark.${marker}'"
        echo "   Use '@pytest.mark.performance' instead"
        FOUND_FORBIDDEN=true
    fi
done

# Check for correct marker usage
REQUIRED_MARKERS=("performance" "stress" "integration" "contract")

echo ""
echo "✅ Checking required markers are registered..."

# Verify markers are in pytest.ini
for marker in "${REQUIRED_MARKERS[@]}"; do
    if ! grep -q "${marker}:" pytest.ini; then
        echo "❌ ERROR: Marker '${marker}' not found in pytest.ini"
        FOUND_FORBIDDEN=true
    fi
done

# Verify markers are in conftest.py
for marker in "${REQUIRED_MARKERS[@]}"; do
    if ! grep -q "\"${marker}:" tests/conftest.py; then
        echo "❌ ERROR: Marker '${marker}' not registered in conftest.py"
        FOUND_FORBIDDEN=true
    fi
done

if [ "$FOUND_FORBIDDEN" = true ]; then
    echo ""
    echo "❌ Marker drift detected! Fix the issues above."
    echo "   See: docs/DEPLOYMENT/MCP-TEST-EXECUTION-STRATEGY.md"
    exit 1
fi

echo "✅ All markers are correct!"
echo ""
echo "📊 Marker Summary:"
echo "   - performance: ✅ (use this, not 'perf')"
echo "   - stress: ✅"
echo "   - integration: ✅"
echo "   - contract: ✅"

exit 0

