# Test Execution Strategy — PR Gate & CI Configuration

**Date:** 2026-01-27  
**Status:** ✅ **CONFIGURED**  
**Purpose:** Define test execution strategy for PR gates, CI, and local development

> **📌 SSOT:** For canonical test execution commands and verified counts, see **[MCP-TEST-EXECUTION-STRATEGY.md](MCP-TEST-EXECUTION-STRATEGY.md)** (verified 2026-01-27: 329 tests total, 292 PR gate, 15 performance, 22 stress).

---

## 🎯 Test Execution Tiers

| Tier | Purpose | Command | Test Count | Duration |
|------|---------|---------|------------|----------|
| **PR Gate** | Fast, must-pass on every PR | `-m "not performance and not stress"` | 292 tests | ~2-3 min |
| **Full Suite** | Complete validation (staging/prod) | `pytest -v` | 329 tests | ~5-8 min |
| **Performance** | Performance regression checks | `-m performance` | 15 tests | ~2-3 min |
| **Stress** | Edge-case and large payloads | `-m stress` | 22 tests | ~1-2 min |

---

## 1) PR Gate (Fast, Must-Pass)

**Runs on:** Every PR  
**Requirement:** No flakes, no perf, no stress  
**Goal:** Fast feedback on core functionality

### Command

```bash
cd lynx-ai
python -m pytest -v -m "not performance and not stress"
```

### What It Covers

✅ **Universal Invariants** (52 tests)
- Tool registration & discovery
- Strict schema validation
- Tenant isolation
- Permissions / RBAC
- Audit logging
- Idempotency
- Risk classification

✅ **Domain/Cluster/Cell Protocol Compliance** (144 tests)
- Domain MCP tests (draft-only)
- Cluster MCP tests (draft-only)
- Cell MCP tests (execution allowed)
- Protocol-level validation

✅ **Core Integration Behavior** (46 tests)
- Server initialization
- Registry tool set validation
- Draft creation flows
- Error handling stability
- RLS enforcement

✅ **Security Baseline (Non-Stress)** (18 tests)
- No secret leakage
- Headers sanity
- Input hardening (non-stress)
- Permission denial paths

✅ **HTTP-Level Contract** (32 tests)
- Health & status endpoints
- Content types
- Error handling contract

### Excluded from PR Gate

❌ **Performance Tests** (15 tests) - Run separately in CI
- Latency percentile tests
- Load smoke tests
- Degraded mode tests

❌ **Stress Tests** (22 tests) - Run separately in CI
- Very large batch drafts
- Extremely long strings (10KB+, 100KB+)
- High-cardinality lists (200+ items)
- Edge-case payloads

### Expected Results

- **Test Count:** 292 tests
- **Duration:** ~2-3 minutes
- **Pass Rate:** 100% (no flakes allowed)
- **Purpose:** Fast feedback on core functionality

---

## 2) Full Suite (Complete Validation)

**Runs on:** Staging deployments, pre-production  
**Requirement:** All tests pass  
**Goal:** Complete validation before production

### Command

```bash
cd lynx-ai
python -m pytest -v
```

### What It Covers

✅ **All 329 Tests**
- Universal tests (52)
- Level-specific tests (144)
- Integration tests (46)
- HTTP-level tests (32)
- Security tests (18)
- Performance tests (15)
- Edge-case tests (22)

### Expected Results

- **Test Count:** 329 tests
- **Duration:** ~5-8 minutes
- **Pass Rate:** 97%+ (all critical tests pass)
- **Purpose:** Complete validation before production

---

## 3) Performance Tests (Separate CI Job)

**Runs on:** Scheduled CI, pre-production  
**Requirement:** Performance thresholds met  
**Goal:** Prevent performance regressions

### Command

```bash
cd lynx-ai
python -m pytest -v -m performance
```

### What It Covers

✅ **Performance Tests** (15 tests)
- Latency percentiles (p95 thresholds)
- Load smoke (10-25 concurrent requests)
- Degraded mode (Kernel API down scenarios)
- Memory usage stability

### Expected Results

- **Test Count:** 15 tests
- **Duration:** ~2-3 minutes
- **Pass Rate:** 100% (all thresholds met)
- **Purpose:** Performance regression detection

---

## 4) Stress Tests (Separate CI Job)

**Runs on:** Scheduled CI, pre-production  
**Requirement:** Edge-cases handled correctly  
**Goal:** Validate extreme payload handling

### Command

```bash
cd lynx-ai
python -m pytest -v -m stress
```

### What It Covers

✅ **Edge-Case Tests** (22 tests)
- Very large batch drafts (boundary conditions)
- Extremely long strings (10KB+, 100KB+)
- Mixed-language input (i18n)
- High-cardinality lists (200+ items)
- Unicode/emoji handling

### Expected Results

- **Test Count:** 22 tests
- **Duration:** ~1-2 minutes
- **Pass Rate:** 100% (all edge-cases handled)
- **Purpose:** Extreme payload validation

---

## 📋 Test Markers Configuration

### Current Markers (pytest.ini)

```ini
markers =
    integration: marks tests as integration tests
    performance: marks tests as performance tests
    contract: marks tests as contract validation tests
    stress: marks tests as stress/edge-case tests
```

### Marker Usage

| Marker | Purpose | Test Files |
|--------|---------|------------|
| `@pytest.mark.performance` | Performance tests | `test_performance_reliability.py`, `test_dashboard_perf.py` |
| `@pytest.mark.stress` | Stress/edge-case tests | `test_edge_cases_large_payloads.py` |
| `@pytest.mark.integration` | Integration tests | Various integration test files |
| `@pytest.mark.contract` | Contract validation | `test_dashboard_contracts.py` |

---

## 🔧 CI/CD Configuration

### GitHub Actions Example

```yaml
name: Test Suite

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

jobs:
  pr-gate:
    name: PR Gate (Fast)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - run: pip install -r requirements.txt
      - run: |
          cd lynx-ai
          python -m pytest -v -m "not performance and not stress"
    
  performance:
    name: Performance Tests
    runs-on: ubuntu-latest
    if: github.event_name == 'push' || github.event.pull_request.head.repo.full_name == github.repository
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - run: pip install -r requirements.txt
      - run: |
          cd lynx-ai
          python -m pytest -v -m performance
    
  stress:
    name: Stress Tests
    runs-on: ubuntu-latest
    if: github.event_name == 'push' || github.event.pull_request.head.repo.full_name == github.repository
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - run: pip install -r requirements.txt
      - run: |
          cd lynx-ai
          python -m pytest -v -m stress
```

---

## 🚀 Local Development Commands

### Quick Test (PR Gate Equivalent)

```bash
cd lynx-ai
python -m pytest -v -m "not performance and not stress"
```

### Full Test Suite

```bash
cd lynx-ai
python -m pytest -v
```

### Run Specific Category

```bash
# Universal tests only
python -m pytest -v tests/integration/test_tool_registry.py \
  tests/integration/test_schema_validation_strict.py \
  tests/integration/test_tenant_isolation.py

# Performance tests only
python -m pytest -v -m performance

# Stress tests only
python -m pytest -v -m stress

# MCP tests only
python -m pytest -v -k "mcp or cluster_mcp or domain_mcp or cell_mcp"
```

### Run with Coverage

```bash
cd lynx-ai
python -m pytest -v --cov=lynx --cov-report=html --cov-report=term
```

---

## 📊 Test Distribution by Marker

| Marker | Test Count | Test Files | Purpose |
|--------|------------|------------|---------|
| **No marker** | 292 tests | Most test files | Core functionality (PR gate) |
| **`@pytest.mark.performance`** | 15 tests | `test_performance_reliability.py`, `test_dashboard_perf.py` | Performance validation |
| **`@pytest.mark.stress`** | 22 tests | `test_edge_cases_large_payloads.py` | Edge-case validation |
| **`@pytest.mark.integration`** | ~46 tests | Various integration files | Integration scenarios |
| **`@pytest.mark.contract`** | ~32 tests | `test_dashboard_contracts.py` | Contract validation |

---

## ✅ PR Gate Checklist

Before merging a PR, verify:

- [ ] PR gate tests pass (`-m "not performance and not stress"`)
- [ ] No flaky tests
- [ ] All core functionality tests pass
- [ ] Security baseline tests pass
- [ ] HTTP-level contract tests pass
- [ ] Integration tests pass

**Optional (run separately):**
- [ ] Performance tests pass (if performance-related changes)
- [ ] Stress tests pass (if payload-related changes)

---

## 🎯 Test Execution Summary

| Scenario | Command | Test Count | When to Run |
|----------|---------|------------|-------------|
| **PR Gate** | `pytest -v -m "not performance and not stress"` | 292 | Every PR |
| **Full Suite** | `pytest -v` | 329 | Pre-production |
| **Performance** | `pytest -v -m performance` | 15 | Scheduled CI |
| **Stress** | `pytest -v -m stress` | 22 | Scheduled CI |
| **MCP Only** | `pytest -v -k "mcp"` | ~144 | MCP changes |

---

## 📚 Related Documents

- **Master Checklist:** `docs/DEPLOYMENT/MASTER-TEST-CHECKLIST.md` - Complete test checklist
- **Test Matrix:** `docs/DEPLOYMENT/MCP-TEST-MATRIX.md` - Test matrix with status
- **Before/After:** `docs/DEPLOYMENT/TEST-COVERAGE-BEFORE-AFTER.md` - Coverage comparison

---

**Status:** ✅ **CONFIGURED** - Ready for CI/CD integration  
**Date:** 2026-01-27  
**PR Gate:** 292 tests, ~2-3 minutes  
**Full Suite:** 329 tests, ~5-8 minutes

