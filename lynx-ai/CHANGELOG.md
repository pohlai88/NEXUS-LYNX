# Changelog — Lynx AI

All notable changes to Lynx AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-01-27

### Added

#### Foundation (Phase 1)
- Core runtime with LLM integration (vendor-agnostic)
- Tenant-scoped session management
- MCP Tool Registry with schema validation and risk classification
- Kernel SSOT integration (metadata, schema, permission readers)
- Audit logging system (Lynx Run tracking, tool call logging)
- Tenant isolation enforcement
- Testing infrastructure (pytest, fixtures, test structure)
- Integration tests for PRD Law gates (31 tests)

#### Domain MCPs (Phase 2)
- 12 Domain MCPs (read-only, advisory tools):
  - `finance.domain.health.read`
  - `kernel.domain.registry.read`
  - `tenant.domain.profile.read`
  - `audit.domain.run.read`
  - `security.domain.permission.read`
  - `workflow.domain.status.read`
  - `workflow.domain.policy.read`
  - `docs.domain.registry.read`
  - `featureflag.domain.status.read`
  - `system.domain.health.read`
  - `vpm.domain.vendor.read`
  - `vpm.domain.payment.status.read`

#### Cluster MCPs (Phase 3)
- Draft Protocol implementation (shared draft model, storage interface)
- 3 Cluster MCPs (draft creation):
  - `docs.cluster.draft.create` - Document draft creation
  - `workflow.cluster.draft.create` - Workflow draft creation
  - `vpm.cluster.payment.draft.create` - Payment draft creation
- Draft immutability guardrail (idempotency preserves draft integrity)

#### Cell MCPs (Phase 4)
- Cell Execution Protocol implementation (execution record model, validation)
- Exactly-once semantics (one successful execution per draft_id per tool_id)
- Draft lifecycle states (PUBLISHED, EXECUTED)
- 3 Cell MCPs (execution):
  - `docs.cell.draft.submit_for_approval` - Submit document draft for approval
  - `workflow.cell.draft.publish` - Publish approved workflow draft
  - `vpm.cell.payment.execute` - Execute approved payment draft (internal-only)
- Settlement Intent object for payment execution (queued settlement, no bank APIs)

#### Documentation
- Tool Index (`docs/MCP/INDEX.md`) - Complete tool catalog
- Runbook (`docs/RUNBOOK/LYNX.md`) - Operations guide
- Decision document (DECISION-LYNX-002) - Cell Execution Protocol

### Protocol Versions

- **LYNX_PROTOCOL_VERSION:** 0.1.0
- **MCP_TOOLSET_VERSION:** 0.1.0

### Test Coverage

- **Total Tests:** 89
- **Passing:** 89/89 (100%)
- **Breakdown:**
  - PRD Law Gates: 31 tests
  - Domain MCP Suite: 14 tests
  - Cluster Draft Suite: 20 tests
  - Cell Execution Suite: 21 tests
  - Persistence Tests: 3 tests

### Architecture

- **Three-Layer MCP Architecture:**
  - Domain (read-only, advisory)
  - Cluster (draft creation, medium risk)
  - Cell (execution, high risk)
- **Governance:**
  - Draft Protocol (non-negotiable invariants)
  - Cell Execution Protocol (non-negotiable invariants)
  - Exactly-once semantics
  - Tenant isolation
  - Full audit trail

### Known Limitations

- **Storage:** In-memory implementation (Supabase integration pending)
- **Settlement:** Internal-only execution (bank integration pending)
- **Approval Workflow:** External approval process (not implemented as MCP tool)

---

## [Unreleased]

### Planned

- Production mode flags and hard stop modes (partially implemented - mode-based approval)
- Observability baseline (`lynx status` command - implemented, `/healthz` endpoint pending)
- Bank settlement integration (separate Cell tool or async worker)

---

## [0.1.1] - 2026-01-27

### Added

#### Supabase Storage Backends (Phase 5.1)
- `DraftStorageSupabase` - Supabase-backed draft storage with idempotency and tenant isolation
- `ExecutionStorageSupabase` - Supabase-backed execution storage with exactly-once semantics
- `SettlementIntentStorageSupabase` - Supabase-backed settlement intent storage
- Model separation (`models.py` files) to break circular dependencies
- Persistence integration tests (3 tests) verifying idempotency and exactly-once survive restarts

### Changed

- Storage interfaces moved to `lynx/storage/` module
- Models separated into `lynx/mcp/cluster/drafts/models.py` and `lynx/mcp/cell/execution/models.py`
- `ExecutionRecord` now includes `source_context` field
- Supabase schema updated to include `source_context` column in `lynx_executions` table

### Test Coverage

- **Total Tests:** 89 (was 86)
- **Passing:** 89/89 (100%)
- **New Tests:** 3 persistence tests

