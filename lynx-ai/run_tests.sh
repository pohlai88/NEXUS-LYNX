#!/bin/bash
# Test runner script for Lynx AI

echo "🧪 Running Lynx AI Test Suite"
echo "================================"

# Run all tests
uv run pytest -v

echo ""
echo "✅ Tests complete"

