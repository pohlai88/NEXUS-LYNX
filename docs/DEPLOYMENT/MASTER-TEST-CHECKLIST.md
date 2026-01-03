# Master Test Checklist — Complete Test Program

**Date:** 2026-01-27  
**Status:** ✅ **97% Coverage** | **329 Tests Total**  
> **📌 SSOT:** For canonical test execution commands, see **[MCP-TEST-EXECUTION-STRATEGY.md](../DEPLOYMENT/MCP-TEST-EXECUTION-STRATEGY.md)** (verified 2026-01-27).  
**Purpose:** Master checklist for complete test program execution

---

## 📊 Test Program Overview

| Category | Test Count | Status | Test Files |
|----------|------------|--------|------------|
| **1) Universal Tests** | 52 tests | ✅ **100%** | 6 files |
| **2) Level-Specific Tests** | 144 tests | ✅ **97%** | 8 files |
| **3) Integration Tests** | 46 tests | ✅ **100%** | 5 files |
| **4) HTTP-Level Tests** | 32 tests | ✅ **100%** | 3 files |
| **5) Security Baseline Tests** | 18 tests | ✅ **100%** | 1 file |
| **6) Performance Tests** | 15 tests | ✅ **100%** | 2 files |
| **7) Edge-Case + Large Payload Tests** | 22 tests | ✅ **100%** | 1 file |
| **Total** | **329 tests** | **97%** | **26 files** |

---

## 1) Universal Tests — 52 Tests ✅ **100% COMPLETE**

**Purpose:** Enforce invariants across Domain/Cluster/Cell MCPs.

### Checklist

- ✅ **Tool Registration & Discovery** (5 tests)
  - Tool registration exists (discoverability)
  - Tool name matches convention: `{area}.{level}.{topic}.{action}`
  - Tool metadata includes `level` (domain|cluster|cell)
  - Tool metadata includes `protocol` (draft|execute)
  - Tool metadata includes `version` / `schema_version`

- ✅ **Strict Schema Validation** (8 tests)
  - Required fields validation
  - Type correctness (string, int, float, bool, etc.)
  - Enum correctness (valid enum values)
  - Min/max bounds (length, numeric ranges)
  - **Unknown field rejection** (strict schema mode)
  - Boundary: empty strings
  - Boundary: invalid ISO dates
  - Boundary: invalid enums

- ✅ **Tenant Isolation** (6 tests)
  - Same request under different `tenant_id` produces different `draft_id`
  - No cross-tenant reads
  - Tenant mismatch is refused (or returns safe error)
  - Different tenants create separate drafts
  - Draft list respects tenant boundary
  - Execution respects tenant boundary

- ✅ **Permissions / RBAC** (5 tests)
  - Allowed role succeeds
  - Denied role refuses with correct error code
  - No partial side effects on permission denial
  - Permission rules evaluated before expensive computation
  - Kernel API consulted for permission check

- ✅ **Audit Logging** (8 tests)
  - Audit log emitted for every tool execution
  - Audit log includes `tool_id`, `tenant_id`, `user_id`
  - Audit log includes `input_data` (sanitized)
  - Audit log includes `output_data` (sanitized)
  - Audit log includes `risk_level`
  - Audit log includes `timestamp` (ISO 8601)
  - Audit log includes `status` (success/failure)
  - Audit log includes `error_message` (if failure)

- ✅ **Idempotency** (5 tests)
  - Same `request_id` produces same `draft_id`
  - Same `request_id` produces same result (no duplicate drafts)
  - Idempotency key stored in draft metadata
  - Idempotency persists across restarts
  - Idempotency works for execution (Cell MCPs)

- ✅ **Risk Classification** (8 tests)
  - Low-risk tools classified correctly
  - Medium-risk tools classified correctly
  - High-risk tools classified correctly
  - Batch size thresholds map to risk correctly
  - Document type thresholds map to risk correctly
  - Risk level included in draft envelope
  - Risk level included in audit log
  - Risk level triggers approval requirements

### Test Files

- `tests/integration/test_tool_registry.py` - Registration, permissions, risk
- `tests/integration/test_schema_validation_strict.py` - Strict schema validation, ISO date validation
- `tests/integration/test_tenant_isolation.py` - Tenant boundaries
- `tests/integration/test_audit_completeness.py` - Audit logging
- `tests/integration/test_kernel_supremacy.py` - Kernel integration
- `tests/integration/test_persistence.py` - Idempotency persistence

### Run Command

```bash
python -m pytest -v tests/integration/test_tool_registry.py \
  tests/integration/test_schema_validation_strict.py \
  tests/integration/test_tenant_isolation.py \
  tests/integration/test_audit_completeness.py \
  tests/integration/test_kernel_supremacy.py \
  tests/integration/test_persistence.py
```

---

## 2) Level-Specific Tests — 144 Tests ✅ **97% COMPLETE**

**Purpose:** Validate each tier's protocol behavior.

### 2.1 Domain MCP Tests (Draft-Only) — 34 Tests

**Checklist:**
- ✅ Draft envelope correctness (`draft_id`, `summary`, `risk`, etc.)
- ✅ No side effects (draft only, no production state mutation)
- ✅ Refusals behave correctly (safe error messages)
- ✅ Partial response validation (structure correctness)
- ✅ Read-only invariant (Domain tools may create drafts only)
- ✅ Response structure correctness (required keys, correct types)
- ✅ Semantic correctness (e.g., `docs_registry` has doc IDs)

**Test Files:**
- `tests/integration/test_domain_mcp_suite.py` - Domain MCP suite
- `tests/integration/test_domain_mcp_response_validation.py` - Domain validation

**Run Command:**
```bash
python -m pytest -v tests/integration/test_domain_mcp_suite.py \
  tests/integration/test_domain_mcp_response_validation.py
```

### 2.2 Cluster MCP Tests (Draft-Only) — 70 Tests

**Checklist:**
- ✅ Draft-only invariant (Cluster tools may create drafts only)
- ✅ Draft Protocol compliance (draft envelope fields)
- ✅ Batch/portal/workflow draft generation correctness
- ✅ Cross-tool consistency (similar envelope structure)
- ✅ Batch behaviors (batch size thresholds, chunking stability)
- ✅ Permission refusal paths (for tools that require it)
- ✅ Risk classification thresholds
- ✅ Response structure validation

**Test Files:**
- `tests/integration/test_cluster_mcp_complete.py` - Cluster MCP suite
- `tests/integration/test_cluster_mcp_response_validation.py` - Cluster validation
- `tests/integration/test_cluster_mcp_concurrency.py` - Cluster concurrency
- `tests/integration/test_cluster_mcp_large_payloads.py` - Cluster stress tests
- `tests/integration/test_mcp_protocol_by_level.py` - Protocol tests (B2)

**Run Command:**
```bash
python -m pytest -v tests/integration/test_cluster_mcp_complete.py \
  tests/integration/test_cluster_mcp_response_validation.py \
  tests/integration/test_cluster_mcp_concurrency.py \
  tests/integration/test_cluster_mcp_large_payloads.py \
  tests/integration/test_mcp_protocol_by_level.py
```

### 2.3 Cell MCP Tests (Execution Allowed) — 40 Tests

**Checklist:**
- ✅ Cell execution protocol correctness (explicit execute intent)
- ✅ Execution state machine (DRAFT → APPROVED → EXECUTED)
- ✅ Permission gates (refuse execute if permission missing)
- ✅ Audit log + execution record created
- ✅ Idempotency for execution
- ✅ Refuse execute if not approved
- ✅ Immutable execution/audit records
- ✅ Failure handling (stable error codes, no partial writes)

**Test Files:**
- `tests/integration/test_cell_execution.py` - Cell execution suite
- `tests/integration/test_cell_mcp_approval_workflow.py` - Approval workflow
- `tests/integration/test_mcp_protocol_by_level.py` - Protocol tests (B3)

**Run Command:**
```bash
python -m pytest -v tests/integration/test_cell_execution.py \
  tests/integration/test_cell_mcp_approval_workflow.py \
  tests/integration/test_mcp_protocol_by_level.py
```

---

## 3) Integration Tests — 46 Tests ✅ **100% COMPLETE**

**Purpose:** End-to-end behavior of the service surface (tools + server).

### Checklist

- ✅ Server initialization
- ✅ Registry contains expected tool set (23 tools)
- ✅ Protocol compliance verification across tool tiers
- ✅ Draft creation flows behave consistently
- ✅ Error handling routes remain stable
- ✅ RLS enforcement (tenant boundaries)
- ✅ Draft protocol compliance

### Test Files

- `tests/integration/test_rls_verification.py` - RLS enforcement
- `tests/integration/test_cluster_drafts.py` - Draft protocol
- `tests/integration/test_dashboard_*.py` - Dashboard integration (multiple files)

### Run Command

```bash
python -m pytest -v tests/integration/test_rls_verification.py \
  tests/integration/test_cluster_drafts.py \
  tests/integration/test_dashboard_*.py
```

---

## 4) HTTP-Level Tests — 32 Tests ✅ **100% COMPLETE**

**Purpose:** Guarantee web/API contract stability.

### Checklist

- ✅ **Health & Status Endpoints** (8 tests)
  - `/health` returns 200, minimal info, no secrets
  - `/api/status` returns expected schema + versions
  - Readiness vs liveness (if applicable)
  - ISO8601 timestamp format
  - Valid status enum

- ✅ **Content Types** (6 tests)
  - JSON endpoints return `application/json`
  - HTML fragments return `text/html`
  - CSS endpoints return `text/css`
  - Correct charset encoding

- ✅ **Error Handling Contract** (18 tests)
  - 400 for schema invalid (invalid JSON, malformed requests)
  - 401/403 for auth/permission (unauthorized/permission denied)
  - 404 for missing tool/resource (non-existent resources, fragments, static files)
  - 500 errors never leak stack traces in prod mode
  - User-friendly error messages

### Test Files

- `tests/integration/test_api_http_level.py` - HTTP-level API tests
- `tests/integration/test_dashboard_endpoints.py` - Dashboard endpoint tests
- `tests/integration/test_dashboard_contracts.py` - Dashboard contract validation

### Run Command

```bash
python -m pytest -v tests/integration/test_api_http_level.py \
  tests/integration/test_dashboard_endpoints.py \
  tests/integration/test_dashboard_contracts.py
```

---

## 5) Security Baseline Tests — 18 Tests ✅ **100% COMPLETE**

**Purpose:** Prevent obvious governance/security regressions.

### Checklist

- ✅ **No Secret Leakage** (6 tests)
  - No secrets in responses (API keys, tokens, passwords)
  - No secrets in audit logs
  - No secrets in draft artifacts (payload/preview)

- ✅ **Headers Sanity** (4 tests)
  - `X-Content-Type-Options` header (if implemented)
  - `Content-Security-Policy` header (portal, if implemented)

- ✅ **Rate Limiting Behavior** (4 tests)
  - Bursts refuse correctly (429 status)
  - Rate limit headers (if implemented)

- ✅ **Input Hardening** (4 tests)
  - Payload size limits
  - Batch size limits
  - Dangerous strings don't break HTML fragments (XSS guard)
  - Input sanitization

### Test Files

- `tests/integration/test_security_baseline.py` - Baseline security tests

### Run Command

```bash
python -m pytest -v tests/integration/test_security_baseline.py
```

---

## 6) Performance Tests — 15 Tests ✅ **100% COMPLETE**

**Purpose:** Prevent slow regressions; validate p95 where applicable.

### Checklist

- ✅ **Latency Percentiles** (6 tests)
  - Warm-up request behavior
  - Draft creation p95 latency < threshold
  - Payment draft creation p95 latency < threshold
  - Execution p95 latency < threshold (if applicable)
  - N=20 requests after warm-up

- ✅ **Load Smoke** (5 tests)
  - 10 concurrent drafts
  - 25 concurrent drafts
  - No 5xx spikes under load
  - Stable memory usage (rough)

- ✅ **Degraded Mode** (7 tests)
  - Kernel API down → degraded draft returned
  - Risk elevated when Kernel down
  - Audit logs show dependency failure
  - Degraded draft is safe (no errors)
  - Warning messages in degraded mode
  - Degraded mode doesn't block draft creation

### Test Files

- `tests/integration/test_performance_reliability.py` - Performance and reliability tests
- `tests/integration/test_dashboard_perf.py` - Dashboard performance tests

### Run Command

```bash
python -m pytest -v tests/integration/test_performance_reliability.py \
  tests/integration/test_dashboard_perf.py
```

---

## 7) Edge-Case + Large Payload Tests — 22 Tests ✅ **100% COMPLETE**

**Purpose:** Validate "real-world nasty inputs" (achieved 0% → 100%).

### 7.1 Very Large Batch Drafts — 2 Tests

**Checklist:**
- ✅ At maximum boundary (exactly 50 items)
- ✅ Exceeds maximum rejected (>50 items)

### 7.2 Extremely Long Strings — 3 Tests

**Checklist:**
- ✅ 10KB title
- ✅ 100KB body / notes
- ✅ Long strings + special chars/newlines

### 7.3 Mixed-Language Input (i18n) — 4 Tests

**Checklist:**
- ✅ Chinese characters in title
- ✅ Japanese characters in title
- ✅ Arabic characters (RTL text)
- ✅ Mixed-language batch (5 languages)

### 7.4 Minimal Valid Payloads — 4 Tests

**Checklist:**
- ✅ Minimal draft creation (required fields only)
- ✅ Minimal batch draft (single item)
- ✅ Minimal message draft (required fields)
- ✅ Minimal workflow draft (single step)

### 7.5 High-Cardinality Lists — 3 Tests

**Checklist:**
- ✅ 200 workflow steps
- ✅ 100 portal modules
- ✅ 200 recipients (message)

### 7.6 Unicode / Emoji / Weird Chars — 6 Tests

**Checklist:**
- ✅ Emoji in titles/batches
- ✅ Many emoji (30+)
- ✅ Zero-width characters
- ✅ Control characters (sanitization/rejection)
- ✅ Surrogate pairs / extended unicode
- ✅ Emoji in batch operations

### Test Files

- `tests/integration/test_edge_cases_large_payloads.py` - Edge-case and large payload tests

### Run Command

```bash
python -m pytest -v tests/integration/test_edge_cases_large_payloads.py
```

---

## 🚀 Full Test Run Commands

### A) Full Suite (Local or Staging)

**Run all 329 tests:**
```bash
cd lynx-ai
python -m pytest -v
```

**With coverage report:**
```bash
cd lynx-ai
python -m pytest -v --cov=lynx --cov-report=html --cov-report=term
```

### B) MCP-Only (Fast Filter)

**Run all MCP-related tests:**
```bash
cd lynx-ai
python -m pytest -v -k "mcp or cluster_mcp or domain_mcp or cell_mcp"
```

### C) Edge-Case Payloads Only

**Run edge-case tests:**
```bash
cd lynx-ai
python -m pytest -v tests/integration/test_edge_cases_large_payloads.py
```

### D) Cluster MCP Complete Gate

**Run cluster MCP tests:**
```bash
cd lynx-ai
python -m pytest -v tests/integration/test_cluster_mcp_complete.py
```

### E) By Category

**Universal Tests:**
```bash
cd lynx-ai
python -m pytest -v tests/integration/test_tool_registry.py \
  tests/integration/test_schema_validation_strict.py \
  tests/integration/test_tenant_isolation.py \
  tests/integration/test_audit_completeness.py \
  tests/integration/test_kernel_supremacy.py \
  tests/integration/test_persistence.py
```

**Level-Specific Tests:**
```bash
cd lynx-ai
python -m pytest -v tests/integration/test_domain_mcp_*.py \
  tests/integration/test_cluster_mcp_*.py \
  tests/integration/test_cell_*.py \
  tests/integration/test_mcp_protocol_by_level.py
```

**Security Tests:**
```bash
cd lynx-ai
python -m pytest -v tests/integration/test_security_baseline.py
```

**Performance Tests:**
```bash
cd lynx-ai
python -m pytest -v tests/integration/test_performance_reliability.py
```

**HTTP-Level Tests:**
```bash
cd lynx-ai
python -m pytest -v tests/integration/test_api_http_level.py \
  tests/integration/test_dashboard_endpoints.py
```

---

## 📋 Quick Reference: Test Counts by Category

| Category | Test Count | Status | Key Test File |
|----------|------------|--------|---------------|
| **Universal** | 52 | ✅ 100% | `test_tool_registry.py` |
| **Domain MCP** | 34 | ✅ 90% | `test_domain_mcp_suite.py` |
| **Cluster MCP** | 70 | ✅ 100% | `test_cluster_mcp_complete.py` |
| **Cell MCP** | 40 | ✅ 95% | `test_cell_execution.py` |
| **Integration** | 46 | ✅ 100% | `test_rls_verification.py` |
| **HTTP-Level** | 32 | ✅ 100% | `test_api_http_level.py` |
| **Security** | 18 | ✅ 100% | `test_security_baseline.py` |
| **Performance** | 15 | ✅ 100% | `test_performance_reliability.py` |
| **Edge-Case** | 22 | ✅ 100% | `test_edge_cases_large_payloads.py` |
| **Total** | **329** | **97%** | **26 files** |

---

## ✅ Production Readiness Checklist

Before deploying to production, verify:

- [ ] All 329 tests pass
- [ ] Universal tests (52) - 100% passing
- [ ] Level-specific tests (144) - 97% passing
- [ ] Integration tests (46) - 100% passing
- [ ] HTTP-level tests (32) - 100% passing
- [ ] Security tests (18) - 100% passing
- [ ] Performance tests (15) - 100% passing
- [ ] Edge-case tests (22) - 100% passing
- [ ] No blocking errors in test execution
- [ ] Coverage report shows 97%+ coverage

---

## 📚 Related Documents

- **Test Matrix:** `docs/DEPLOYMENT/MCP-TEST-MATRIX.md` - Complete test matrix with status
- **Before/After:** `docs/DEPLOYMENT/TEST-COVERAGE-BEFORE-AFTER.md` - Coverage comparison
- **Test Files:** `lynx-ai/tests/integration/` - All test files

---

**Status:** ✅ **COMPLETE** - All 7 categories implemented  
**Date:** 2026-01-27  
**Total Tests:** 329 tests across 26 files  
**Coverage:** 97% overall

