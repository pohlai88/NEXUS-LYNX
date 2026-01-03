# Test Strategy - LOCKED & ENFORCED

**Date:** 2026-01-27  
**Status:** ✅ **LOCKED** - No drift allowed  
**SSOT:** `MCP-TEST-EXECUTION-STRATEGY.md`

---

## 🔒 Final Canonical Configuration (Copy-Paste Ready)

### `pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
addopts = -v --tb=short
markers =
    integration: marks tests as integration tests (deselect with '-m "not integration"')
    performance: marks tests as performance tests (deselect with '-m "not performance"')
    stress: marks tests as stress/edge-case tests (deselect with '-m "not stress"')
    contract: marks tests as contract validation tests
```

### `tests/conftest.py` (Marker Registration)

```python
# Pytest markers - DO NOT MODIFY without updating SSOT
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "integration: marks tests as integration tests (deselect with '-m \"not integration\"')")
    config.addinivalue_line("markers", "performance: marks tests as performance tests")
    config.addinivalue_line("markers", "stress: marks tests as stress/edge-case tests")
    config.addinivalue_line("markers", "contract: marks tests as contract validation tests")
```

---

## 🚀 The 3 CI Gates (Minimal & Clean)

### Gate A: PR Gate
```bash
pytest -v -m "not performance and not stress"
```
**292 tests | ~2-3 min | Every PR**

### Gate B: Governance Gate
```bash
pytest -v tests/integration/test_cluster_mcp_complete.py
```
**16 tests | ~1 min | Main merge**

### Gate C: Edge-Case Gate
```bash
pytest -v -m stress
```
**22 tests | ~1-2 min | Main merge**

---

## 📊 Verified Counts (SSOT)

- **Total:** 329 tests
- **PR Gate:** 292 tests
- **Performance:** 15 tests
- **Stress:** 22 tests

---

## 🔒 Drift Prevention

**CI Scripts:**
- `lynx-ai/scripts/check-test-markers.sh` - Prevents `perf` marker
- `lynx-ai/scripts/verify-test-counts.sh` - Validates counts

**Forbidden:**
- ❌ `@pytest.mark.perf` (use `@pytest.mark.performance`)

**Historical Docs:**
- ⚠️ `TEST-COVERAGE-BEFORE-AFTER.md` (shows old 327/25 counts)

---

**Authority:** `MCP-TEST-EXECUTION-STRATEGY.md` is the ONLY SSOT

