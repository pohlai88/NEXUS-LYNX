<!-- BEGIN: AIBOS_MANAGED -->
| Field | Value |
|---|---|
| **Document ID** | PRD-LYNX-001 |
| **Document Type** | PRD |
| **Classification** | STANDARD |
| **Title** | MASTER PRD — LYNX AI: Kernel-Governed Artificial Intelligence for AI-BOS NexusCanon |
| **Status** | APPROVED |
| **Authority** | DERIVED |
| **Version** | 1.0.0 |
| **Owners** | `Founder`, `Chief Architect`, `Product Owner` |
| **Checksum (SHA-256)** | `e94d27104994b8b34fafd584ca3689e9ffccb61fb14bd7e8383831b2fbefd40e` |
| **Updated** | 2026-01-01 |

<!-- END: AIBOS_MANAGED -->





# MASTER PRD — LYNX AI

**Kernel-Governed Artificial Intelligence for AI-BOS NexusCanon**

---

## 0. Document Control

* **Product Name:** Lynx AI
* **System:** AI-BOS NexusCanon
* **Document Type:** **MASTER PRD (SSOT)**
* **Audience:** Founder, Chief Architect, Product Owner, Kernel / Canon / Cell Designers
* **Scope:** Global (applies to all tenants, all domains)
* **Status:** Authoritative Reference

> This document supersedes all prior Lynx drafts.
> Any future Lynx capability must comply with this Master PRD.

---

## 1. Executive Definition (Lock This In)

### 1.1 What Lynx AI Is

**Lynx AI is the intelligence layer of NexusCanon itself.**

It is:

* tenant-aware
* permission-bound
* schema-aware
* workflow-aware
* audit-first
* extensible through controlled tools

Lynx AI **does not exist outside NexusCanon**.

---

### 1.2 What Lynx AI Is NOT

Lynx AI is **not**:

* a chatbot plugin
* a free-roaming AI
* an external SaaS
* an autonomous agent
* a replacement for governance

**Clarification:**
While Lynx AI is powered by a large language model and is capable of broad reasoning, explanation, and synthesis, it is intentionally *not* designed to be a free-roaming or autonomous system.

Lynx's intelligence is broad by design; its authority is narrow by governance.

This ensures flexibility of thought without compromising Kernel control, tenant safety, or audit integrity.

---

## 2. Core Product Vision

> **Vision Statement**
> Lynx AI ensures that every user of NexusCanon is *guided toward correct, auditable, and optimal system behavior* — automatically, consistently, and safely.

Lynx does not "think for the user".
Lynx **thinks with the system**.

---

## 3. First-Principle Design Laws (Non-Negotiable)

These are **constitutional rules**. Breaking any of these is a system violation.

### Law 1 — Kernel Supremacy

Lynx obeys **Kernel SSOT**:

* metadata
* schema
* permissions
* lifecycle rules

Lynx never invents truth.

---

### Law 2 — Tenant Absolutism

Lynx is **strictly tenant-scoped**:

* no cross-tenant visibility
* no shared memory
* no implicit inheritance

---

### Law 3 — Tool-Only Action

Lynx **cannot act directly** on systems.

All actions must go through **MCP tools** (documented, versioned, governed).

If a capability is not a tool → **Lynx cannot do it**.

---

### Law 4 — Suggest First, Execute with Consent

Default mode = **Suggest**
Execution requires:

* correct role
* correct scope
* correct risk level
* explicit approval (if required)

---

### Law 5 — Audit Is Reality

If an action is not logged, it is considered **not happened**.

---

## 4. Conceptual Architecture (Mental Model)

```
User
  ↓
Lynx AI (Reasoning + Advice)
  ↓
MCP Tool Registry (Allowed Capabilities)
  ↓
Kernel / Canon / Cell APIs
  ↓
Supabase / System State
```

Lynx **never bypasses** the tool layer.

---

## 5. MCP Explained as Lynx Documentation (Plain Language)

### 5.1 What MCP Means in NexusCanon

**MCP = Machine-Callable Procedures**

In NexusCanon terms:

> MCP is the **formal contract that defines what Lynx is allowed to do**.

Each MCP tool is:

* explicit
* typed
* permissioned
* auditable
* versioned

---

### 5.2 Why MCP Is Mandatory for Lynx

Without MCP:

* AI can drift
* behavior becomes unpredictable
* governance breaks
* audit fails

With MCP:

* Lynx becomes **stable, safe, enterprise-grade**

---

### 5.3 MCP vs Traditional APIs

| Aspect      | API         | MCP       |
| ----------- | ----------- | --------- |
| Caller      | Human / App | AI        |
| Safety      | Assumed     | Enforced  |
| Schema      | Optional    | Mandatory |
| Permissions | External    | Built-in  |
| Audit       | Partial     | Required  |

---

## 6. MCP Taxonomy — **This Is the Core of Your Question**

### **Answer: Three Layers. Exactly.**

No more. No less.

---

## 7. MCP Layer 1 — **Domain MCPs**

**(Strategic / Advisory / Read-Heavy)**

### Purpose

* Provide **context**
* Provide **understanding**
* Enable **advice**

### Characteristics

* Mostly READ
* Low risk
* Broad scope
* No side effects

### Examples

* `finance.domain.health.read`
* `vendor.domain.summary.read`
* `workflow.domain.inefficiency.scan`
* `compliance.domain.risk.explain`

### Lynx Usage

> "I see that payments were made without VPM records. This creates audit risk."

---

## 8. MCP Layer 2 — **Cluster MCPs**

**(Operational / Draft-Creating)**

### Purpose

* Prepare actions
* Create drafts
* Assemble workflows

### Characteristics

* CREATE / UPDATE (draft)
* Medium risk
* Approval-aware

### Examples

* `document.cluster.request.draft`
* `workflow.cluster.approval.draft`
* `portal.cluster.scaffold.draft`
* `policy.cluster.revision.draft`

### Lynx Usage

> "I've prepared a document request batch. Please review before publishing."

---

## 9. MCP Layer 3 — **Cell MCPs**

**(Execution / Atomic Actions)**

### Purpose

* Perform **exact system mutations**

### Characteristics

* Narrow scope
* Single responsibility
* Strict permission checks
* Often irreversible (soft-delete only)

### Examples

* `document.cell.request.create`
* `workflow.cell.publish`
* `vpm.cell.payment.record`
* `portal.cell.enable`

### Lynx Usage

> "This action will create live document requests. Confirm?"

---

## 10. MCP Count Guidance (Practical Numbers)

### Initial v1 Recommendation

| Layer        | Approx Count |
| ------------ | ------------ |
| Domain MCPs  | 10–15        |
| Cluster MCPs | 15–25        |
| Cell MCPs    | 30–50        |

Do **not** overbuild.
MCPs grow organically as Cells grow.

---

## 11. Tenant Customisation AI (Critical Section)

### 11.1 Principle

Tenants may customise:

* schema
* workflows
* policies
* fields

**Lynx must understand customisation, not break it.**

---

### 11.2 How Lynx Handles Tenant Customisation

Lynx:

1. Reads **tenant metadata**
2. Reads **custom schema extensions**
3. Adjusts reasoning accordingly
4. Never assumes defaults if overridden

---

### 11.3 Customisation-Aware Advice

Example:

Tenant A:

* manual approval disabled
* cryptographic timestamp enabled

Tenant B:

* hybrid approval

Lynx responses **must differ**, even for the same question.

---

## 12. Lynx Functional Modes

### Mode 1 — Conversational

* explain
* guide
* teach

### Mode 2 — Advisory

* detect inefficiencies
* recommend better system usage

### Mode 3 — Drafting

* prepare workflows
* assemble requests
* generate configurations

### Mode 4 — Execution (Controlled)

* perform approved actions via MCP

---

## 13. Canonical Use Cases (Authoritative)

These are **foundational**, not optional.

1. Document Request Assistant
2. Workflow Optimisation Advisor
3. Financial Discipline Coach (VPM)
4. Customer Portal Scaffolder
5. Design System & Brand Assistant

Any future Lynx feature must map to one of these patterns.

---

## 14. Governance & Risk Model

### Risk Levels

* **Low:** Read, explain, suggest
* **Medium:** Draft, prepare, assemble
* **High:** Publish, record payment, change permissions

Execution matrix:

| Risk   | Approval          |
| ------ | ----------------- |
| Low    | None              |
| Medium | Role-based        |
| High   | Explicit approval |

---

## 15. Success Criteria (System-Level)

* Users rely on Lynx instead of tribal knowledge
* Reduction in manual / paper workflows
* Increase in correct feature usage (VPM, workflows, portals)
* Zero unauthorised AI execution
* Full audit traceability

---

## 16. Explicit Non-Goals (Locked)

* Autonomous payments
* Self-modifying governance
* Cross-tenant intelligence
* Black-box AI behavior

---

## 17. Strategic Positioning (Final Lock)

> **ChatGPT answers questions.**
> **Palantir runs enterprises.**
> **Lynx governs how NexusCanon is used.**

---

## 18. Closing Authority Statement

This **Master PRD – Lynx AI** defines:

* product intent
* architectural boundaries
* governance laws
* MCP taxonomy
* tenant customisation handling

Any implementation, feature, or experiment that contradicts this document is **invalid by design**.

---

## 19. Cognitive vs Operational Boundary (Constitutional Rule)

### 19.1 Definition

Lynx AI is powered by a Large Language Model (LLM) and therefore possesses **broad cognitive capability**.
However, Lynx AI is intentionally designed with **strict operational constraint**.

This boundary is **fundamental** to the safety, scalability, and enterprise-readiness of NexusCanon.

---

### 19.2 Cognitive Freedom (What Lynx May Think)

Lynx AI **is allowed unrestricted reasoning**, including but not limited to:

* Understanding ambiguous or incomplete human intent
* Reasoning across domains (finance, workflow, compliance, UX, governance)
* Explaining system concepts and consequences
* Detecting inefficiencies, risks, and anti-patterns
* Proposing alternatives and optimisations
* Generating drafts, plans, explanations, and recommendations
* Teaching users how NexusCanon *should* be used

Cognitive freedom is required to:

* unlock LLM value,
* avoid brittle rule engines,
* support evolving tenant customisation.

**No artificial restriction shall be imposed on Lynx's reasoning capability.**

---

### 19.3 Operational Constraint (What Lynx May Do)

Despite cognitive freedom, Lynx AI **has no inherent authority**.

Lynx **may not**:

* mutate system state directly,
* access databases freely,
* execute arbitrary logic,
* bypass Kernel governance,
* exceed tenant or user permissions,
* perform unlogged actions.

All operational actions **must**:

1. Be executed through Kernel-approved MCP tools
2. Pass role + scope checks
3. Respect risk classification
4. Be recorded in the audit log

> **If an action is not available as an MCP tool, Lynx is incapable of performing it.**

---

### 19.4 Constitutional Statement

> **Lynx AI may think freely.
> Lynx AI may act only by permission.**

This statement is binding across all domains, tenants, and future implementations.

---

## 20. Risk Classification Model

All MCP tools are classified into **three immutable risk levels**.

### 20.1 Risk Levels

| Risk Level | Description                                    | Examples                                 |
| ---------- | ---------------------------------------------- | ---------------------------------------- |
| **Low**    | Read-only or explanatory actions               | summaries, explanations, health scans    |
| **Medium** | Draft or preparatory actions                   | document drafts, workflow proposals      |
| **High**   | State-changing or compliance-impacting actions | publishing workflows, recording payments |

---

## 21. Execution Authorization Matrix

| Risk Level | Execution Rule                                 |
| ---------- | ---------------------------------------------- |
| **Low**    | Immediate                                      |
| **Medium** | Role + Scope required                          |
| **High**   | Explicit approval required (human-in-the-loop) |

> **Approval requirements are enforced by Kernel policy, not by Lynx logic.**

Lynx **never self-approves**.

---

## 22. Failure & Refusal Behavior (Required)

If Lynx cannot act due to constraint, it **must**:

1. Explain *why* execution is blocked
2. Suggest the correct alternative (draft, escalation, or manual action)
3. Record the refusal in the audit trail

Silent failure is prohibited.

---

**End of Master PRD**

