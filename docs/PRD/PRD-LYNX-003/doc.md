<!-- BEGIN: AIBOS_MANAGED -->
| Field | Value |
|---|---|
| **Document ID** | PRD-LYNX-003 |
| **Document Type** | PRD |
| **Classification** | STANDARD |
| **Title** | LYNX AI — HYBRID BASIC: Balanced MCP Implementation Strategy |
| **Status** | APPROVED (LOCKED) |
| **Authority** | DERIVED |
| **Version** | 1.1.0 |
| **Owners** | `Founder`, `Chief Architect`, `Product Owner` |
| **Derived From** | `PRD-LYNX-001` |
| **References** | `ANALYSIS-LYNX-002`, `DECISION-LYNX-002` |
| **Updated** | 2026-01-01 |

<!-- END: AIBOS_MANAGED -->

# LYNX AI — HYBRID BASIC: Balanced MCP Implementation Strategy

**Derived from:** PRD-LYNX-001 (Master PRD)  
**Timeline:** 6-8 weeks  
**Goal:** Balanced implementation with core PRD laws enforced

> **🔒 LOCKED DECISION (2026-01-01)**  
> This PRD has been **APPROVED and LOCKED** as the implementation basis for Lynx AI.  
> All development must follow this strategy. Changes require formal RFC process.

---

## Executive Summary

**HYBRID BASIC** is a balanced approach that enforces **core PRD laws** while keeping implementation **practical and achievable**. This strategy uses `mcp-agent` as foundation and builds essential governance layers.

**Key Principle:** Enforce safety (PRD laws) while keeping scope manageable.

---

## Scope & Timeline

### Timeline: 6-8 Weeks

| Week | Phase | Deliverables |
|------|-------|--------------|
| **Week 1-2** | Foundation + Governance | mcp-agent + Kernel/Tenant/Audit layers |
| **Week 3-4** | Domain MCPs | 10-12 Domain MCPs |
| **Week 5-6** | Cluster MCPs | 8-10 Cluster MCPs (drafts) |
| **Week 7-8** | Integration + Polish | UI, use cases, testing |

### Scope: Core Features

- ✅ **10-12 Domain MCPs** (read-only, advisory)
- ✅ **8-10 Cluster MCPs** (draft creation)
- ✅ **Kernel SSOT integration** (read metadata, enforce rules)
- ✅ **Tenant isolation** (multi-tenant support)
- ✅ **Risk classification** (Low/Medium/High)
- ✅ **Basic audit system** (Lynx Run tracking)
- ⚠️ **Limited Cell MCPs** (3-5 execution tools only)
- ⚠️ **Basic approval gates** (role-based, not explicit)

---

## Implementation Strategy

### Phase 1: Foundation + Governance (Weeks 1-2)

**Goal:** mcp-agent + essential governance layers

**Learning Resources:**
- Study `awesome-llm-apps/mcp_ai_agents/browser_mcp_agent/` for structure patterns
- Study `awesome-llm-apps/mcp_ai_agents/github_mcp_agent/` for integration patterns
- Reference `ANALYSIS-LYNX-002.md` for detailed guidance
- **Expected time savings:** 1-2 days from learning examples

**Components:**

1. **mcp-agent Foundation**
   - Install and configure (reference awesome-llm-apps examples)
   - Basic tool registration (learn from browser_mcp_agent example)
   - LLM integration (follow mcp-agent patterns)

2. **Kernel SSOT Integration**
   - Metadata reader
   - Schema reader
   - Permission checker
   - **Enforces PRD Law 1** ✅

3. **Tenant Isolation Layer**
   - Tenant-scoped sessions
   - Tenant boundary enforcement
   - No cross-tenant access
   - **Enforces PRD Law 2** ✅

4. **Risk Classification**
   - Low/Medium/High classification
   - Basic approval gates (role-based)
   - **Enforces PRD Section 20-21** ✅

5. **Basic Audit System**
   - Lynx Run tracking
   - Tool call logging
   - Audit trail storage
   - **Enforces PRD Law 5** ✅

**Deliverable:** Foundation with all core PRD laws enforced

---

### Phase 2: Domain MCPs (Weeks 3-4)

**Goal:** 10-12 Domain MCPs (read-only, advisory)

**MCPs to Build:**

**Finance Domain (3 tools):**
- `finance.domain.health.read`
- `finance.domain.payment.gaps.read`
- `finance.domain.audit.risk.read`

**Vendor Domain (3 tools):**
- `vendor.domain.summary.read`
- `vendor.domain.documents.status.read`
- `vendor.domain.performance.read`

**Workflow Domain (2 tools):**
- `workflow.domain.inefficiency.scan`
- `workflow.domain.usage.analyze`

**Compliance Domain (2 tools):**
- `compliance.domain.risk.explain`
- `compliance.domain.gaps.identify`

**Design Domain (2 tools):**
- `design.domain.tokens.read`
- `design.domain.brand.read`

**All tools:**
- Read-only (no side effects)
- Tenant-scoped
- Kernel SSOT integration
- Audit logged

**Deliverable:** 10-12 Domain MCPs working with governance

---

### Phase 3: Cluster MCPs (Weeks 5-6)

**Goal:** 8-10 Cluster MCPs (draft creation, medium risk)

**MCPs to Build:**

**Document Cluster (3 tools):**
- `document.cluster.request.draft`
- `document.cluster.batch.draft`
- `document.cluster.message.draft`

**Workflow Cluster (2 tools):**
- `workflow.cluster.approval.draft`
- `workflow.cluster.digital.draft`

**Portal Cluster (2 tools):**
- `portal.cluster.scaffold.draft`
- `portal.cluster.config.draft`

**VPM Cluster (1 tool):**
- `vpm.cluster.payment.draft`

**All tools:**
- Create drafts (not execute)
- Medium risk classification
- Role-based approval
- Tenant-scoped
- Audit logged

**Deliverable:** 8-10 Cluster MCPs for draft creation

---

### Phase 4: Limited Cell MCPs (Week 7)

**Goal:** 3-5 Cell MCPs (execution, high risk)

**MCPs to Build (Priority):**

1. **Document Cell:**
   - `document.cell.request.publish` - Publish document requests

2. **Workflow Cell:**
   - `workflow.cell.publish` - Publish workflows

3. **VPM Cell:**
   - `vpm.cell.payment.record` - Record payments

**All tools:**
- High risk classification
- Explicit approval required
- Tenant-scoped
- Full audit trail

**Deliverable:** 3-5 Cell MCPs for critical execution

---

### Phase 5: Integration + Polish (Week 8)

**Goal:** UI, use cases, testing

**Components:**

1. **UI Integration**
   - Global "Ask Lynx" button
   - Contextual "Ask Lynx about this" buttons
   - Draft review interface
   - Execution confirmation dialogs
   - Basic audit trail visibility

2. **Use Cases (3 of 5)**
   - ✅ Document Request Assistant (Primary MVP)
   - ✅ Workflow Optimisation Advisor
   - ✅ Financial Discipline Coach (VPM)
   - ⚠️ Customer Portal Scaffolder (partial)
   - ⚠️ Design System Assistant (basic)

3. **Testing**
   - Unit tests for MCP tools
   - Integration tests
   - Security tests (tenant isolation)

**Deliverable:** Working system with 3 use cases

---

## What's Included

### ✅ Included (HYBRID BASIC)

1. **All Core PRD Laws**
   - ✅ Law 1: Kernel Supremacy
   - ✅ Law 2: Tenant Absolutism
   - ✅ Law 3: Tool-Only Action
   - ✅ Law 4: Suggest First (drafts work)
   - ✅ Law 5: Audit Is Reality

2. **MCP Taxonomy (Partial)**
   - ✅ Domain MCPs (10-12 tools)
   - ✅ Cluster MCPs (8-10 tools)
   - ⚠️ Cell MCPs (3-5 tools only)

3. **Governance**
   - ✅ Kernel SSOT integration
   - ✅ Tenant isolation
   - ✅ Risk classification
   - ✅ Basic audit system

4. **Use Cases (3 of 5)**
   - ✅ Document Request Assistant
   - ✅ Workflow Optimisation Advisor
   - ✅ Financial Discipline Coach

---

## What's NOT Included (Deferred)

### ❌ Deferred to Later

1. **Full Cell MCP Suite**
   - Only 3-5 execution tools
   - Missing: Portal, Policy, advanced Workflow execution
   - **Impact:** Limited execution capabilities

2. **Explicit Approval Gates**
   - Role-based approval only
   - No human-in-the-loop UI
   - **Impact:** Less granular control

3. **Advanced Audit**
   - Basic Lynx Run tracking
   - No replay capability
   - No advanced analytics
   - **Impact:** Limited audit insights

4. **Full Use Cases**
   - 3 of 5 use cases complete
   - Portal Scaffolder partial
   - Design System Assistant basic
   - **Impact:** Not all use cases supported

5. **Tenant Customisation**
   - Basic customisation support
   - No advanced schema extensions
   - **Impact:** Limited tenant flexibility

---

## Success Criteria

### Week 2 Success

- ✅ Foundation with governance layers
- ✅ All PRD laws enforced
- ✅ Kernel SSOT integration working
- ✅ Tenant isolation working

### Week 4 Success

- ✅ 10-12 Domain MCPs working
- ✅ All tools tenant-scoped
- ✅ All tools audit logged
- ✅ Advisory responses accurate

### Week 6 Success

- ✅ 8-10 Cluster MCPs working
- ✅ Draft creation works
- ✅ Role-based approval enforced
- ✅ Drafts require review

### Week 8 Success

- ✅ 3-5 Cell MCPs working
- ✅ Execution with approval gates
- ✅ 3 use cases functional
- ✅ UI integrated
- ✅ Production ready (with limitations)

---

## Risks & Mitigations

### Risk 1: Limited Execution Capabilities

**Risk:** Only 3-5 Cell MCPs, can't execute all operations

**Mitigation:**
- Focus on highest-value executions
- Add more Cell MCPs in next phase
- Use Cluster MCPs for most operations (drafts)

### Risk 2: Basic Approval Gates

**Risk:** Role-based only, no explicit human approval

**Mitigation:**
- All high-risk actions require role check
- Add explicit approval in next phase
- Monitor for unauthorized actions

### Risk 3: Partial Use Cases

**Risk:** Only 3 of 5 use cases complete

**Mitigation:**
- Focus on highest-value use cases
- Complete remaining use cases in next phase
- Document limitations clearly

---

## Migration Path to Comprehensive

**After HYBRID BASIC works:**

1. **Week 9-10:** Add remaining Cell MCPs (20-30 more)
2. **Week 11:** Add explicit approval gates
3. **Week 12:** Complete remaining use cases
4. **Week 13-14:** Advanced audit system
5. **Week 15-16:** Tenant customisation support

**Or:** Use HYBRID BASIC as production baseline, expand incrementally.

---

## Use Cases Supported

### ✅ Fully Supported

1. **Document Request Assistant** ✅
   - Create document request drafts
   - Publish document requests
   - Track document status

2. **Workflow Optimisation Advisor** ✅
   - Detect inefficient workflows
   - Draft digital workflow proposals
   - Publish workflows

3. **Financial Discipline Coach (VPM)** ✅
   - Identify missing payment records
   - Draft payment records
   - Record payments (with approval)

### ⚠️ Partially Supported

4. **Customer Portal Scaffolder** ⚠️
   - Draft portal structure ✅
   - Draft portal configuration ✅
   - Enable portal (limited) ⚠️

5. **Design System & Brand Assistant** ⚠️
   - Read design tokens ✅
   - Read brand guidelines ✅
   - Export CSS/JSON (basic) ⚠️

---

## Technical Stack

### Core

- **mcp-agent** - MCP runtime
- **OpenAI/Anthropic** - LLM provider
- **Python** - Backend implementation
- **TypeScript** - Frontend (optional)

### Governance

- **Kernel API Client** - SSOT integration
- **Tenant Isolation Layer** - Custom implementation
- **Risk Classification** - Custom implementation
- **Audit System** - Custom implementation (basic)

### Storage

- **PostgreSQL** - Audit logs, Lynx Runs
- **Kernel Database** - Source of truth

### UI

- **React/Next.js** - Frontend framework
- **shadcn/ui** - UI components
- **TanStack Query** - State management

---

## Learning Resources & Reference Materials

### Primary Reference: awesome-llm-apps

**Repository:** [Shubhamsaboo/awesome-llm-apps](https://github.com/Shubhamsaboo/awesome-llm-apps)  
**Analysis:** See `ANALYSIS-LYNX-002.md` for detailed analysis  
**Status:** Active (85.9k stars, actively maintained)

#### Value for Lynx Implementation

The **awesome-llm-apps** repository provides **highly valuable learning resources** that can accelerate Lynx development:

**What it provides:**
- ✅ **4+ MCP agent examples** with working code
- ✅ **mcp-agent framework** usage patterns (matches our foundation choice)
- ✅ **Configuration examples** (`mcp_agent.config.yaml` patterns)
- ✅ **Tool implementation patterns** (input/output validation, error handling)
- ✅ **UI integration examples** (Streamlit patterns)
- ✅ **Best practices** from a well-maintained, popular repository

**Estimated time savings:** 8-11 days (15-25% timeline reduction)

#### Key Examples to Study

**Priority 1: Must Study (Week 1-2)**
1. **`mcp_ai_agents/browser_mcp_agent/`**
   - Complete MCP agent implementation
   - Shows `mcp-agent` usage patterns
   - Configuration management examples
   - **Use for:** Foundation structure, tool registration patterns

2. **`mcp_ai_agents/github_mcp_agent/`**
   - External MCP server integration
   - UI integration patterns
   - Natural language interface examples
   - **Use for:** Kernel SSOT integration patterns, UI inspiration

**Priority 2: Should Study (Week 3-4)**
3. **`ai_agent_framework_crash_course/google_adk_crash_course/`**
   - MCP tools integration
   - Structured outputs (Pydantic)
   - Memory patterns
   - **Use for:** Domain MCP implementation patterns

4. **`mcp_ai_agents/multi_mcp_agent/`**
   - Multiple MCP server coordination
   - Tool aggregation patterns
   - **Use for:** MCP tool registry design

#### Integration into Implementation

**Phase 1 (Week 1-2): Foundation**
- Study `browser_mcp_agent` example structure
- Adapt configuration patterns for Lynx
- Learn tool registration patterns
- **Expected benefit:** Faster foundation setup (1-2 days saved)

**Phase 2 (Week 3-4): Domain MCPs**
- Reference tool implementation patterns
- Learn input/output validation approaches
- Study error handling patterns
- **Expected benefit:** Faster Domain MCP development (2-3 days saved)

**Phase 3 (Week 5-6): Cluster MCPs**
- Reference draft creation patterns
- Learn workflow coordination patterns
- **Expected benefit:** Faster Cluster MCP development (1-2 days saved)

**Phase 4 (Week 7-8): Integration**
- Reference UI integration patterns
- Learn state management approaches
- **Expected benefit:** Faster UI integration (1 day saved)

#### What's NOT in awesome-llm-apps

The repository does **not** provide (we must build ourselves):
- ❌ Tenant isolation patterns
- ❌ Governance/audit logging
- ❌ Kernel SSOT integration
- ❌ Risk classification
- ❌ Approval workflows

**Action:** Use awesome-llm-apps for **MCP patterns**, build **governance layers** per PRD-LYNX-001.

#### Usage Strategy

**Do:**
- ✅ Study MCP agent examples for structure and patterns
- ✅ Learn `mcp-agent` configuration from examples
- ✅ Reference tool implementation patterns
- ✅ Adapt code patterns for Lynx (with governance layers)
- ✅ Use as inspiration for MCP tool structure

**Don't:**
- ❌ Clone as foundation (missing governance)
- ❌ Use directly without adaptation
- ❌ Expect tenant isolation or audit patterns
- ❌ Rely on it for Kernel SSOT integration

**Reference:** See `ANALYSIS-LYNX-002.md` for complete analysis and detailed recommendations.

---

## Timeline Summary

| Phase | Weeks | Deliverable |
|-------|-------|-------------|
| Foundation + Governance | 1-2 | All PRD laws enforced |
| Domain MCPs | 3-4 | 10-12 tools working |
| Cluster MCPs | 5-6 | 8-10 tools working |
| Limited Cell MCPs | 7 | 3-5 tools working |
| Integration + Polish | 8 | 3 use cases, UI, production ready |
| **TOTAL** | **8 weeks** | **Production-ready with limitations** |

---

## Decision Criteria

**Choose HYBRID BASIC if:**

- ✅ Need core PRD laws enforced
- ✅ Multi-tenant required
- ✅ Need draft creation capabilities
- ✅ Need limited execution
- ✅ 8-week timeline acceptable
- ✅ Can defer full Cell MCP suite

**Do NOT choose HYBRID BASIC if:**

- ❌ Need all 5 use cases immediately
- ❌ Need full Cell MCP suite (30-50 tools)
- ❌ Need explicit approval gates from day 1
- ❌ Need advanced audit capabilities
- ❌ Need full tenant customisation

---

## Comparison with Other Strategies

| Feature | SHIP NOW | HYBRID BASIC | HYBRID COMPREHENSIVE |
|---------|----------|--------------|---------------------|
| **Timeline** | 1-2 weeks | 6-8 weeks | 15-17 weeks |
| **Domain MCPs** | 5-7 | 10-12 | 10-15 |
| **Cluster MCPs** | 0 | 8-10 | 15-25 |
| **Cell MCPs** | 0 | 3-5 | 30-50 |
| **PRD Laws** | Partial | ✅ All | ✅ All |
| **Tenant Isolation** | ❌ | ✅ | ✅ |
| **Risk Classification** | ❌ | ✅ Basic | ✅ Full |
| **Use Cases** | 0 | 3 of 5 | 5 of 5 |
| **Production Ready** | ⚠️ Limited | ✅ Yes | ✅ Yes |

---

## Next Steps

1. **Approve this PRD**
2. **Set up foundation** (Week 1)
3. **Build governance layers** (Week 2)
4. **Implement Domain MCPs** (Weeks 3-4)
5. **Implement Cluster MCPs** (Weeks 5-6)
6. **Implement limited Cell MCPs** (Week 7)
7. **Integrate and polish** (Week 8)
8. **Ship to production** (Week 8)

---

## References

- **PRD-LYNX-001** - Master PRD (SSOT)
- **ANALYSIS-LYNX-002** - awesome-llm-apps Repository Analysis
- **DECISION-LYNX-002** - GitHub Repository Selection for PRD-LYNX-003
- **ADR-LYNX-001** - Architecture Decision Record
- **SRS-LYNX-001** - Software Requirements Specification
- **TSD-LYNX-001** - Technical Specification Document

---

**End of PRD-LYNX-003 (HYBRID BASIC)**

