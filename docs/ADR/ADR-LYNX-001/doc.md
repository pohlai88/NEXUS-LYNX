<!-- BEGIN: AIBOS_MANAGED -->
| Field | Value |
|---|---|
| **Document ID** | ADR-LYNX-001 |
| **Document Type** | ADR |
| **Classification** | STANDARD |
| **Title** | Lynx AI Implementation Architecture Decision: Build Strategy & MCP Taxonomy |
| **Status** | DRAFT |
| **Authority** | DERIVED |
| **Derived From** | `PRD-LYNX-001`, `PRD-LYNX-003` |
| **Version** | 1.0.0 |
| **Owners** | `Chief Architect`, `Lead Engineer` |
| **Updated** | 2026-01-01 |

<!-- END: AIBOS_MANAGED -->



# Lynx AI Implementation Architecture Decision: Build Strategy & MCP Taxonomy

**Derived from:** PRD-LYNX-001

---

## Context

We need to build Lynx AI following the Master PRD principles without drift. This ADR defines the implementation strategy, MCP taxonomy structure, and build phases.

---

## Decision

### Build Lynx in Phases Following MCP Taxonomy

**Three-Layer MCP Architecture:**
1. **Domain MCPs** (Layer 1) - Read-heavy, advisory
2. **Cluster MCPs** (Layer 2) - Draft creation, medium risk
3. **Cell MCPs** (Layer 3) - Execution, high risk

**Build Order:**
1. Foundation (Core Infrastructure)
2. Domain Layer (Advisory Capabilities)
3. Cluster Layer (Draft Creation)
4. Cell Layer (Execution)
5. Integration & Polish

---

## Implementation Phases

### Phase 1: Foundation (Week 1-2)

**Goal:** Establish core infrastructure that enforces PRD laws

**Components:**
1. **Lynx Core Runtime**
   - LLM integration (vendor-agnostic interface)
   - Session management (tenant-scoped)
   - Authentication integration (login required)
   - Audit logging system (audit is reality)

2. **MCP Tool Registry**
   - Tool registration system
   - Schema validation (Zod)
   - Risk classification (Low/Medium/High)
   - Permission checking hooks

3. **Kernel SSOT Integration**
   - Metadata reader
   - Schema reader
   - Permission reader
   - Lifecycle rule reader

**Deliverables:**
- Lynx can authenticate
- Lynx can read Kernel metadata
- Lynx can register MCP tools
- All actions are logged

**Validation:**
- ✅ Law 1 (Kernel Supremacy) - Enforced
- ✅ Law 2 (Tenant Absolutism) - Enforced
- ✅ Law 5 (Audit Is Reality) - Enforced

---

### Phase 2: Domain MCPs (Week 3-4)

**Goal:** Enable advisory and read-only capabilities

**MCPs to Build (10-15 total):**

**Finance Domain:**
- `finance.domain.health.read` - Financial health summary
- `finance.domain.payment.gaps.read` - Missing payment records
- `finance.domain.audit.risk.read` - Audit risk assessment

**Vendor Domain:**
- `vendor.domain.summary.read` - Vendor overview
- `vendor.domain.documents.status.read` - Document compliance status
- `vendor.domain.performance.read` - Vendor performance metrics

**Workflow Domain:**
- `workflow.domain.inefficiency.scan` - Detect inefficient workflows
- `workflow.domain.usage.analyze` - Workflow usage patterns
- `workflow.domain.compliance.check` - Workflow compliance status

**Compliance Domain:**
- `compliance.domain.risk.explain` - Explain compliance risks
- `compliance.domain.gaps.identify` - Identify compliance gaps

**Design System Domain:**
- `design.domain.tokens.read` - Read design tokens
- `design.domain.brand.read` - Read brand guidelines

**Deliverables:**
- 10-15 Domain MCPs implemented
- Lynx can provide advisory responses
- All reads are tenant-scoped
- No side effects

**Validation:**
- ✅ Law 3 (Tool-Only Action) - Domain layer enforced
- ✅ Cognitive freedom works (broad reasoning)
- ✅ Operational constraint works (read-only)

---

### Phase 3: Cluster MCPs (Week 5-6)

**Goal:** Enable draft creation and preparation

**MCPs to Build (15-25 total):**

**Document Cluster:**
- `document.cluster.request.draft` - Create document request drafts
- `document.cluster.batch.draft` - Create batch document requests
- `document.cluster.message.draft` - Draft vendor messages

**Workflow Cluster:**
- `workflow.cluster.approval.draft` - Draft approval workflows
- `workflow.cluster.digital.draft` - Draft digital workflow proposals
- `workflow.cluster.optimization.draft` - Draft workflow optimizations

**Portal Cluster:**
- `portal.cluster.scaffold.draft` - Draft portal structure
- `portal.cluster.config.draft` - Draft portal configuration
- `portal.cluster.access.draft` - Draft access rules

**VPM Cluster:**
- `vpm.cluster.payment.draft` - Draft payment records
- `vpm.cluster.reconciliation.draft` - Draft reconciliation entries

**Policy Cluster:**
- `policy.cluster.revision.draft` - Draft policy revisions
- `policy.cluster.compliance.draft` - Draft compliance policies

**Deliverables:**
- 15-25 Cluster MCPs implemented
- Lynx can create drafts
- Drafts require review before execution
- Medium risk classification enforced

**Validation:**
- ✅ Law 4 (Suggest First) - Draft mode works
- ✅ Role-based approval enforced
- ✅ Drafts are logged

---

### Phase 4: Cell MCPs (Week 7-9)

**Goal:** Enable controlled execution

**MCPs to Build (30-50 total):**

**Document Cell:**
- `document.cell.request.create` - Create document requests
- `document.cell.request.publish` - Publish document requests
- `document.cell.reminder.send` - Send document reminders

**Workflow Cell:**
- `workflow.cell.publish` - Publish workflows
- `workflow.cell.activate` - Activate workflows
- `workflow.cell.archive` - Archive workflows

**VPM Cell:**
- `vpm.cell.payment.record` - Record payments
- `vpm.cell.reconciliation.create` - Create reconciliation entries

**Portal Cell:**
- `portal.cell.enable` - Enable portal
- `portal.cell.module.toggle` - Toggle portal modules
- `portal.cell.access.update` - Update access rules

**Deliverables:**
- 30-50 Cell MCPs implemented
- High-risk actions require explicit approval
- All executions are logged
- Soft-delete only (no hard deletes)

**Validation:**
- ✅ Law 3 (Tool-Only Action) - Full enforcement
- ✅ Law 4 (Execute with Consent) - Approval gates work
- ✅ All actions are auditable

---

### Phase 5: Integration & Polish (Week 10-12)

**Goal:** Complete use cases and UX

**Components:**

1. **UI Integration**
   - Global "Ask Lynx" button
   - Contextual "Ask Lynx about this" buttons
   - Inline suggestions
   - Draft review interface
   - Execution confirmation dialogs
   - Audit trail visibility

2. **Use Case Implementation**
   - Document Request Assistant (Primary MVP)
   - Workflow Optimisation Advisor
   - Financial Discipline Coach (VPM)
   - Customer Portal Scaffolder
   - Design System & Brand Assistant

3. **Tenant Customisation Support**
   - Tenant metadata reader
   - Custom schema extension reader
   - Customisation-aware reasoning
   - Tenant-specific advice generation

4. **Failure & Refusal Handling**
   - Explain blocked actions
   - Suggest alternatives
   - Log all refusals
   - No silent failures

**Deliverables:**
- All 5 canonical use cases working
- Full UI integration
- Tenant customisation support
- Complete audit trail

**Validation:**
- ✅ All PRD laws enforced
- ✅ All use cases functional
- ✅ Zero unauthorized executions
- ✅ Full audit traceability

---

## MCP Tool Structure

### Standard MCP Tool Schema

```typescript
interface MCPTool {
  // Identity
  id: string;                    // e.g., "document.cluster.request.draft"
  name: string;                  // Human-readable name
  description: string;           // What it does
  
  // Classification
  layer: "domain" | "cluster" | "cell";
  risk: "low" | "medium" | "high";
  domain: string;                // e.g., "document", "workflow", "finance"
  
  // Schema
  inputSchema: ZodSchema;        // Input validation
  outputSchema: ZodSchema;       // Output validation
  
  // Permissions
  requiredRole?: string[];       // Role requirements
  requiredScope?: string[];      // Scope requirements
  tenantScoped: boolean;        // Always true for Lynx
  
  // Execution
  handler: (input: any, context: ExecutionContext) => Promise<any>;
  
  // Audit
  auditRequired: boolean;        // Always true
  auditCategory: string;         // Audit categorization
}
```

### Execution Context

```typescript
interface ExecutionContext {
  // User & Tenant
  userId: string;
  tenantId: string;
  userRole: string;
  userScope: string[];
  
  // Session
  sessionId: string;
  lynxRunId: string;            // Every interaction creates a run
  
  // Kernel
  kernelMetadata: KernelMetadata;
  tenantCustomizations: TenantCustomizations;
  
  // Audit
  auditLogger: AuditLogger;
}
```

---

## Build Principles (From PRD)

### 1. Cognitive Freedom / Operational Constraint

**Implementation:**
- LLM reasoning: No restrictions on prompt engineering
- Tool execution: Strict MCP-only enforcement
- Code separation: Reasoning layer vs Execution layer

**Code Structure:**
```
lynx/
  reasoning/          # Cognitive freedom
    llm/
    prompts/
    context/
  execution/          # Operational constraint
    mcp-registry/
    tool-handlers/
    permission-checks/
  audit/              # Audit is reality
    logger/
    trail/
```

### 2. MCP-Only Action

**Enforcement:**
- No direct database access
- No direct API calls (except through MCP)
- Runtime check: If tool not registered → fail
- Type safety: All tools typed with Zod

### 3. Tenant Absolutism

**Implementation:**
- Every MCP call includes tenantId
- Kernel enforces tenant isolation
- No cross-tenant data access
- Session scoped to tenant

### 4. Suggest First, Execute with Consent

**Implementation:**
- Default mode: Suggest (no execution)
- Draft creation: Medium risk (role-based)
- Execution: High risk (explicit approval)
- UI: Clear separation of advice/draft/execution

### 5. Audit Is Reality

**Implementation:**
- Every interaction → Lynx Run
- Every tool call → Audit log entry
- Every draft → Audit log entry
- Every execution → Audit log entry
- If not logged → Considered not happened

---

## Risk Classification Implementation

### Risk Level Enforcement

```typescript
function executeMCPTool(
  tool: MCPTool,
  input: any,
  context: ExecutionContext
): Promise<ExecutionResult> {
  // 1. Validate input
  const validatedInput = tool.inputSchema.parse(input);
  
  // 2. Check permissions
  if (!hasPermission(tool, context)) {
    return {
      success: false,
      reason: "Insufficient permissions",
      suggestion: "Request approval or use draft mode"
    };
  }
  
  // 3. Check risk level
  if (tool.risk === "high") {
    if (!context.explicitApproval) {
      return {
        success: false,
        reason: "High-risk action requires explicit approval",
        suggestion: "Use draft mode first"
      };
    }
  }
  
  // 4. Execute (with audit)
  const auditEntry = {
    lynxRunId: context.lynxRunId,
    toolId: tool.id,
    input: validatedInput,
    timestamp: new Date(),
    userId: context.userId,
    tenantId: context.tenantId
  };
  
  context.auditLogger.log(auditEntry);
  
  // 5. Execute tool
  const result = await tool.handler(validatedInput, context);
  
  // 6. Log result
  context.auditLogger.log({
    ...auditEntry,
    result,
    success: true
  });
  
  return { success: true, result };
}
```

---

## Success Criteria

### Phase Completion Criteria

**Phase 1 (Foundation):**
- ✅ Lynx authenticates users
- ✅ Lynx reads Kernel SSOT
- ✅ MCP registry works
- ✅ Audit logging works

**Phase 2 (Domain):**
- ✅ 10-15 Domain MCPs working
- ✅ Advisory responses accurate
- ✅ Tenant-scoped correctly

**Phase 3 (Cluster):**
- ✅ 15-25 Cluster MCPs working
- ✅ Draft creation works
- ✅ Role-based approval works

**Phase 4 (Cell):**
- ✅ 30-50 Cell MCPs working
- ✅ High-risk approval gates work
- ✅ All executions logged

**Phase 5 (Integration):**
- ✅ All 5 use cases working
- ✅ UI fully integrated
- ✅ Zero unauthorized executions
- ✅ Full audit traceability

---

## Consequences

### Positive

- **No Drift:** PRD is SSOT, all decisions trace back to it
- **Safe by Design:** MCP-only enforcement prevents unauthorized actions
- **Auditable:** Every action logged, replayable
- **Extensible:** New MCPs can be added without rewriting Lynx
- **Tenant-Safe:** Strict tenant isolation enforced

### Negative

- **Initial Complexity:** Three-layer MCP taxonomy requires careful design
- **Tool Development:** Each MCP tool must be carefully designed
- **Approval Gates:** May slow down some workflows (by design)

### Mitigation

- Start with Domain MCPs (lowest risk, highest value)
- Build Cluster MCPs for most common use cases first
- Cell MCPs can be added incrementally
- Approval gates are a feature, not a bug (safety first)

---

## References

- **PRD-LYNX-001** - Master PRD for Lynx AI
- **PRD-LYNX-003** - HYBRID BASIC Implementation Strategy
- **SRS-LYNX-001** - Software Requirements Specification
- **TSD-LYNX-001** - Technical Specification Document
- **SOP-LYNX-001** - Standard Operating Procedures
- **IMPLEMENTATION-LYNX-001** - Implementation Plan
- **MCP Taxonomy** - Section 6-9 of PRD-LYNX-001
- **Risk Model** - Section 20-21 of PRD-LYNX-001
- **Cognitive vs Operational Boundary** - Section 19 of PRD-LYNX-001

---

## Status

**Status:** DRAFT  
**Next Steps:**
1. Review and approve this ADR
2. Begin Phase 1 (Foundation) implementation per IMPLEMENTATION-LYNX-001
3. Follow TSD-LYNX-001 for technical implementation
4. Set up development environment

---

**End of ADR**

