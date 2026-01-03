#!/usr/bin/env python3
"""
Quick validation script to verify test harness setup.

Checks:
1. All test files can be imported
2. All utility modules can be imported
3. Fixtures are available
4. No syntax errors
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all modules can be imported."""
    print("🔍 Checking imports...")
    
    errors = []
    
    # Test utility modules
    try:
        from tests.utils.http_assertions import assert_status_code, assert_content_type
        print("  ✅ tests.utils.http_assertions")
    except Exception as e:
        errors.append(f"  ❌ tests.utils.http_assertions: {e}")
    
    try:
        from tests.utils.json_contracts import validate_health_contract, validate_status_contract
        print("  ✅ tests.utils.json_contracts")
    except Exception as e:
        errors.append(f"  ❌ tests.utils.json_contracts: {e}")
    
    try:
        from tests.utils.html_selectors import parse_html, assert_kpi_cards_exist
        print("  ✅ tests.utils.html_selectors")
    except Exception as e:
        errors.append(f"  ❌ tests.utils.html_selectors: {e}")
    
    # Test test files
    try:
        from tests.integration.test_dashboard_endpoints import TestDashboardEndpoints
        print("  ✅ tests.integration.test_dashboard_endpoints")
    except Exception as e:
        errors.append(f"  ❌ tests.integration.test_dashboard_endpoints: {e}")
    
    try:
        from tests.integration.test_dashboard_contracts import TestHealthContract
        print("  ✅ tests.integration.test_dashboard_contracts")
    except Exception as e:
        errors.append(f"  ❌ tests.integration.test_dashboard_contracts: {e}")
    
    try:
        from tests.integration.test_dashboard_fragments import TestKPIFragment
        print("  ✅ tests.integration.test_dashboard_fragments")
    except Exception as e:
        errors.append(f"  ❌ tests.integration.test_dashboard_fragments: {e}")
    
    try:
        from tests.integration.test_dashboard_resilience import TestDegradationMode
        print("  ✅ tests.integration.test_dashboard_resilience")
    except Exception as e:
        errors.append(f"  ❌ tests.integration.test_dashboard_resilience: {e}")
    
    try:
        from tests.integration.test_dashboard_perf import TestResponseTimes
        print("  ✅ tests.integration.test_dashboard_perf")
    except Exception as e:
        errors.append(f"  ❌ tests.integration.test_dashboard_perf: {e}")
    
    # Test conftest fixtures
    try:
        import tests.conftest
        print("  ✅ tests.conftest (fixtures)")
    except Exception as e:
        errors.append(f"  ❌ tests.conftest: {e}")
    
    return errors

def test_dependencies():
    """Test that required dependencies are available."""
    print("\n🔍 Checking dependencies...")
    
    errors = []
    
    try:
        import httpx
        print(f"  ✅ httpx ({httpx.__version__})")
    except ImportError as e:
        errors.append(f"  ❌ httpx: {e}")
    
    try:
        import pytest
        print(f"  ✅ pytest ({pytest.__version__})")
    except ImportError as e:
        errors.append(f"  ❌ pytest: {e}")
    
    try:
        from bs4 import BeautifulSoup
        print("  ✅ beautifulsoup4")
    except ImportError as e:
        errors.append(f"  ❌ beautifulsoup4: {e}")
    
    return errors

def test_file_structure():
    """Test that all expected files exist."""
    print("\n🔍 Checking file structure...")
    
    project_root = Path(__file__).parent.parent
    expected_files = [
        "tests/integration/test_dashboard_endpoints.py",
        "tests/integration/test_dashboard_contracts.py",
        "tests/integration/test_dashboard_fragments.py",
        "tests/integration/test_dashboard_resilience.py",
        "tests/integration/test_dashboard_perf.py",
        "tests/utils/http_assertions.py",
        "tests/utils/json_contracts.py",
        "tests/utils/html_selectors.py",
        "tests/conftest.py",
    ]
    
    errors = []
    for file_path in expected_files:
        full_path = project_root / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            errors.append(f"  ❌ {file_path} (missing)")
    
    return errors

def main():
    """Run all validation checks."""
    print("=" * 60)
    print("API Test Harness Validation")
    print("=" * 60)
    
    all_errors = []
    
    # Check file structure
    all_errors.extend(test_file_structure())
    
    # Check dependencies
    all_errors.extend(test_dependencies())
    
    # Check imports
    all_errors.extend(test_imports())
    
    # Summary
    print("\n" + "=" * 60)
    if all_errors:
        print("❌ VALIDATION FAILED")
        print("\nErrors found:")
        for error in all_errors:
            print(error)
        sys.exit(1)
    else:
        print("✅ VALIDATION PASSED")
        print("\nAll test files and utilities are properly set up!")
        print("\nNext steps:")
        print("  1. Start dashboard: python -m lynx.api.dashboard")
        print("  2. Run tests: pytest tests/integration/test_dashboard_*.py -v")
        sys.exit(0)

if __name__ == "__main__":
    main()

