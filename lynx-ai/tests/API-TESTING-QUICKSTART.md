# API Testing Quick Start

**Production-grade test harness for dashboard API testing.**

---

## 🚀 Golden Commands

### Local Testing
```bash
TEST_API_URL=http://localhost:8000 uv run pytest tests/integration/test_dashboard_*.py -v
```

### Railway Testing
```bash
TEST_API_URL=https://lynx-ai-production.up.railway.app uv run pytest tests/integration/test_dashboard_*.py -v -m integration
```

### Run Specific Test Suite
```bash
# Endpoints only
uv run pytest tests/integration/test_dashboard_endpoints.py -v

# Contracts only
uv run pytest tests/integration/test_dashboard_contracts.py -v -m contract

# Performance only
uv run pytest tests/integration/test_dashboard_perf.py -v -m performance

# Resilience only
uv run pytest tests/integration/test_dashboard_resilience.py -v -m integration
```

---

## 📋 Test Structure

### Test Files

| File | Purpose | Markers |
|------|---------|---------|
| `test_dashboard_endpoints.py` | Status codes, content types, headers | - |
| `test_dashboard_contracts.py` | JSON schema validation, required fields | `@pytest.mark.contract` |
| `test_dashboard_fragments.py` | HTML parsing, structure validation | - |
| `test_dashboard_resilience.py` | Degradation mode, error handling | `@pytest.mark.integration` |
| `test_dashboard_perf.py` | Response times (p95), concurrency | `@pytest.mark.performance` |

### Utility Modules

| Module | Purpose |
|--------|---------|
| `tests/utils/http_assertions.py` | HTTP response assertions (status, content-type, headers) |
| `tests/utils/json_contracts.py` | JSON contract validation (types, enums, required fields) |
| `tests/utils/html_selectors.py` | HTML parsing with stable selectors (data-testid) |

---

## 🎯 Key Features

### 1. Environment-Driven (One Suite, Two Targets)
- Single test suite works for localhost and Railway
- Set `TEST_API_URL` environment variable
- No duplicate test files

### 2. Contract Validation
- Strict JSON schema validation
- Type checking for all fields
- Enumeration validation
- ISO8601 timestamp validation

### 3. Resilient Fragment Tests
- Uses `data-testid` attributes (when implemented)
- Falls back to CSS classes for backward compatibility
- Avoids brittle assertions

### 4. Degradation Mode Testing
- Tests user-facing behavior when services are down
- Ensures dashboard returns 200 with degraded indicators
- Validates error message format

### 5. Performance Testing
- Percentile-based (p95) to avoid cold start issues
- Warm-up request + N=20 requests
- Concurrent request handling

---

## 📊 Test Coverage

### Endpoints Covered
- ✅ `GET /` - Main dashboard
- ✅ `GET /dashboard` - Dashboard alias
- ✅ `GET /health` - Health check
- ✅ `GET /api/status` - Status API
- ✅ `GET /dashboard/_kpis` - KPI fragment
- ✅ `GET /dashboard/_services` - Services fragment
- ✅ `GET /dashboard/_recent` - Recent activity fragment
- ✅ `GET /dashboard/_cockpit` - Cockpit fragment
- ✅ `GET /static/aibos-design-system.css` - CSS file

### Test Categories
- ✅ Status codes and content types
- ✅ JSON contract validation
- ✅ HTML structure validation
- ✅ Error handling and degradation
- ✅ Performance (p95 response times)
- ✅ Concurrency handling
- ✅ Security (no secrets in responses)

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TEST_API_URL` | `http://localhost:8000` | Base URL for API testing |

### Pytest Markers

| Marker | Description |
|--------|-------------|
| `@pytest.mark.integration` | Integration tests (Railway, external services) |
| `@pytest.mark.performance` | Performance tests (may be slower) |
| `@pytest.mark.contract` | Contract validation tests |

### Running with Markers

```bash
# Skip integration tests (faster local runs)
uv run pytest -m "not integration" -v

# Run only contract tests
uv run pytest -m contract -v

# Run only performance tests
uv run pytest -m performance -v
```

---

## 📈 Performance Requirements

| Endpoint | Requirement | Test |
|----------|-------------|------|
| Dashboard (`/`) | p95 < 350ms | ✅ `test_dashboard_response_time_p95` |
| Fragments | p95 < 200ms | ✅ `test_fragment_response_time_p95` |
| Health (`/health`) | p95 < 100ms | ✅ `test_health_endpoint_response_time` |
| Status (`/api/status`) | p95 < 350ms | ✅ `test_api_status_response_time` |

---

## 🛡️ Security Checks

- ✅ No secrets in JSON responses
- ✅ No API keys in error messages
- ✅ No environment variable dumps
- ✅ Content-type headers validated

---

## 🐛 Debugging

### Verbose Output
```bash
uv run pytest tests/integration/test_dashboard_*.py -vv
```

### Show Test Names
```bash
uv run pytest tests/integration/test_dashboard_*.py --collect-only
```

### Run Single Test
```bash
uv run pytest tests/integration/test_dashboard_endpoints.py::TestDashboardEndpoints::test_dashboard_home_returns_200 -v
```

### Show Performance Details
```bash
uv run pytest tests/integration/test_dashboard_perf.py -v --durations=10
```

---

## 📝 Next Steps

### To Add data-testid Attributes (Recommended)

Add `data-testid` attributes to dashboard HTML for more stable tests:

```html
<!-- In dashboard.py -->
<div class="na-card" data-testid="kpi-card">
<div class="na-grid-kpis" data-testid="kpi-grid">
<div id="fragment-kpis" data-fragment="kpis">
```

This makes tests more resilient to CSS refactors.

---

## ✅ Success Criteria

- [x] Environment-driven (one suite, two targets)
- [x] Contract validation (strict JSON schema)
- [x] Resilient fragment tests (data-testid support)
- [x] Degradation mode testing
- [x] Performance testing (p95 percentiles)
- [x] Concurrency testing
- [x] Security checks
- [x] DRY structure (shared utilities)

---

**Status:** ✅ **PRODUCTION-READY** - Ready to run!

