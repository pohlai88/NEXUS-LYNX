# Test runner script for Lynx AI (PowerShell)

Write-Host "🧪 Running Lynx AI Test Suite" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Run all tests
uv run pytest -v

Write-Host ""
Write-Host "✅ Tests complete" -ForegroundColor Green

