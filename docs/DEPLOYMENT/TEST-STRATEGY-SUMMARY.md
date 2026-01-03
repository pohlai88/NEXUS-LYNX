# Test Strategy Summary - Quick Reference

**Date:** 2026-01-27  
**SSOT:** `docs/DEPLOYMENT/MCP-TEST-EXECUTION-STRATEGY.md`  
**Status:** ✅ **LOCKED** - No drift allowed

---

## 🎯 The 3 CI Gates (Minimal & Clean)

### Gate A: PR Gate (Every PR)
```bash
pytest -v -m "not performance and not stress"
```
**Expected:** 292 tests | **Duration:** ~2-3 min

### Gate B: Governance Gate (Main Merge)
```bash
pytest -v tests/integration/test_cluster_mcp_complete.py
```
**Expected:** 16 tests | **Duration:** ~1 min

### Gate C: Edge-Case Gate (Main Merge)
```bash
pytest -v -m stress
```
**Expected:** 22 tests | **Duration:** ~1-2 min

---

## 📊 Verified Test Counts (SSOT)

| Category | Count | Marker |
|----------|-------|--------|
| **Total** | **329** | All tests |
| **PR Gate** | **292** | `not performance and not stress` |
| **Performance** | **15** | `@pytest.mark.performance` |
| **Stress** | **22** | `@pytest.mark.stress` |
| **Integration** | **~46** | `@pytest.mark.integration` |
| **Contract** | **~32** | `@pytest.mark.contract` |

---

## 🔒 Frozen Configuration

**Marker Names (DO NOT CHANGE):**
- ✅ `performance` (NOT `perf`)
- ✅ `stress`
- ✅ `integration`
- ✅ `contract`

**CI Enforcement:**
- `scripts/check-test-markers.sh` - Prevents `perf` marker
- `scripts/verify-test-counts.sh` - Validates counts match SSOT

---

## ⚠️ Historical Documents

These documents show **old counts** and are marked as historical:
- `TEST-COVERAGE-BEFORE-AFTER.md` - Shows 327 tests, 25 performance (historical)

**For current counts, always check:** `MCP-TEST-EXECUTION-STRATEGY.md`

---

**Last Updated:** 2026-01-27  
**Authority:** `MCP-TEST-EXECUTION-STRATEGY.md` is the ONLY SSOT

