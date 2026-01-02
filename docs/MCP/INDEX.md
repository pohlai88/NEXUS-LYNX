# MCP Tool Index — Lynx AI

**Protocol Version:** 0.1.0  
**Toolset Version:** 0.1.0  
**Last Updated:** 2026-01-27

---

## Overview

Lynx AI implements a three-layer MCP architecture:
- **Domain MCPs** (Layer 1): Read-only, advisory tools
- **Cluster MCPs** (Layer 2): Draft creation, medium risk
- **Cell MCPs** (Layer 3): Execution, high risk

**Total Tools:** 18

---

## Domain MCPs (12 tools)

**Layer:** Domain  
**Risk:** Low  
**Requirement:** Read-only, no state changes

### Finance Domain

1. **`finance.domain.health.read`**
   - **Purpose:** Financial health summary
   - **Risk:** Low
   - **Input:** Optional filters
   - **Output:** Financial health metrics

### Kernel Domain

2. **`kernel.domain.registry.read`**
   - **Purpose:** Read available Kernel tool definitions and policies
   - **Risk:** Low
   - **Input:** `include_policies`, `include_versions`
   - **Output:** Tool definitions, policy references, version hash

### Tenant Domain

3. **`tenant.domain.profile.read`**
   - **Purpose:** Tenant profile summary
   - **Risk:** Low
   - **Input:** None (tenant inferred from context)
   - **Output:** Tenant profile, enabled modules, user role/scope

### Audit Domain

4. **`audit.domain.run.read`**
   - **Purpose:** Read audit run history
   - **Risk:** Low
   - **Input:** Optional filters (`limit`, `since`, `status`)
   - **Output:** Last N Lynx runs with outcomes

### Security Domain

5. **`security.domain.permission.read`**
   - **Purpose:** Explain permission denials
   - **Risk:** Low
   - **Input:** `action`, `resource`
   - **Output:** Permission explanation, required vs current scopes

### Workflow Domain

6. **`workflow.domain.status.read`**
   - **Purpose:** Workflow state snapshot
   - **Risk:** Low
   - **Input:** Optional filters
   - **Output:** Active workflows count, pending approvals, last N events

7. **`workflow.domain.policy.read`**
   - **Purpose:** Read workflow approval rules and thresholds
   - **Risk:** Low
   - **Input:** Optional filters
   - **Output:** Approval rules, role gates, thresholds

### Docs Domain

8. **`docs.domain.registry.read`**
   - **Purpose:** Read available document packs (PRD/SRS/ADR/Decision Records)
   - **Risk:** Low
   - **Input:** Optional filters
   - **Output:** Document registry, versions, checksums

### Feature Flag Domain

9. **`featureflag.domain.status.read`**
   - **Purpose:** Read enabled modules/tools/features per tenant
   - **Risk:** Low
   - **Input:** None (tenant inferred from context)
   - **Output:** Feature flag status per module

### System Domain

10. **`system.domain.health.read`**
    - **Purpose:** System health status (Kernel, Supabase, queues)
    - **Risk:** Low
    - **Input:** None
    - **Output:** System health metrics, connectivity status

### VPM Domain

11. **`vpm.domain.vendor.read`**
    - **Purpose:** Vendor profile summary, risk flags, status
    - **Risk:** Low
    - **Input:** `vendor_id`
    - **Output:** Vendor snapshot, risk flags, payment terms

12. **`vpm.domain.payment.status.read`**
    - **Purpose:** Payment lifecycle snapshot
    - **Risk:** Low
    - **Input:** Optional filters (`vendor_id`, `status`, `since`)
    - **Output:** Payment status, pending approvals, failed payments

---

## Cluster MCPs (3 tools)

**Layer:** Cluster  
**Risk:** Medium  
**Requirement:** Draft creation only, no production mutation

### Docs Cluster

1. **`docs.cluster.draft.create`**
   - **Purpose:** Create document draft (PRD/SRS/ADR/DECISION)
   - **Risk:** Medium
   - **Input:** `doc_type`, `title`, `content_outline`, `source_refs`, `request_id`
   - **Output:** `draft_id`, `status`, `preview_markdown`, `next_actions`
   - **Draft Protocol:** ✅
   - **Approval Required:** No (draft creation)

### Workflow Cluster

2. **`workflow.cluster.draft.create`**
   - **Purpose:** Create workflow draft with steps, approvers, gates
   - **Risk:** Medium
   - **Input:** `workflow_kind`, `name`, `steps`, `linked_object`, `request_id`
   - **Output:** `draft_id`, `status`, `preview_markdown`, `risk_level`, `recommended_approvers`
   - **Draft Protocol:** ✅
   - **Domain Reads:** `workflow.domain.policy.read`, `security.domain.permission.read`, `featureflag.domain.status.read`
   - **Approval Required:** No (draft creation)

### VPM Cluster

3. **`vpm.cluster.payment.draft.create`**
   - **Purpose:** Create payment draft with vendor snapshot and execution readiness
   - **Risk:** Medium
   - **Input:** `vendor_id`, `amount`, `currency`, `due_date`, `invoice_refs`, `request_id`
   - **Output:** `draft_id`, `status`, `preview_markdown`, `vendor_snapshot`, `execution_readiness`, `risk_level`
   - **Draft Protocol:** ✅
   - **Domain Reads:** `vpm.domain.vendor.read`, `workflow.domain.policy.read`, `security.domain.permission.read`, `featureflag.domain.status.read`
   - **Approval Required:** No (draft creation)

---

## Cell MCPs (3 tools)

**Layer:** Cell  
**Risk:** Low to High  
**Requirement:** Execution from approved drafts only

### Docs Cell

1. **`docs.cell.draft.submit_for_approval`**
   - **Purpose:** Submit document draft for approval
   - **Risk:** Low (changes draft state only)
   - **Input:** `draft_id`
   - **Output:** `execution_id`, `draft_id`, `status`, `tenant_id`
   - **Execution Protocol:** ✅
   - **Draft Requirement:** DRAFT status (not CANCELLED)
   - **Approval Required:** No (low risk, draft state change only)

### Workflow Cell

2. **`workflow.cell.draft.publish`**
   - **Purpose:** Publish approved workflow draft as production workflow
   - **Risk:** Medium (creates production workflow record)
   - **Input:** `draft_id`
   - **Output:** `execution_id`, `draft_id`, `workflow_id`, `status`, `tenant_id`
   - **Execution Protocol:** ✅
   - **Draft Requirement:** APPROVED status
   - **Approval Required:** No (medium risk, approved draft is sufficient)

### VPM Cell

3. **`vpm.cell.payment.execute`**
   - **Purpose:** Execute approved payment draft (internal-only)
   - **Risk:** High (creates production payment record)
   - **Input:** `draft_id`
   - **Output:** `execution_id`, `draft_id`, `payment_id`, `status`, `settlement_intent`, `tenant_id`
   - **Execution Protocol:** ✅
   - **Draft Requirement:** APPROVED status
   - **Vendor Validation:** Active vendor required
   - **Policy Validation:** Thresholds and gates must pass
   - **Approval Required:** Yes (high risk - requires `explicit_approval=True` in production)
   - **Settlement:** Internal-only execution, creates `SettlementIntent` with `status=queued`, `provider=none`

---

## Risk Classification

| Risk Level | Description | Approval Requirement |
|------------|-------------|---------------------|
| **Low** | Read-only or draft state changes | None |
| **Medium** | Draft creation or production record creation | Approved draft |
| **High** | Production state changes with financial impact | Approved draft + explicit approval (prod only) |

---

## Draft Lifecycle

```
DRAFT → SUBMITTED → APPROVED → PUBLISHED/EXECUTED
  ↓         ↓          ↓
CANCELLED  REJECTED   (execution states)
```

**Status Definitions:**
- `DRAFT`: Initial draft state
- `SUBMITTED`: Draft submitted for approval
- `APPROVED`: Draft approved, ready for execution
- `REJECTED`: Draft rejected
- `CANCELLED`: Draft cancelled
- `PUBLISHED`: Workflow draft published (execution complete)
- `EXECUTED`: Payment/docs draft executed (execution complete)

---

## Execution Lifecycle

```
STARTED → SUCCEEDED/FAILED/DENIED
```

**Exactly-Once Semantics:**
- One successful execution per `draft_id` per `tool_id`
- Same `request_id` returns same `execution_id` (idempotency)
- Draft status `PUBLISHED`/`EXECUTED` prevents re-execution

---

## References

- **PRD:** PRD-LYNX-003 (HYBRID BASIC)
- **Decision:** DECISION-LYNX-002 (Cell Execution Protocol)
- **Draft Protocol:** `lynx/mcp/cluster/drafts/base.py`
- **Execution Protocol:** `lynx/mcp/cell/execution/base.py`

