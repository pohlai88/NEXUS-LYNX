# Quick Start: Fast MCP Rollout for Lynx

**Goal:** Get MCP tools working in **1-2 days**, not weeks.

**Strategy:** Start with the simplest possible setup, prove it works, then expand.

---

## Fastest Path: 3 Steps to Working MCP

### Step 1: Minimal Setup (2-4 hours)

**Install mcp-agent:**

```bash
# Create new directory
mkdir lynx-mcp-quickstart
cd lynx-mcp-quickstart

# Install with uv (fastest)
uv init
uv add "mcp-agent[openai]"

# Or with pip
pip install mcp-agent[openai]
```

**Create minimal config:**

```yaml
# mcp_agent.config.yaml
execution_engine: asyncio
logger:
  transports: [console]
  level: info

mcp:
  servers: {}

openai:
  default_model: gpt-4o-mini  # Cheapest for testing
```

```yaml
# mcp_agent.secrets.yaml (gitignored)
openai:
  api_key: "${OPENAI_API_KEY}"
```

**Create first MCP tool (Domain layer - read-only):**

```python
# lynx_tools.py
from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from pydantic import BaseModel
from typing import Optional

app = MCPApp(name="lynx_quickstart")

# Simple Domain MCP Tool (Read-only, Low Risk)
class FinanceHealthRead(BaseModel):
    """Read financial health summary"""
    period: Optional[str] = "month"  # month, quarter, year

@app.tool
async def finance_domain_health_read(input: FinanceHealthRead) -> dict:
    """
    Domain MCP: Read financial health summary.
    Risk: Low (read-only)
    Layer: Domain
    """
    # TODO: Replace with actual Kernel call
    # For now, return mock data to prove MCP works
    return {
        "health_score": 85,
        "risks": ["Missing VPM records detected"],
        "recommendations": [
            "Record payments via VPM",
            "Enable digital approval workflows"
        ],
        "period": input.period
    }

async def main():
    async with app.run():
        # Create agent with our tool
        agent = Agent(
            name="lynx_advisor",
            instruction="You are Lynx AI. Provide advisory responses based on NexusCanon data.",
            server_names=[],  # No external MCP servers yet
        )
        
        # Register our custom tool
        await agent.register_tool(finance_domain_health_read)
        
        async with agent:
            llm = await agent.attach_llm(OpenAIAugmentedLLM)
            
            # Test: Ask Lynx about financial health
            response = await llm.generate_str(
                "What's our financial health status?"
            )
            print(response)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

**Run it:**

```bash
export OPENAI_API_KEY="your-key-here"
uv run lynx_tools.py
```

**✅ You now have a working MCP tool!**

---

### Step 2: Add 3 More Domain MCPs (2-3 hours)

**Expand with more read-only tools:**

```python
# lynx_tools.py (expanded)

@app.tool
async def vendor_domain_summary_read(vendor_id: str) -> dict:
    """Domain MCP: Read vendor summary"""
    return {
        "vendor_id": vendor_id,
        "name": "Example Vendor",
        "status": "active",
        "documents_required": ["PO", "GRN", "Invoice"],
        "documents_missing": ["GRN"]
    }

@app.tool
async def workflow_domain_inefficiency_scan() -> dict:
    """Domain MCP: Scan for inefficient workflows"""
    return {
        "inefficiencies": [
            {
                "type": "paper_approval",
                "description": "Manual paper signatures detected",
                "recommendation": "Use cryptographic timestamp approval"
            }
        ]
    }

@app.tool
async def compliance_domain_risk_explain(area: str) -> dict:
    """Domain MCP: Explain compliance risks"""
    return {
        "area": area,
        "risks": [
            "Unrecorded payments break audit trail",
            "Missing documents create compliance gaps"
        ],
        "mitigations": [
            "Use VPM for all payments",
            "Request missing documents via Document Request Assistant"
        ]
    }

# Update agent to include all tools
async def main():
    async with app.run():
        agent = Agent(
            name="lynx_advisor",
            instruction="You are Lynx AI. Provide advisory responses.",
            server_names=[],
        )
        
        # Register all Domain MCPs
        await agent.register_tool(finance_domain_health_read)
        await agent.register_tool(vendor_domain_summary_read)
        await agent.register_tool(workflow_domain_inefficiency_scan)
        await agent.register_tool(compliance_domain_risk_explain)
        
        async with agent:
            llm = await agent.attach_llm(OpenAIAugmentedLLM)
            
            # Test multiple tools
            response = await llm.generate_str(
                "We're still signing paper approvals. What should we do?"
            )
            print(response)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

**✅ You now have 4 Domain MCPs working!**

---

### Step 3: Connect to Kernel (4-6 hours)

**Replace mocks with real Kernel calls:**

```python
# kernel_client.py
class KernelClient:
    """Simple Kernel client (replace with actual implementation)"""
    
    async def finance_get_health(self, tenant_id: str, period: str) -> dict:
        # Call actual Kernel API
        # For now, placeholder
        pass
    
    async def vendor_get_summary(self, tenant_id: str, vendor_id: str) -> dict:
        # Call actual Kernel API
        pass

# Update tools to use Kernel
@app.tool
async def finance_domain_health_read(
    input: FinanceHealthRead,
    context: ExecutionContext  # Add context injection
) -> dict:
    """Domain MCP: Read financial health from Kernel"""
    kernel = context.kernel_client
    tenant_id = context.tenant_id
    
    # Real Kernel call
    health = await kernel.finance_get_health(tenant_id, input.period)
    
    # Audit log
    await context.audit_logger.log({
        "tool": "finance.domain.health.read",
        "tenant_id": tenant_id,
        "input": input.dict(),
        "result": health
    })
    
    return health
```

**✅ You now have MCP tools connected to Kernel!**

---

## Even Faster: Copy-Paste Template

**Single-file template you can run immediately:**

```python
# quickstart_lynx.py
"""
Fastest MCP Rollout - Copy, paste, run.
Replace mocks with Kernel calls when ready.
"""
import asyncio
from mcp_agent.app import MCPApp
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM
from pydantic import BaseModel
from typing import Optional

app = MCPApp(name="lynx_quickstart")

# ============================================
# DOMAIN MCPs (Read-only, Low Risk)
# ============================================

class FinanceHealthInput(BaseModel):
    period: Optional[str] = "month"

@app.tool
async def finance_domain_health_read(input: FinanceHealthInput) -> dict:
    """Read financial health summary"""
    return {
        "health_score": 85,
        "risks": ["Missing VPM records"],
        "recommendations": ["Use VPM for payments"]
    }

@app.tool
async def vendor_domain_summary_read(vendor_id: str) -> dict:
    """Read vendor summary"""
    return {
        "vendor_id": vendor_id,
        "documents_missing": ["GRN", "Invoice"]
    }

@app.tool
async def workflow_domain_inefficiency_scan() -> dict:
    """Scan for inefficient workflows"""
    return {
        "inefficiencies": [{
            "type": "paper_approval",
            "recommendation": "Use cryptographic timestamp"
        }]
    }

# ============================================
# MAIN
# ============================================

async def main():
    async with app.run():
        agent = Agent(
            name="lynx_advisor",
            instruction="You are Lynx AI. Provide advisory responses about NexusCanon.",
            server_names=[],
        )
        
        # Register all tools
        await agent.register_tool(finance_domain_health_read)
        await agent.register_tool(vendor_domain_summary_read)
        await agent.register_tool(workflow_domain_inefficiency_scan)
        
        async with agent:
            llm = await agent.attach_llm(OpenAIAugmentedLLM)
            
            # Test
            response = await llm.generate_str(
                "What's our financial health and what should we improve?"
            )
            print("\n=== Lynx Response ===")
            print(response)

if __name__ == "__main__":
    asyncio.run(main())
```

**Run it:**

```bash
export OPENAI_API_KEY="your-key"
uv run quickstart_lynx.py
```

**✅ Working MCP in 5 minutes!**

---

## Fast Expansion Path

### Day 1: Domain MCPs (Read-only)
- ✅ 4-5 Domain MCPs working
- ✅ Mock data (proves MCP works)
- ✅ Can answer advisory questions

### Day 2: Connect to Kernel
- ✅ Replace mocks with Kernel calls
- ✅ Add tenant scoping
- ✅ Add basic audit logging

### Week 1: Add Cluster MCPs (Drafts)
- ✅ 3-5 Cluster MCPs (draft creation)
- ✅ Medium risk classification
- ✅ Role-based approval

### Week 2: Add Cell MCPs (Execution)
- ✅ 3-5 Cell MCPs (execution)
- ✅ High risk classification
- ✅ Explicit approval gates

---

## Key Principles for Fast Rollout

1. **Start with mocks** - Prove MCP works first, then connect to Kernel
2. **Domain MCPs first** - Read-only, no side effects, easiest to test
3. **One tool at a time** - Get one working, then add more
4. **Copy-paste friendly** - Use templates, not complex abstractions
5. **Test immediately** - Run after each tool addition

---

## Common Issues & Quick Fixes

### Issue: "Tool not found"
**Fix:** Make sure you `register_tool()` before using agent

### Issue: "No response from LLM"
**Fix:** Check `OPENAI_API_KEY` is set correctly

### Issue: "Import errors"
**Fix:** Make sure `mcp-agent` is installed: `uv add mcp-agent[openai]`

### Issue: "Tool not being called"
**Fix:** Make tool description clear, LLM needs to understand when to use it

---

## Next Steps After Quick Start

1. **Replace mocks** - Connect to actual Kernel APIs
2. **Add tenant scoping** - Enforce tenant isolation
3. **Add audit logging** - Track all tool calls
4. **Add risk classification** - Low/Medium/High enforcement
5. **Add more tools** - Expand to 10-15 Domain MCPs

---

## Timeline: Fastest Possible

| Phase | Time | What You Get |
|-------|------|--------------|
| **Setup** | 30 min | mcp-agent installed, config ready |
| **First Tool** | 1 hour | One Domain MCP working |
| **4 Tools** | 3 hours | 4 Domain MCPs working |
| **Kernel Connect** | 4 hours | Real data from Kernel |
| **10 Tools** | 1 day | Full Domain layer working |

**Total: 1-2 days to working MCP system**

---

## Why This Is Fast

1. **mcp-agent handles complexity** - MCP protocol, LLM integration, tool calling
2. **Start simple** - Domain MCPs are read-only, easiest to build
3. **Mock first** - Prove concept before connecting to Kernel
4. **Incremental** - Add one tool at a time, test immediately
5. **No over-engineering** - Simple functions, not complex frameworks

---

**End of Quick Start Guide**

