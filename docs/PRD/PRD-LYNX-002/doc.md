<!-- BEGIN: AIBOS_MANAGED -->
| Field | Value |
|---|---|
| **Document ID** | PRD-LYNX-002 |
| **Document Type** | PRD |
| **Classification** | STANDARD |
| **Title** | LYNX AI — SHIP NOW: Fastest MCP Rollout Strategy |
| **Status** | DRAFT |
| **Authority** | DERIVED |
| **Version** | 1.0.0 |
| **Owners** | `Founder`, `Chief Architect`, `Product Owner` |
| **Derived From** | `PRD-LYNX-001` |
| **Updated** | 2026-01-01 |

<!-- END: AIBOS_MANAGED -->

# LYNX AI — SHIP NOW: Fastest MCP Rollout Strategy

**Derived from:** PRD-LYNX-001 (Master PRD)  
**Timeline:** 1-2 weeks  
**Goal:** Get working MCP tools in production ASAP

---

## Executive Summary

**SHIP NOW** is the fastest possible path to get Lynx AI working with MCP tools. This strategy prioritizes **speed over completeness**, focusing on proving the concept works and delivering immediate value.

**Key Principle:** Start with the simplest possible implementation, prove it works, then expand.

---

## Scope & Timeline

### Timeline: 1-2 Weeks

| Week | Phase | Deliverables |
|------|-------|--------------|
| **Week 1** | Foundation + Domain MCPs | 5-7 Domain MCPs working |
| **Week 2** | Kernel Integration + Polish | Connected to Kernel, basic UI |

### Scope: Minimal Viable

- ✅ **5-7 Domain MCPs** (read-only, advisory)
- ✅ **Basic Kernel integration** (read metadata)
- ✅ **Simple audit logging** (log to console/file)
- ✅ **Basic UI** (single "Ask Lynx" button)
- ⚠️ **No tenant isolation** (single tenant only)
- ⚠️ **No risk classification** (all tools low risk)
- ⚠️ **No approval gates** (suggestions only, no execution)

---

## Implementation Strategy

### Phase 1: Foundation (Days 1-2)

**Goal:** Get mcp-agent working with one tool

**Tasks:**
1. Install mcp-agent
2. Create minimal config
3. Create first Domain MCP tool (mock data)
4. Test with LLM

**Deliverable:** One working MCP tool that LLM can call

**Code Example:**
```python
from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM

app = MCPApp(name="lynx_ship_now")

@app.tool
async def finance_domain_health_read(period: str = "month") -> dict:
    """Read financial health summary"""
    return {
        "health_score": 85,
        "risks": ["Missing VPM records"],
        "recommendations": ["Use VPM for payments"]
    }

async def main():
    async with app.run():
        agent = Agent(
            name="lynx",
            instruction="You are Lynx AI. Provide advisory responses.",
            server_names=[],
        )
        await agent.register_tool(finance_domain_health_read)
        
        async with agent:
            llm = await agent.attach_llm(OpenAIAugmentedLLM)
            response = await llm.generate_str("What's our financial health?")
            print(response)
```

---

### Phase 2: Domain MCPs (Days 3-5)

**Goal:** 5-7 Domain MCPs working

**MCPs to Build:**

1. **Finance Domain:**
   - `finance.domain.health.read` - Financial health summary
   - `finance.domain.payment.gaps.read` - Missing payment records

2. **Vendor Domain:**
   - `vendor.domain.summary.read` - Vendor overview
   - `vendor.domain.documents.status.read` - Document compliance

3. **Workflow Domain:**
   - `workflow.domain.inefficiency.scan` - Detect inefficient workflows

4. **Compliance Domain:**
   - `compliance.domain.risk.explain` - Explain compliance risks

**All tools:**
- Read-only (no side effects)
- Mock data (prove MCP works)
- Simple return values (dict/string)

**Deliverable:** 5-7 Domain MCPs that LLM can call

---

### Phase 3: Kernel Integration (Days 6-8)

**Goal:** Replace mocks with real Kernel calls

**Tasks:**
1. Create simple Kernel client
2. Replace mock data with Kernel API calls
3. Add basic error handling
4. Test with real data

**Kernel Integration:**
```python
class SimpleKernelClient:
    """Minimal Kernel client for SHIP NOW"""
    
    async def finance_get_health(self, tenant_id: str) -> dict:
        # Call Kernel API
        response = await kernel_api.get(f"/finance/health/{tenant_id}")
        return response.json()
    
    async def vendor_get_summary(self, tenant_id: str, vendor_id: str) -> dict:
        # Call Kernel API
        response = await kernel_api.get(f"/vendor/{vendor_id}")
        return response.json()

# Update tool to use Kernel
@app.tool
async def finance_domain_health_read(period: str = "month") -> dict:
    """Read financial health from Kernel"""
    kernel = SimpleKernelClient()
    health = await kernel.finance_get_health(tenant_id="default")
    return health
```

**Deliverable:** Tools connected to Kernel, real data flowing

---

### Phase 4: Basic UI (Days 9-10)

**Goal:** Simple "Ask Lynx" interface

**UI Components:**
1. Single "Ask Lynx" button (global)
2. Chat interface (simple text input/output)
3. Show tool calls (what Lynx is doing)
4. Show responses (Lynx answers)

**No complex features:**
- ❌ No draft review
- ❌ No approval gates
- ❌ No audit trail UI
- ✅ Just ask, get answer

**Deliverable:** Working UI where users can ask Lynx questions

---

## What's Included

### ✅ Included (MVP)

1. **MCP Runtime**
   - mcp-agent foundation
   - Tool registration
   - LLM integration

2. **Domain MCPs (5-7 tools)**
   - Read-only advisory tools
   - Finance, Vendor, Workflow, Compliance domains

3. **Basic Kernel Integration**
   - Read metadata
   - Read data
   - Simple API calls

4. **Basic Audit**
   - Console/file logging
   - Tool call tracking
   - Simple audit trail

5. **Basic UI**
   - "Ask Lynx" button
   - Chat interface
   - Tool call visibility

---

## What's NOT Included (Deferred)

### ❌ Deferred to Later

1. **Tenant Isolation**
   - Single tenant only
   - No multi-tenant support
   - **Risk:** Data leakage between tenants

2. **Risk Classification**
   - All tools treated as low risk
   - No approval gates
   - **Risk:** No execution control

3. **Cluster MCPs (Drafts)**
   - No draft creation
   - Suggestions only
   - **Impact:** Can't create workflows/documents

4. **Cell MCPs (Execution)**
   - No execution capabilities
   - Read-only operations
   - **Impact:** Can't perform actions

5. **Advanced Audit**
   - No Lynx Run tracking
   - No replay capability
   - **Impact:** Limited audit trail

6. **Tenant Customisation**
   - No custom schema support
   - Default configurations only
   - **Impact:** One-size-fits-all

---

## Success Criteria

### Week 1 Success

- ✅ mcp-agent installed and running
- ✅ 5-7 Domain MCPs registered
- ✅ LLM can call tools successfully
- ✅ Tools return data (mock or real)

### Week 2 Success

- ✅ Tools connected to Kernel
- ✅ Real data flowing
- ✅ Basic UI working
- ✅ Users can ask questions and get answers

### Production Readiness

- ⚠️ **Single tenant only** (not multi-tenant ready)
- ⚠️ **Read-only operations** (no execution)
- ⚠️ **Basic audit** (not comprehensive)
- ✅ **Working MCP system** (proves concept)

---

## Risks & Mitigations

### Risk 1: Single Tenant Only

**Risk:** Data leakage if multiple tenants use system

**Mitigation:**
- Deploy per-tenant instance
- Or add tenant check in Week 3

### Risk 2: No Execution Control

**Risk:** Can't prevent unauthorized actions (but also can't perform any actions)

**Mitigation:**
- All tools are read-only (no execution)
- Add risk classification in next phase

### Risk 3: Basic Audit

**Risk:** Limited audit trail

**Mitigation:**
- Log all tool calls to file
- Upgrade audit system in next phase

---

## Migration Path to Full Implementation

**After SHIP NOW works:**

1. **Week 3:** Add tenant isolation
2. **Week 4:** Add risk classification
3. **Week 5-6:** Add Cluster MCPs (drafts)
4. **Week 7-9:** Add Cell MCPs (execution)
5. **Week 10-12:** Full audit system

**Or:** Use SHIP NOW as proof-of-concept, then build full implementation from scratch using lessons learned.

---

## Use Cases Supported

### ✅ Supported (SHIP NOW)

1. **Advisory Questions**
   - "What's our financial health?"
   - "What documents are missing from vendor X?"
   - "What workflows are inefficient?"

2. **Information Retrieval**
   - Read financial summaries
   - Read vendor status
   - Read workflow efficiency

### ❌ NOT Supported (Deferred)

1. **Document Request Assistant** - Needs Cluster MCPs
2. **Workflow Creation** - Needs Cluster MCPs
3. **Payment Recording** - Needs Cell MCPs
4. **Portal Setup** - Needs Cluster + Cell MCPs

---

## Technical Stack

### Core

- **mcp-agent** - MCP runtime
- **OpenAI/Anthropic** - LLM provider
- **Python** - Implementation language

### Integration

- **Kernel API** - Simple HTTP client
- **File/Console** - Audit logging

### UI

- **Simple React/Vue** - Basic chat interface
- **No complex state management** - Keep it simple

---

## Timeline Summary

| Phase | Days | Deliverable |
|-------|------|-------------|
| Foundation | 1-2 | One working MCP tool |
| Domain MCPs | 3-5 | 5-7 tools working |
| Kernel Integration | 6-8 | Real data flowing |
| Basic UI | 9-10 | Users can ask questions |
| **TOTAL** | **10 days** | **Working MVP** |

---

## Decision Criteria

**Choose SHIP NOW if:**

- ✅ Need to prove MCP concept works quickly
- ✅ Single tenant deployment acceptable
- ✅ Read-only operations sufficient
- ✅ Can defer full implementation
- ✅ Need quick win for stakeholders

**Do NOT choose SHIP NOW if:**

- ❌ Multi-tenant required immediately
- ❌ Need execution capabilities
- ❌ Need comprehensive audit
- ❌ Need all PRD laws enforced from day 1

---

## Next Steps

1. **Approve this PRD**
2. **Set up mcp-agent** (Day 1)
3. **Create first Domain MCP** (Day 1-2)
4. **Expand to 5-7 tools** (Days 3-5)
5. **Connect to Kernel** (Days 6-8)
6. **Build basic UI** (Days 9-10)
7. **Ship to production** (Week 2)

---

**End of PRD-LYNX-002 (SHIP NOW)**

