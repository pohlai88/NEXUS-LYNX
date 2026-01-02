<!-- BEGIN: AIBOS_MANAGED -->
| Field | Value |
|---|---|
| **Document ID** | PRD-LYNX-004 |
| **Document Type** | PRD |
| **Classification** | STANDARD |
| **Title** | LYNX AI — HYBRID COMPREHENSIVE: Full MCP Implementation Strategy |
| **Status** | DRAFT |
| **Authority** | DERIVED |
| **Version** | 1.0.0 |
| **Owners** | `Founder`, `Chief Architect`, `Product Owner` |
| **Derived From** | `PRD-LYNX-001` |
| **Updated** | 2026-01-01 |

<!-- END: AIBOS_MANAGED -->

# LYNX AI — HYBRID COMPREHENSIVE: Full MCP Implementation Strategy

**Derived from:** PRD-LYNX-001 (Master PRD)  
**Timeline:** 15-17 weeks  
**Goal:** Complete implementation with all PRD requirements

---

## Executive Summary

**HYBRID COMPREHENSIVE** is the full implementation of Lynx AI following the Master PRD. This strategy enforces **all PRD laws**, implements **complete MCP taxonomy**, and delivers **all 5 canonical use cases**.

**Key Principle:** Build it right, build it complete, build it once.

---

## Scope & Timeline

### Timeline: 15-17 Weeks

| Week | Phase | Deliverables |
|------|-------|--------------|
| **Week 1-2** | Foundation + Governance | mcp-agent + all governance layers |
| **Week 3-4** | Domain MCPs | 10-15 Domain MCPs |
| **Week 5-7** | Cluster MCPs | 15-25 Cluster MCPs |
| **Week 8-11** | Cell MCPs | 30-50 Cell MCPs |
| **Week 12-15** | Integration + Use Cases | All 5 use cases, full UI |
| **Week 16-17** | Polish + Testing | Testing, optimization, production |

### Scope: Complete Implementation

- ✅ **10-15 Domain MCPs** (read-only, advisory)
- ✅ **15-25 Cluster MCPs** (draft creation)
- ✅ **30-50 Cell MCPs** (execution)
- ✅ **Kernel SSOT integration** (full metadata, schema, permissions)
- ✅ **Tenant isolation** (strict multi-tenant support)
- ✅ **Risk classification** (Low/Medium/High with approval gates)
- ✅ **Full audit system** (Lynx Run tracking, replay, analytics)
- ✅ **Tenant customisation** (schema extensions, custom workflows)
- ✅ **All 5 use cases** (complete implementation)

---

## Implementation Strategy

### Phase 1: Foundation + Governance (Weeks 1-2)

**Goal:** Complete foundation with all governance layers

**Components:**

1. **mcp-agent Foundation**
   - Full MCP protocol support
   - Tool registration system
   - LLM integration (multi-provider)
   - Durable execution (Temporal)

2. **Kernel SSOT Integration (Complete)**
   - Metadata reader (all domains)
   - Schema reader (with extensions)
   - Permission checker (role + scope)
   - Lifecycle rule reader
   - **Enforces PRD Law 1** ✅

3. **Tenant Isolation Layer (Complete)**
   - Tenant-scoped sessions
   - Strict tenant boundary enforcement
   - No cross-tenant access
   - Tenant metadata support
   - **Enforces PRD Law 2** ✅

4. **Risk Classification (Complete)**
   - Low/Medium/High classification
   - Approval gate enforcement
   - Role-based checks
   - Explicit approval (human-in-the-loop)
   - **Enforces PRD Section 20-21** ✅

5. **Full Audit System**
   - Lynx Run tracking (every interaction)
   - Tool call logging (with context)
   - Draft tracking
   - Execution tracking
   - Replay capability
   - Analytics dashboard
   - **Enforces PRD Law 5** ✅

**Deliverable:** Complete foundation with all PRD laws enforced

---

### Phase 2: Domain MCPs (Weeks 3-4)

**Goal:** 10-15 Domain MCPs (read-only, advisory)

**MCPs to Build:**

**Finance Domain (4 tools):**
- `finance.domain.health.read`
- `finance.domain.payment.gaps.read`
- `finance.domain.audit.risk.read`
- `finance.domain.compliance.status.read`

**Vendor Domain (3 tools):**
- `vendor.domain.summary.read`
- `vendor.domain.documents.status.read`
- `vendor.domain.performance.read`

**Workflow Domain (3 tools):**
- `workflow.domain.inefficiency.scan`
- `workflow.domain.usage.analyze`
- `workflow.domain.compliance.check`

**Compliance Domain (2 tools):**
- `compliance.domain.risk.explain`
- `compliance.domain.gaps.identify`

**Design Domain (2 tools):**
- `design.domain.tokens.read`
- `design.domain.brand.read`

**Portal Domain (1 tool):**
- `portal.domain.status.read`

**All tools:**
- Read-only (no side effects)
- Tenant-scoped
- Kernel SSOT integration
- Full audit logging
- Tenant customisation aware

**Deliverable:** 10-15 Domain MCPs with full governance

---

### Phase 3: Cluster MCPs (Weeks 5-7)

**Goal:** 15-25 Cluster MCPs (draft creation, medium risk)

**MCPs to Build:**

**Document Cluster (5 tools):**
- `document.cluster.request.draft`
- `document.cluster.batch.draft`
- `document.cluster.message.draft`
- `document.cluster.reminder.draft`
- `document.cluster.template.draft`

**Workflow Cluster (5 tools):**
- `workflow.cluster.approval.draft`
- `workflow.cluster.digital.draft`
- `workflow.cluster.optimization.draft`
- `workflow.cluster.automation.draft`
- `workflow.cluster.integration.draft`

**Portal Cluster (4 tools):**
- `portal.cluster.scaffold.draft`
- `portal.cluster.config.draft`
- `portal.cluster.access.draft`
- `portal.cluster.module.draft`

**VPM Cluster (3 tools):**
- `vpm.cluster.payment.draft`
- `vpm.cluster.reconciliation.draft`
- `vpm.cluster.batch.draft`

**Policy Cluster (3 tools):**
- `policy.cluster.revision.draft`
- `policy.cluster.compliance.draft`
- `policy.cluster.governance.draft`

**All tools:**
- Create drafts (not execute)
- Medium risk classification
- Role-based approval
- Tenant-scoped
- Full audit logging
- Tenant customisation aware

**Deliverable:** 15-25 Cluster MCPs for comprehensive draft creation

---

### Phase 4: Cell MCPs (Weeks 8-11)

**Goal:** 30-50 Cell MCPs (execution, high risk)

**MCPs to Build:**

**Document Cell (8 tools):**
- `document.cell.request.create`
- `document.cell.request.publish`
- `document.cell.request.update`
- `document.cell.reminder.send`
- `document.cell.status.update`
- `document.cell.batch.publish`
- `document.cell.template.create`
- `document.cell.archive`

**Workflow Cell (10 tools):**
- `workflow.cell.publish`
- `workflow.cell.activate`
- `workflow.cell.deactivate`
- `workflow.cell.archive`
- `workflow.cell.version.create`
- `workflow.cell.approval.configure`
- `workflow.cell.automation.enable`
- `workflow.cell.integration.connect`
- `workflow.cell.permission.update`
- `workflow.cell.delete` (soft)

**VPM Cell (6 tools):**
- `vpm.cell.payment.record`
- `vpm.cell.payment.update`
- `vpm.cell.reconciliation.create`
- `vpm.cell.reconciliation.approve`
- `vpm.cell.batch.process`
- `vpm.cell.archive`

**Portal Cell (8 tools):**
- `portal.cell.enable`
- `portal.cell.disable`
- `portal.cell.module.toggle`
- `portal.cell.access.update`
- `portal.cell.config.apply`
- `portal.cell.theme.update`
- `portal.cell.integration.connect`
- `portal.cell.archive`

**Policy Cell (5 tools):**
- `policy.cell.publish`
- `policy.cell.activate`
- `policy.cell.revision.create`
- `policy.cell.compliance.enforce`
- `policy.cell.archive`

**All tools:**
- High risk classification
- Explicit approval required
- Tenant-scoped
- Full audit trail
- Soft-delete only
- Tenant customisation aware

**Deliverable:** 30-50 Cell MCPs for comprehensive execution

---

### Phase 5: Integration + Use Cases (Weeks 12-15)

**Goal:** All 5 use cases, full UI, complete integration

**Components:**

1. **Complete UI Integration**
   - Global "Ask Lynx" button
   - Contextual "Ask Lynx about this" buttons
   - Inline suggestions
   - Draft review interface
   - Execution confirmation dialogs
   - Approval workflow UI
   - Full audit trail visibility
   - Analytics dashboard

2. **All 5 Use Cases (Complete)**

   **a. Document Request Assistant** ✅
   - Identify missing documents
   - Create document request drafts
   - Batch document requests
   - Publish requests
   - Track status
   - Send reminders

   **b. Workflow Optimisation Advisor** ✅
   - Detect inefficient workflows
   - Draft digital workflow proposals
   - Draft approval workflows
   - Publish workflows
   - Activate workflows

   **c. Financial Discipline Coach (VPM)** ✅
   - Identify missing payment records
   - Draft payment records
   - Record payments (with approval)
   - Create reconciliation entries
   - Track payment compliance

   **d. Customer Portal Scaffolder** ✅
   - Draft portal structure
   - Draft portal configuration
   - Draft access rules
   - Enable portal
   - Configure modules
   - Update themes

   **e. Design System & Brand Assistant** ✅
   - Read design tokens
   - Read brand guidelines
   - Export CSS/JSON snippets
   - Validate accessibility
   - Suggest improvements

3. **Tenant Customisation Support**
   - Read tenant metadata
   - Read custom schema extensions
   - Customisation-aware reasoning
   - Tenant-specific advice generation

4. **Failure & Refusal Handling**
   - Explain blocked actions
   - Suggest alternatives
   - Log all refusals
   - No silent failures

**Deliverable:** Complete system with all use cases

---

### Phase 6: Polish + Testing (Weeks 16-17)

**Goal:** Testing, optimization, production readiness

**Tasks:**

1. **Comprehensive Testing**
   - Unit tests (all MCP tools)
   - Integration tests (end-to-end)
   - Security tests (tenant isolation)
   - Performance tests
   - Load tests

2. **Optimization**
   - Performance tuning
   - Cost optimization
   - Error handling improvements
   - UX polish

3. **Documentation**
   - User guides
   - Developer guides
   - API documentation
   - Troubleshooting guides

4. **Production Readiness**
   - Deployment scripts
   - Monitoring setup
   - Alerting configuration
   - Backup procedures

**Deliverable:** Production-ready system

---

## What's Included

### ✅ Included (HYBRID COMPREHENSIVE)

1. **All PRD Laws (Complete)**
   - ✅ Law 1: Kernel Supremacy (full integration)
   - ✅ Law 2: Tenant Absolutism (strict enforcement)
   - ✅ Law 3: Tool-Only Action (all actions via MCP)
   - ✅ Law 4: Suggest First (drafts + execution)
   - ✅ Law 5: Audit Is Reality (complete audit system)

2. **Complete MCP Taxonomy**
   - ✅ Domain MCPs (10-15 tools)
   - ✅ Cluster MCPs (15-25 tools)
   - ✅ Cell MCPs (30-50 tools)

3. **Full Governance**
   - ✅ Kernel SSOT integration (complete)
   - ✅ Tenant isolation (strict)
   - ✅ Risk classification (full)
   - ✅ Approval gates (explicit)
   - ✅ Complete audit system

4. **All 5 Use Cases**
   - ✅ Document Request Assistant
   - ✅ Workflow Optimisation Advisor
   - ✅ Financial Discipline Coach (VPM)
   - ✅ Customer Portal Scaffolder
   - ✅ Design System & Brand Assistant

5. **Advanced Features**
   - ✅ Tenant customisation support
   - ✅ Failure handling
   - ✅ Analytics dashboard
   - ✅ Replay capability
   - ✅ Complete UI

---

## Success Criteria

### Week 2 Success

- ✅ Complete foundation with all governance layers
- ✅ All PRD laws enforced
- ✅ Kernel SSOT integration complete
- ✅ Tenant isolation strict
- ✅ Full audit system working

### Week 4 Success

- ✅ 10-15 Domain MCPs working
- ✅ All tools tenant-scoped
- ✅ All tools audit logged
- ✅ Tenant customisation aware

### Week 7 Success

- ✅ 15-25 Cluster MCPs working
- ✅ Draft creation comprehensive
- ✅ Role-based approval enforced
- ✅ All drafts require review

### Week 11 Success

- ✅ 30-50 Cell MCPs working
- ✅ Execution with explicit approval
- ✅ All high-risk actions gated
- ✅ Complete execution capabilities

### Week 15 Success

- ✅ All 5 use cases functional
- ✅ Complete UI integrated
- ✅ Tenant customisation working
- ✅ Failure handling complete

### Week 17 Success

- ✅ All tests passing
- ✅ Performance optimized
- ✅ Documentation complete
- ✅ Production ready

---

## Technical Stack

### Core

- **mcp-agent** - MCP runtime (full features)
- **OpenAI/Anthropic/Google** - Multi-provider LLM support
- **Python** - Backend implementation
- **TypeScript** - Frontend implementation

### Governance

- **Kernel API Client** - Complete SSOT integration
- **Tenant Isolation Layer** - Strict enforcement
- **Risk Classification** - Complete implementation
- **Audit System** - Full system with analytics

### Storage

- **PostgreSQL** - Audit logs, Lynx Runs, analytics
- **Kernel Database** - Source of truth
- **Redis** - Caching, session management

### UI

- **React/Next.js** - Frontend framework
- **shadcn/ui** - UI components
- **TanStack Query** - State management
- **Recharts** - Analytics visualization

### Infrastructure

- **Docker** - Containerization
- **Kubernetes** - Orchestration (optional)
- **Monitoring** - Prometheus, Grafana
- **Logging** - ELK stack or similar

---

## Timeline Summary

| Phase | Weeks | Deliverable |
|-------|-------|-------------|
| Foundation + Governance | 1-2 | All PRD laws enforced |
| Domain MCPs | 3-4 | 10-15 tools working |
| Cluster MCPs | 5-7 | 15-25 tools working |
| Cell MCPs | 8-11 | 30-50 tools working |
| Integration + Use Cases | 12-15 | All 5 use cases, full UI |
| Polish + Testing | 16-17 | Production ready |
| **TOTAL** | **17 weeks** | **Complete implementation** |

---

## Decision Criteria

**Choose HYBRID COMPREHENSIVE if:**

- ✅ Need complete PRD compliance
- ✅ Need all 5 use cases
- ✅ Need full MCP taxonomy (55-90 tools)
- ✅ Need explicit approval gates
- ✅ Need advanced audit capabilities
- ✅ Need tenant customisation
- ✅ 15-17 week timeline acceptable
- ✅ Budget allows full implementation

**Do NOT choose HYBRID COMPREHENSIVE if:**

- ❌ Need quick proof-of-concept
- ❌ Limited budget/resources
- ❌ Can't wait 15-17 weeks
- ❌ Don't need all features immediately
- ❌ Prefer incremental rollout

---

## Comparison with Other Strategies

| Feature | SHIP NOW | HYBRID BASIC | HYBRID COMPREHENSIVE |
|---------|----------|--------------|---------------------|
| **Timeline** | 1-2 weeks | 6-8 weeks | 15-17 weeks |
| **Domain MCPs** | 5-7 | 10-12 | 10-15 |
| **Cluster MCPs** | 0 | 8-10 | 15-25 |
| **Cell MCPs** | 0 | 3-5 | 30-50 |
| **Total MCPs** | 5-7 | 21-27 | 55-90 |
| **PRD Laws** | Partial | ✅ All | ✅ All |
| **Tenant Isolation** | ❌ | ✅ | ✅ Strict |
| **Risk Classification** | ❌ | ✅ Basic | ✅ Full |
| **Approval Gates** | ❌ | ✅ Role-based | ✅ Explicit |
| **Audit System** | Basic | Basic | ✅ Complete |
| **Use Cases** | 0 | 3 of 5 | ✅ 5 of 5 |
| **Tenant Customisation** | ❌ | ⚠️ Basic | ✅ Full |
| **Production Ready** | ⚠️ Limited | ✅ Yes | ✅ Complete |

---

## Migration from Other Strategies

### From SHIP NOW

**If starting with SHIP NOW, migrate to COMPREHENSIVE:**

1. **Week 3:** Add governance layers
2. **Week 4-5:** Expand Domain MCPs
3. **Week 6-8:** Add Cluster MCPs
4. **Week 9-12:** Add Cell MCPs
5. **Week 13-15:** Complete use cases
6. **Week 16-17:** Polish and test

**Total additional time: 14-15 weeks**

### From HYBRID BASIC

**If starting with HYBRID BASIC, migrate to COMPREHENSIVE:**

1. **Week 9-10:** Expand Cluster MCPs (7-15 more)
2. **Week 11-13:** Expand Cell MCPs (25-45 more)
3. **Week 14-15:** Complete remaining use cases
4. **Week 16:** Advanced audit features
5. **Week 17:** Tenant customisation polish

**Total additional time: 9-10 weeks**

---

## Risks & Mitigations

### Risk 1: Timeline Overrun

**Risk:** 15-17 weeks may extend to 20+ weeks

**Mitigation:**
- Phased delivery (ship Domain MCPs first)
- Parallel development (multiple teams)
- Prioritize high-value features

### Risk 2: Complexity

**Risk:** 55-90 MCP tools is complex to maintain

**Mitigation:**
- Standard tool templates
- Automated testing
- Clear documentation
- Incremental rollout

### Risk 3: Over-Engineering

**Risk:** Building more than needed

**Mitigation:**
- Follow PRD strictly (no feature creep)
- Regular reviews
- User feedback loops

---

## Next Steps

1. **Approve this PRD**
2. **Set up foundation** (Week 1)
3. **Build governance layers** (Week 2)
4. **Implement Domain MCPs** (Weeks 3-4)
5. **Implement Cluster MCPs** (Weeks 5-7)
6. **Implement Cell MCPs** (Weeks 8-11)
7. **Integrate use cases** (Weeks 12-15)
8. **Polish and test** (Weeks 16-17)
9. **Ship to production** (Week 17)

---

**End of PRD-LYNX-004 (HYBRID COMPREHENSIVE)**

