<!-- BEGIN: AIBOS_MANAGED -->
| Field | Value |
|---|---|
| **Document ID** | SRS-LYNX-001 |
| **Document Type** | SRS |
| **Classification** | STANDARD |
| **Title** | Software Requirements Specification — LYNX AI |
| **Status** | DRAFT |
| **Authority** | DERIVED |
| **Scope** | MULTI_TENANT_PRODUCTION_MVP |
| **Derived From** | `PRD-LYNX-001`, `PRD-LYNX-003` |
| **Version** | 1.0.0 |
| **Owners** | `Chief Architect`, `Lead Engineer`, `QA Lead` |
| **Created** | 2026-01-01 |
| **Updated** | 2026-01-01 |

<!-- END: AIBOS_MANAGED -->

# Software Requirements Specification — LYNX AI

**Derived from:** PRD-LYNX-001 (Master PRD), PRD-LYNX-003 (HYBRID BASIC Implementation Strategy)  
**Timeline:** 6-8 weeks  
**Status:** DRAFT

---

## 1. Introduction

### 1.1 Purpose

This Software Requirements Specification (SRS) defines the **functional and non-functional requirements** for Lynx AI implementation, derived from the Master PRD (PRD-LYNX-001) and the approved implementation strategy (PRD-LYNX-003).

### 1.2 Scope

This SRS covers:
- Functional requirements for Lynx AI core system
- MCP tool requirements (Domain, Cluster, Cell layers)
- Integration requirements (Kernel SSOT, Tenant Isolation, Audit)
- Non-functional requirements (Performance, Security, Compliance)
- User interface requirements
- API requirements

**Out of Scope:**
- LLM model selection (vendor-agnostic)
- Kernel API implementation details
- Frontend UI framework selection

### 1.3 Document Relationships

| Document | Relationship |
|----------|-------------|
| **PRD-LYNX-001** | Master PRD (SSOT) - Defines *what* Lynx is |
| **PRD-LYNX-003** | Implementation Strategy - Defines *how* to build |
| **ADR-LYNX-001** | Architecture Decisions - Defines *why* we build this way |
| **TSD-LYNX-001** | Technical Specification - Defines *how* to implement |
| **SOP-LYNX-001** | Standard Operating Procedures - Defines *how* to operate |
| **IMPLEMENTATION-LYNX-001** | Implementation Plan - Defines *when* and *who* |

---

## 2. System Overview

### 2.1 System Purpose

Lynx AI is a **tenant-aware, permission-governed AI assistant** embedded within AI-BOS NexusCanon that:
- Provides advisory guidance to users
- Creates drafts for user review
- Executes approved actions through MCP tools
- Enforces Kernel SSOT and tenant isolation
- Maintains complete audit trails

### 2.2 System Context

```
┌─────────────────┐
│   User (UI)     │
└────────┬────────┘
         │
┌────────▼────────┐
│   Lynx AI       │  ← This System
│   (mcp-agent)   │
└────────┬────────┘
         │ MCP Tools
┌────────▼────────┐
│  Kernel SSOT    │  ← External System
│  (Metadata API) │
└────────┬────────┘
         │
┌────────▼────────┐
│  Supabase DB    │  ← External System
└─────────────────┘
```

### 2.3 Key Constraints

1. **PRD Laws (Non-Negotiable):**
   - Law 1: Kernel Supremacy
   - Law 2: Tenant Absolutism
   - Law 3: Tool-Only Action
   - Law 4: Suggest First, Execute with Consent
   - Law 5: Audit Is Reality

2. **Technical Constraints:**
   - Python-based (mcp-agent foundation)
   - Must integrate with existing Kernel APIs
   - Must support multi-tenant architecture
   - Must maintain audit compliance

---

## 3. Functional Requirements

### 3.1 Core Runtime Requirements

#### FR-001: Authentication Integration
**Priority:** HIGH  
**Source:** PRD-LYNX-001, Law 1

**Requirement:**
- Lynx MUST require user authentication before any operation
- Lynx MUST integrate with NexusCanon authentication system
- Lynx MUST reject unauthenticated requests

**Acceptance Criteria:**
- ✅ Unauthenticated user cannot access Lynx
- ✅ Authenticated user session is validated on every request
- ✅ Session timeout follows NexusCanon policy

---

#### FR-002: Tenant Isolation
**Priority:** HIGH  
**Source:** PRD-LYNX-001, Law 2

**Requirement:**
- Lynx MUST enforce strict tenant scoping
- Lynx MUST NOT allow cross-tenant data access
- Lynx MUST scope all MCP tool calls to user's tenant

**Acceptance Criteria:**
- ✅ User from Tenant A cannot see Tenant B data
- ✅ All MCP tool calls include tenantId
- ✅ Kernel APIs enforce tenant isolation
- ✅ No shared memory between tenants

---

#### FR-003: Kernel SSOT Integration
**Priority:** HIGH  
**Source:** PRD-LYNX-001, Law 1

**Requirement:**
- Lynx MUST read metadata from Kernel SSOT
- Lynx MUST read schema from Kernel SSOT
- Lynx MUST read permissions from Kernel SSOT
- Lynx MUST read lifecycle rules from Kernel SSOT
- Lynx MUST NOT invent or assume truth

**Acceptance Criteria:**
- ✅ Lynx reads metadata via Kernel API
- ✅ Lynx uses Kernel schema for validation
- ✅ Lynx checks permissions via Kernel API
- ✅ Lynx respects Kernel lifecycle rules

---

#### FR-004: MCP Tool Registry
**Priority:** HIGH  
**Source:** PRD-LYNX-001, Law 3; ADR-LYNX-001

**Requirement:**
- Lynx MUST maintain a registry of all available MCP tools
- Each MCP tool MUST have:
  - Unique ID (e.g., `document.cluster.request.draft`)
  - Layer classification (domain/cluster/cell)
  - Risk classification (low/medium/high)
  - Input schema (Zod)
  - Output schema (Zod)
  - Permission requirements
  - Handler function
- Lynx MUST NOT execute actions not in the registry

**Acceptance Criteria:**
- ✅ Tool registry initialized on startup
- ✅ All tools have required metadata
- ✅ Attempt to use unregistered tool fails gracefully
- ✅ Tool discovery API available

---

#### FR-005: Audit Logging
**Priority:** HIGH  
**Source:** PRD-LYNX-001, Law 5

**Requirement:**
- Lynx MUST log every user interaction (Lynx Run)
- Lynx MUST log every MCP tool call
- Lynx MUST log every draft creation
- Lynx MUST log every execution
- Lynx MUST log every refusal/block
- If an action is not logged, it is considered **not happened**

**Acceptance Criteria:**
- ✅ Every interaction creates a Lynx Run record
- ✅ Every tool call creates an audit log entry
- ✅ Audit logs include: userId, tenantId, timestamp, toolId, input, output
- ✅ Audit logs are immutable
- ✅ Audit logs are queryable

---

### 3.2 MCP Tool Requirements

#### FR-010: Domain MCP Tools (Read-Only)
**Priority:** HIGH  
**Source:** PRD-LYNX-003, Phase 2

**Requirement:**
- Lynx MUST implement 10-12 Domain MCP tools
- All Domain MCPs MUST be read-only (no side effects)
- All Domain MCPs MUST be classified as "Low" risk
- All Domain MCPs MUST be tenant-scoped

**Required Domain MCPs:**
1. `finance.domain.health.read` - Financial health summary
2. `finance.domain.payment.gaps.read` - Missing payment records
3. `finance.domain.audit.risk.read` - Audit risk assessment
4. `vendor.domain.summary.read` - Vendor overview
5. `vendor.domain.documents.status.read` - Document compliance status
6. `vendor.domain.performance.read` - Vendor performance metrics
7. `workflow.domain.inefficiency.scan` - Detect inefficient workflows
8. `workflow.domain.usage.analyze` - Workflow usage patterns
9. `compliance.domain.risk.explain` - Explain compliance risks
10. `design.domain.tokens.read` - Read design tokens
11. `design.domain.brand.read` - Read brand guidelines

**Acceptance Criteria:**
- ✅ All 10-12 Domain MCPs implemented
- ✅ All are read-only (no mutations)
- ✅ All return tenant-scoped data
- ✅ All are classified as "Low" risk
- ✅ All have Zod input/output schemas

---

#### FR-011: Cluster MCP Tools (Draft Creation)
**Priority:** HIGH  
**Source:** PRD-LYNX-003, Phase 3

**Requirement:**
- Lynx MUST implement 8-10 Cluster MCP tools
- All Cluster MCPs MUST create drafts (not execute)
- All Cluster MCPs MUST be classified as "Medium" risk
- All Cluster MCPs MUST require role-based approval

**Required Cluster MCPs:**
1. `document.cluster.request.draft` - Create document request drafts
2. `document.cluster.batch.draft` - Create batch document requests
3. `workflow.cluster.approval.draft` - Draft approval workflows
4. `workflow.cluster.digital.draft` - Draft digital workflow proposals
5. `portal.cluster.scaffold.draft` - Draft portal structure
6. `portal.cluster.config.draft` - Draft portal configuration
7. `vpm.cluster.payment.draft` - Draft payment records
8. `policy.cluster.revision.draft` - Draft policy revisions

**Acceptance Criteria:**
- ✅ All 8-10 Cluster MCPs implemented
- ✅ All create drafts (not execute)
- ✅ All require role-based approval
- ✅ All are classified as "Medium" risk
- ✅ Drafts are stored and reviewable

---

#### FR-012: Cell MCP Tools (Execution)
**Priority:** MEDIUM  
**Source:** PRD-LYNX-003, Phase 4

**Requirement:**
- Lynx MUST implement 3-5 Cell MCP tools (limited for HYBRID BASIC)
- All Cell MCPs MUST execute system mutations
- All Cell MCPs MUST be classified as "High" risk
- All Cell MCPs MUST require explicit approval (human-in-the-loop)

**Required Cell MCPs:**
1. `document.cell.request.publish` - Publish document requests
2. `workflow.cell.publish` - Publish workflows
3. `vpm.cell.payment.record` - Record payments

**Acceptance Criteria:**
- ✅ All 3-5 Cell MCPs implemented
- ✅ All require explicit approval before execution
- ✅ All are classified as "High" risk
- ✅ All executions are logged
- ✅ All use soft-delete (no hard deletes)

---

### 3.3 Risk Classification Requirements

#### FR-020: Risk-Based Execution
**Priority:** HIGH  
**Source:** PRD-LYNX-001, Section 20-21

**Requirement:**
- Lynx MUST classify all MCP tools by risk level (Low/Medium/High)
- Lynx MUST enforce execution rules based on risk:
  - **Low:** Immediate execution
  - **Medium:** Role + Scope required
  - **High:** Explicit approval required
- Lynx MUST NOT self-approve high-risk actions

**Acceptance Criteria:**
- ✅ Risk classification is immutable per tool
- ✅ Low-risk tools execute immediately
- ✅ Medium-risk tools check role/scope
- ✅ High-risk tools require explicit approval
- ✅ Approval gates are enforced by Kernel, not Lynx

---

### 3.4 Cognitive vs Operational Boundary Requirements

#### FR-030: Cognitive Freedom
**Priority:** HIGH  
**Source:** PRD-LYNX-001, Section 19.2

**Requirement:**
- Lynx MUST allow unrestricted reasoning
- Lynx MUST understand ambiguous intent
- Lynx MUST reason across domains
- Lynx MUST explain system concepts
- Lynx MUST detect inefficiencies
- Lynx MUST propose alternatives
- Lynx MUST generate drafts, plans, explanations

**Acceptance Criteria:**
- ✅ LLM reasoning is not artificially restricted
- ✅ Lynx can understand vague user queries
- ✅ Lynx can reason about finance, workflow, compliance, etc.
- ✅ Lynx can explain why something should be done differently

---

#### FR-031: Operational Constraint
**Priority:** HIGH  
**Source:** PRD-LYNX-001, Section 19.3

**Requirement:**
- Lynx MUST NOT mutate system state directly
- Lynx MUST NOT access databases freely
- Lynx MUST NOT execute arbitrary logic
- Lynx MUST NOT bypass Kernel governance
- Lynx MUST NOT exceed tenant/user permissions
- Lynx MUST NOT perform unlogged actions
- All actions MUST go through MCP tools

**Acceptance Criteria:**
- ✅ No direct database access
- ✅ No direct API calls (except through MCP)
- ✅ All actions go through MCP tool registry
- ✅ Permission checks enforced on every tool call

---

### 3.5 Failure & Refusal Requirements

#### FR-040: Graceful Failure Handling
**Priority:** HIGH  
**Source:** PRD-LYNX-001, Section 22

**Requirement:**
- If Lynx cannot act due to constraint, it MUST:
  1. Explain *why* execution is blocked
  2. Suggest the correct alternative (draft, escalation, manual action)
  3. Record the refusal in the audit trail
- Silent failure is PROHIBITED

**Acceptance Criteria:**
- ✅ Blocked actions return clear error messages
- ✅ Error messages explain the constraint
- ✅ Error messages suggest alternatives
- ✅ All refusals are logged
- ✅ No silent failures

---

### 3.6 Tenant Customisation Requirements

#### FR-050: Customisation Awareness
**Priority:** MEDIUM  
**Source:** PRD-LYNX-001, Section 11

**Requirement:**
- Lynx MUST read tenant metadata
- Lynx MUST read custom schema extensions
- Lynx MUST adjust reasoning based on tenant customisations
- Lynx MUST NOT assume defaults if overridden

**Acceptance Criteria:**
- ✅ Lynx reads tenant metadata from Kernel
- ✅ Lynx adapts advice based on tenant customisations
- ✅ Same question to different tenants may yield different responses
- ✅ Custom schema extensions are respected

---

## 4. Non-Functional Requirements

### 4.1 Performance Requirements

#### NFR-001: Response Time
**Priority:** MEDIUM

**Requirement:**
- Domain MCP calls: < 2 seconds (p95)
- Cluster MCP calls: < 5 seconds (p95)
- Cell MCP calls: < 10 seconds (p95)
- LLM response time: < 30 seconds (p95)

**Acceptance Criteria:**
- ✅ Performance metrics collected
- ✅ 95th percentile meets requirements
- ✅ Performance degradation alerts configured

---

#### NFR-002: Throughput
**Priority:** MEDIUM

**Requirement:**
- Support 100 concurrent users per tenant
- Support 1000 MCP tool calls per minute per tenant

**Acceptance Criteria:**
- ✅ Load testing validates throughput
- ✅ System scales horizontally if needed

---

### 4.2 Security Requirements

#### NFR-010: Authentication & Authorization
**Priority:** HIGH

**Requirement:**
- All requests MUST be authenticated
- All MCP tool calls MUST check permissions
- Tenant isolation MUST be enforced at all layers

**Acceptance Criteria:**
- ✅ No unauthenticated access
- ✅ Permission checks on every tool call
- ✅ Tenant isolation verified in tests

---

#### NFR-011: Data Protection
**Priority:** HIGH

**Requirement:**
- All audit logs MUST be encrypted at rest
- All API communications MUST use TLS
- No sensitive data in logs (PII redaction)

**Acceptance Criteria:**
- ✅ Encryption verified
- ✅ TLS enforced
- ✅ PII redaction tested

---

### 4.3 Reliability Requirements

#### NFR-020: Availability
**Priority:** MEDIUM

**Requirement:**
- System availability: 99.5% uptime
- Graceful degradation if LLM API unavailable
- Audit logging continues even if LLM fails

**Acceptance Criteria:**
- ✅ Uptime monitoring configured
- ✅ Fallback behavior tested
- ✅ Audit logging resilient

---

#### NFR-021: Error Recovery
**Priority:** MEDIUM

**Requirement:**
- System MUST recover from transient failures
- System MUST not lose audit logs
- System MUST retry failed MCP calls (with backoff)

**Acceptance Criteria:**
- ✅ Retry logic implemented
- ✅ Audit log persistence verified
- ✅ Error recovery tested

---

### 4.4 Compliance Requirements

#### NFR-030: Audit Compliance
**Priority:** HIGH

**Requirement:**
- All actions MUST be logged
- Audit logs MUST be immutable
- Audit logs MUST be queryable
- Audit retention: 7 years (SOX compliance)

**Acceptance Criteria:**
- ✅ Audit log immutability verified
- ✅ Query API available
- ✅ Retention policy enforced

---

## 5. Interface Requirements

### 5.1 User Interface Requirements

#### UI-001: Entry Points
**Priority:** HIGH

**Requirement:**
- Global "Ask Lynx" button in NexusCanon UI
- Contextual "Ask Lynx about this" buttons
- Inline suggestions within workflows

**Acceptance Criteria:**
- ✅ UI components implemented
- ✅ Entry points functional
- ✅ Contextual buttons work

---

#### UI-002: Response Display
**Priority:** HIGH

**Requirement:**
- Clear separation between:
  - Advice (read-only)
  - Draft (reviewable)
  - Execution (requires confirmation)
- Explicit confirmation before execution
- Visible audit trail

**Acceptance Criteria:**
- ✅ UI clearly distinguishes advice/draft/execution
- ✅ Confirmation dialogs for high-risk actions
- ✅ Audit trail visible to users

---

### 5.2 API Requirements

#### API-001: MCP Tool API
**Priority:** HIGH

**Requirement:**
- REST API for MCP tool registration
- REST API for MCP tool discovery
- REST API for MCP tool execution
- All APIs MUST be tenant-scoped

**Acceptance Criteria:**
- ✅ API endpoints implemented
- ✅ API documentation available
- ✅ Tenant scoping verified

---

#### API-002: Kernel Integration API
**Priority:** HIGH

**Requirement:**
- API to read Kernel metadata
- API to read Kernel schema
- API to check permissions
- API to read lifecycle rules

**Acceptance Criteria:**
- ✅ Kernel API integration working
- ✅ All Kernel APIs called correctly
- ✅ Error handling for Kernel API failures

---

## 6. Data Requirements

### 6.1 Data Models

#### DATA-001: Lynx Run Model
**Priority:** HIGH

**Requirement:**
- Every interaction creates a Lynx Run record
- Fields: runId, userId, tenantId, userQuery, lynxResponse, timestamp, status

**Schema:**
```typescript
interface LynxRun {
  runId: string;              // UUID
  userId: string;
  tenantId: string;
  userQuery: string;
  lynxResponse: string;
  timestamp: Date;
  status: "completed" | "failed" | "blocked";
  toolCalls: ToolCall[];
  auditLogId: string;
}
```

---

#### DATA-002: Audit Log Model
**Priority:** HIGH

**Requirement:**
- Every action creates an audit log entry
- Fields: auditId, lynxRunId, toolId, userId, tenantId, input, output, timestamp, riskLevel

**Schema:**
```typescript
interface AuditLog {
  auditId: string;            // UUID
  lynxRunId: string;
  toolId: string;
  userId: string;
  tenantId: string;
  input: any;
  output: any;
  timestamp: Date;
  riskLevel: "low" | "medium" | "high";
  approved: boolean;
  approvedBy?: string;
}
```

---

## 7. Validation & Testing Requirements

### 7.1 Unit Testing

**Requirement:**
- All MCP tools MUST have unit tests
- All permission checks MUST be tested
- All risk classification logic MUST be tested

**Coverage Target:** 80% code coverage

---

### 7.2 Integration Testing

**Requirement:**
- Integration tests for Kernel API calls
- Integration tests for tenant isolation
- Integration tests for audit logging

---

### 7.3 End-to-End Testing

**Requirement:**
- E2E tests for all 5 canonical use cases
- E2E tests for approval workflows
- E2E tests for failure scenarios

---

## 8. Deployment Requirements

### 8.1 Environment Requirements

**Requirement:**
- Python 3.10+
- mcp-agent framework
- Access to Kernel APIs
- Access to Supabase (for audit logs)
- LLM API access (OpenAI/Anthropic)

---

### 8.2 Configuration Requirements

**Requirement:**
- Configuration via YAML files
- Environment variable support
- Secrets management (API keys)
- Tenant-specific configuration support

---

## 9. References

- **PRD-LYNX-001** - Master PRD (SSOT)
- **PRD-LYNX-003** - HYBRID BASIC Implementation Strategy
- **ADR-LYNX-001** - Architecture Decision Record
- **TSD-LYNX-001** - Technical Specification Document
- **SOP-LYNX-001** - Standard Operating Procedures
- **IMPLEMENTATION-LYNX-001** - Implementation Plan

---

## 10. Approval

**Status:** DRAFT  
**Next Steps:**
1. Review by QA Lead
2. Review by Chief Architect
3. Approval by Product Owner
4. Begin implementation per IMPLEMENTATION-LYNX-001

---

**End of SRS**

