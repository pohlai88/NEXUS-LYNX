<!-- BEGIN: AIBOS_MANAGED -->
| Field | Value |
|---|---|
| **Document ID** | IMPLEMENTATION-LYNX-001 |
| **Document Type** | IMPLEMENTATION |
| **Classification** | STANDARD |
| **Title** | Implementation Plan — LYNX AI |
| **Status** | DRAFT |
| **Authority** | DERIVED |
| **Scope** | MULTI_TENANT_PRODUCTION_MVP |
| **Derived From** | `PRD-LYNX-001`, `PRD-LYNX-003`, `ADR-LYNX-001`, `SRS-LYNX-001`, `TSD-LYNX-001` |
| **Version** | 1.0.0 |
| **Owners** | `Lead Engineer`, `Project Manager` |
| **Created** | 2026-01-01 |
| **Updated** | 2026-01-01 |

<!-- END: AIBOS_MANAGED -->

# Implementation Plan — LYNX AI

**Derived from:** PRD-LYNX-001, PRD-LYNX-003, ADR-LYNX-001, SRS-LYNX-001, TSD-LYNX-001  
**Timeline:** 6-8 weeks  
**Status:** DRAFT

---

## 1. Executive Summary

This implementation plan provides a **week-by-week breakdown** of Lynx AI development, following the HYBRID BASIC strategy (PRD-LYNX-003) and technical specifications (TSD-LYNX-001).

**Key Milestones:**
- Week 2: Foundation complete
- Week 4: Domain MCPs operational
- Week 6: Cluster MCPs operational
- Week 8: Production-ready MVP

---

## 2. Team & Roles

### 2.1 Team Structure

| Role | Responsibilities | Allocation |
|------|-----------------|------------|
| **Lead Engineer** | Architecture, code review, critical decisions | 100% |
| **Backend Engineer** | MCP tools, Kernel integration, audit logging | 100% |
| **Frontend Engineer** | UI integration, user experience | 50% |
| **QA Engineer** | Testing, validation, quality assurance | 50% |
| **DevOps Engineer** | Deployment, monitoring, infrastructure | 25% |

---

## 3. Implementation Phases

### Phase 1: Foundation + Governance (Week 1-2)

**Goal:** Establish core infrastructure enforcing PRD laws

#### Week 1: Setup & Core Runtime

**Day 1-2: Project Setup**
- [ ] Clone `mcp-agent` repository
- [ ] Set up development environment
- [ ] Initialize Lynx project structure
- [ ] Configure dependencies (`uv add "mcp-agent[openai]"`)
- [ ] Set up version control

**Day 3-4: Core Runtime**
- [ ] Implement `MCPApp` initialization
- [ ] Implement `Agent` configuration
- [ ] Implement LLM integration (OpenAI)
- [ ] Basic "Hello Lynx" working

**Day 5: Session Management**
- [ ] Implement `SessionManager`
- [ ] Implement tenant-scoped sessions
- [ ] Test session isolation

**Deliverables:**
- ✅ Lynx can start and connect to LLM
- ✅ Sessions are tenant-scoped
- ✅ Basic chat working

---

#### Week 2: Governance Layers

**Day 1-2: MCP Tool Registry**
- [ ] Implement `MCPToolRegistry`
- [ ] Implement tool registration system
- [ ] Implement schema validation (Zod/Pydantic)
- [ ] Implement risk classification

**Day 3-4: Kernel SSOT Integration**
- [ ] Implement `KernelAPI` client
- [ ] Implement metadata reader
- [ ] Implement schema reader
- [ ] Implement permission checker
- [ ] Test Kernel API integration

**Day 5: Audit Logging**
- [ ] Implement `AuditLogger`
- [ ] Set up Supabase connection
- [ ] Create audit log tables
- [ ] Implement Lynx Run logging
- [ ] Implement tool call logging

**Deliverables:**
- ✅ MCP tool registry working
- ✅ Kernel SSOT integration working
- ✅ Audit logging working
- ✅ All PRD laws enforced (Law 1, 2, 3, 5)

**Validation:**
- ✅ Unit tests for core components
- ✅ Integration tests for Kernel API
- ✅ Audit logging verified

---

### Phase 2: Domain MCPs (Week 3-4)

**Goal:** Enable advisory and read-only capabilities

#### Week 3: Finance & Vendor Domain MCPs

**Day 1-2: Finance Domain**
- [ ] Implement `finance.domain.health.read`
- [ ] Implement `finance.domain.payment.gaps.read`
- [ ] Implement `finance.domain.audit.risk.read`
- [ ] Test with real Kernel API data

**Day 3-4: Vendor Domain**
- [ ] Implement `vendor.domain.summary.read`
- [ ] Implement `vendor.domain.documents.status.read`
- [ ] Implement `vendor.domain.performance.read`
- [ ] Test tenant isolation

**Day 5: Testing & Refinement**
- [ ] Unit tests for all Domain MCPs
- [ ] Integration tests
- [ ] Performance testing
- [ ] Documentation

**Deliverables:**
- ✅ 6 Domain MCPs implemented (Finance + Vendor)
- ✅ All are read-only
- ✅ All are tenant-scoped
- ✅ All are "Low" risk

---

#### Week 4: Workflow, Compliance & Design Domain MCPs

**Day 1-2: Workflow Domain**
- [ ] Implement `workflow.domain.inefficiency.scan`
- [ ] Implement `workflow.domain.usage.analyze`
- [ ] Implement `workflow.domain.compliance.check`

**Day 3: Compliance & Design Domain**
- [ ] Implement `compliance.domain.risk.explain`
- [ ] Implement `design.domain.tokens.read`
- [ ] Implement `design.domain.brand.read`

**Day 4-5: Integration & Testing**
- [ ] End-to-end testing
- [ ] User acceptance testing
- [ ] Performance optimization
- [ ] Documentation

**Deliverables:**
- ✅ 10-12 Domain MCPs total implemented
- ✅ All Domain MCPs tested
- ✅ Advisory responses working
- ✅ Cognitive freedom validated

**Validation:**
- ✅ All Domain MCPs return tenant-scoped data
- ✅ No side effects
- ✅ LLM can reason broadly about responses

---

### Phase 3: Cluster MCPs (Week 5-6)

**Goal:** Enable draft creation and preparation

#### Week 5: Document & Workflow Cluster MCPs

**Day 1-2: Document Cluster**
- [ ] Implement `document.cluster.request.draft`
- [ ] Implement `document.cluster.batch.draft`
- [ ] Test draft creation
- [ ] Test draft storage

**Day 3-4: Workflow Cluster**
- [ ] Implement `workflow.cluster.approval.draft`
- [ ] Implement `workflow.cluster.digital.draft`
- [ ] Test role-based approval

**Day 5: Testing**
- [ ] Unit tests
- [ ] Integration tests
- [ ] Approval workflow testing

**Deliverables:**
- ✅ 5 Cluster MCPs implemented
- ✅ Draft creation working
- ✅ Role-based approval enforced

---

#### Week 6: Portal, VPM & Policy Cluster MCPs

**Day 1-2: Portal & VPM Cluster**
- [ ] Implement `portal.cluster.scaffold.draft`
- [ ] Implement `portal.cluster.config.draft`
- [ ] Implement `vpm.cluster.payment.draft`

**Day 3: Policy Cluster**
- [ ] Implement `policy.cluster.revision.draft`

**Day 4-5: Integration & Testing**
- [ ] End-to-end testing
- [ ] Draft review workflow
- [ ] Performance testing

**Deliverables:**
- ✅ 8-10 Cluster MCPs total implemented
- ✅ All create drafts (not execute)
- ✅ All require role-based approval
- ✅ All are "Medium" risk

**Validation:**
- ✅ Drafts are stored and reviewable
- ✅ Role-based approval gates work
- ✅ Operational constraint validated

---

### Phase 4: Limited Cell MCPs (Week 7)

**Goal:** Enable controlled execution (limited for HYBRID BASIC)

#### Week 7: Cell MCP Implementation

**Day 1-2: Document Cell**
- [ ] Implement `document.cell.request.publish`
- [ ] Test explicit approval workflow
- [ ] Test audit logging

**Day 3: Workflow Cell**
- [ ] Implement `workflow.cell.publish`
- [ ] Test approval gates

**Day 4: VPM Cell**
- [ ] Implement `vpm.cell.payment.record`
- [ ] Test high-risk execution

**Day 5: Testing & Validation**
- [ ] End-to-end testing
- [ ] Approval workflow testing
- [ ] Security testing
- [ ] Performance testing

**Deliverables:**
- ✅ 3-5 Cell MCPs implemented
- ✅ All require explicit approval
- ✅ All are "High" risk
- ✅ All executions logged

**Validation:**
- ✅ High-risk approval gates work
- ✅ No unauthorized executions
- ✅ All actions auditable

---

### Phase 5: Integration & Polish (Week 8)

**Goal:** Complete use cases and UX

#### Week 8: UI Integration & Use Cases

**Day 1-2: UI Integration**
- [ ] Global "Ask Lynx" button
- [ ] Contextual "Ask Lynx about this" buttons
- [ ] Response display (advice/draft/execution)
- [ ] Draft review interface
- [ ] Execution confirmation dialogs
- [ ] Audit trail visibility

**Day 3-4: Use Case Implementation**
- [ ] Document Request Assistant (Primary MVP)
- [ ] Workflow Optimisation Advisor
- [ ] Financial Discipline Coach (VPM)

**Day 5: Final Testing & Deployment**
- [ ] End-to-end testing of all use cases
- [ ] User acceptance testing
- [ ] Performance testing
- [ ] Security audit
- [ ] Production deployment

**Deliverables:**
- ✅ All 3 use cases working (of 5 canonical)
- ✅ Full UI integration
- ✅ Production deployment
- ✅ Monitoring configured

**Validation:**
- ✅ All PRD laws enforced
- ✅ Zero unauthorized executions
- ✅ Full audit traceability
- ✅ User acceptance criteria met

---

## 4. Risk Management

### 4.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Kernel API changes | Medium | High | Version API, maintain compatibility layer |
| LLM API rate limits | Medium | Medium | Implement caching, backoff/retry |
| Performance issues | Low | Medium | Load testing, optimization |
| Integration complexity | Medium | High | Early integration testing, POC |

### 4.2 Schedule Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Scope creep | Medium | High | Strict PRD adherence, change control |
| Resource availability | Low | Medium | Cross-training, documentation |
| Dependency delays | Low | Low | Early dependency setup |

---

## 5. Success Criteria

### 5.1 Phase Completion Criteria

**Phase 1 (Foundation):**
- ✅ All PRD laws enforced
- ✅ Core runtime working
- ✅ Audit logging operational

**Phase 2 (Domain):**
- ✅ 10-12 Domain MCPs working
- ✅ Advisory responses accurate
- ✅ Tenant isolation verified

**Phase 3 (Cluster):**
- ✅ 8-10 Cluster MCPs working
- ✅ Draft creation functional
- ✅ Role-based approval working

**Phase 4 (Cell):**
- ✅ 3-5 Cell MCPs working
- ✅ High-risk approval gates functional
- ✅ All executions logged

**Phase 5 (Integration):**
- ✅ 3 use cases working
- ✅ UI fully integrated
- ✅ Production deployment successful

---

## 6. Dependencies

### 6.1 External Dependencies

- **mcp-agent:** Latest stable version (0.2.5+)
- **Kernel APIs:** Available and documented
- **Supabase:** Database access configured
- **OpenAI API:** API key and quota

### 6.2 Internal Dependencies

- **Frontend Team:** UI components ready by Week 8
- **DevOps Team:** Infrastructure ready by Week 2
- **QA Team:** Test cases ready by Week 3

---

## 7. Deliverables Checklist

### 7.1 Code Deliverables

- [ ] Core runtime (`core/`)
- [ ] MCP tool registry (`core/registry/`)
- [ ] Session management (`core/session/`)
- [ ] Permission checking (`core/permissions/`)
- [ ] Audit logging (`core/audit/`)
- [ ] Domain MCPs (`mcp/domain/`)
- [ ] Cluster MCPs (`mcp/cluster/`)
- [ ] Cell MCPs (`mcp/cell/`)
- [ ] Kernel integration (`integration/kernel/`)
- [ ] UI integration (`integration/ui/`)

### 7.2 Documentation Deliverables

- [ ] API documentation
- [ ] MCP tool catalog
- [ ] Deployment guide
- [ ] Operations runbook
- [ ] User guide

### 7.3 Testing Deliverables

- [ ] Unit test suite (80% coverage)
- [ ] Integration test suite
- [ ] End-to-end test suite
- [ ] Performance test results
- [ ] Security test results

---

## 8. References

- **PRD-LYNX-001** - Master PRD (SSOT)
- **PRD-LYNX-003** - HYBRID BASIC Implementation Strategy
- **ADR-LYNX-001** - Architecture Decision Record
- **SRS-LYNX-001** - Software Requirements Specification
- **TSD-LYNX-001** - Technical Specification Document
- **SOP-LYNX-001** - Standard Operating Procedures

---

## 9. Approval & Sign-off

**Status:** DRAFT  
**Next Steps:**
1. Review by Lead Engineer
2. Review by Project Manager
3. Approval by Product Owner
4. Begin Phase 1 implementation

---

**End of Implementation Plan**

