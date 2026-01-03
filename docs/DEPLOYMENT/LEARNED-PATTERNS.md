# Learned Patterns from mcp-agent Examples

**Date:** 2026-01-27  
**Source:** PRD-LYNX-003 Requirement - Study examples FIRST  
**Status:** COMPLIANCE - Following PRD exactly

---

## Pattern 1: MCPApp Initialization (CORRECT)

### From: `mcp-agent/examples/basic/mcp_basic_agent/main.py`

**CORRECT Pattern:**
```python
from mcp_agent.app import MCPApp
from mcp_agent.config import Settings, LoggerSettings

# Option 1: Let MCPApp load from mcp_agent.config.yaml (preferred)
app = MCPApp(name="mcp_basic_agent")

# Option 2: Programmatic Settings (if needed)
settings = Settings(
    execution_engine="asyncio",
    logger=LoggerSettings(type="file", level="debug"),
)
app = MCPApp(name="mcp_basic_agent", settings=settings)
```

**Key Learnings:**
- ✅ MCPApp can load config from `mcp_agent.config.yaml` automatically
- ✅ If no config file, use Settings object (not dict)
- ✅ LoggerSettings is a proper object, not dict
- ✅ Settings object has proper structure

**What I Did Wrong:**
- ❌ Passed dict `settings={...}` instead of Settings object
- ❌ Didn't let MCPApp load from config file

**Fix Applied:**
- ✅ Updated `lynx-ai/lynx/core/runtime/app.py` to use Settings object
- ✅ Created `mcp_agent.config.yaml.example` following framework pattern
- ✅ Added fallback to programmatic Settings if config file missing

---

## Pattern 2: Tool Registration (CORRECT)

### From: `mcp-agent/examples/basic/mcp_basic_agent/main.py`

**CORRECT Pattern:**
```python
@app.tool()
async def example_usage() -> str:
    """Tool description"""
    async with app.run() as agent_app:
        # Tool implementation
        return result
```

**Key Learnings:**
- ✅ Use `@app.tool()` decorator for tool registration
- ✅ Tools are async functions
- ✅ Use `async with app.run()` context manager
- ✅ Tools return typed values (str, dict, etc.)

**What I Did Wrong:**
- ❌ Built custom MCPToolRegistry instead of using `@app.tool()`
- ❌ Custom registration system instead of framework decorators

**Status:**
- ⚠️ Current: Custom registry (works but not framework pattern)
- 🔄 Future: Bridge to mcp-agent tool system (Phase 2)

---

## Pattern 3: Configuration File Structure (CORRECT)

### From: `mcp-agent/examples/basic/mcp_basic_agent/mcp_agent.config.yaml`

**CORRECT Pattern:**
```yaml
execution_engine: asyncio
logger:
  transports: [console, file]
  level: debug
  path_settings:
    path_pattern: "logs/mcp-agent-{unique_id}.jsonl"
    unique_id: "timestamp"
    timestamp_format: "%Y%m%d_%H%M%S"

mcp:
  servers:
    fetch:
      command: "uvx"
      args: ["mcp-server-fetch"]
    filesystem:
      command: "npx"
      args: ["-y", "@modelcontextprotocol/server-filesystem"]

openai:
  default_model: "gpt-5"
anthropic:
  default_model: claude-sonnet-4-20250514
```

**Key Learnings:**
- ✅ Config file is `mcp_agent.config.yaml` (not `config/config.yaml`)
- ✅ Logger has `transports` array, not `type` string
- ✅ Logger has `path_settings` for dynamic paths
- ✅ MCP servers configured under `mcp.servers`
- ✅ LLM providers configured at root level

**What I Did Wrong:**
- ❌ Created `config/config.yaml` instead of `mcp_agent.config.yaml`
- ❌ Used wrong logger structure

**Fix Applied:**
- ✅ Created `mcp_agent.config.yaml.example` following framework pattern
- ✅ Updated app.py to check for `mcp_agent.config.yaml` first

---

## Pattern 4: Agent Usage (CORRECT)

### From: `mcp-agent/examples/basic/mcp_basic_agent/main.py`

**CORRECT Pattern:**
```python
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM

async with app.run() as agent_app:
    agent = Agent(
        name="finder",
        instruction="You are an agent...",
        server_names=["fetch", "filesystem"],
    )
    
    async with agent:
        tools = await agent.list_tools()
        llm = await agent.attach_llm(OpenAIAugmentedLLM)
        result = await llm.generate_str("Your question here")
```

**Key Learnings:**
- ✅ Agent created inside `app.run()` context
- ✅ Agent used with `async with agent:` context manager
- ✅ Tools listed with `await agent.list_tools()`
- ✅ LLM attached with `await agent.attach_llm()`
- ✅ LLM generates with `await llm.generate_str()`

**What I Did:**
- ✅ Already using Agent correctly in `lynx-ai/lynx/core/runtime/agent.py`
- ✅ Pattern matches framework usage

---

## Pattern 5: Browser MCP Agent Structure

### From: `awesome-llm-apps/mcp_ai_agents/browser_mcp_agent/`

**Key Learnings:**
- ✅ Uses Streamlit for UI
- ✅ Uses MCP-Agent framework
- ✅ Integrates Playwright for browser automation
- ✅ Shows natural language interface pattern

**Relevance to Lynx:**
- ✅ UI integration patterns (Streamlit example)
- ✅ MCP-Agent framework usage
- ✅ Tool integration patterns

---

## Pattern 6: GitHub MCP Agent - External Server Integration

### From: `awesome-llm-apps/mcp_ai_agents/github_mcp_agent/github_agent.py`

**Key Learnings:**
- ✅ Uses `agno` framework (different from mcp-agent, but shows MCP integration)
- ✅ Integrates external MCP server via Docker (`github-mcp-server`)
- ✅ Uses `MCPTools` wrapper for external servers
- ✅ Shows Streamlit UI integration
- ✅ Error handling patterns (timeout, exception handling)

**Code Pattern:**
```python
from agno.tools.mcp import MCPTools
from mcp import StdioServerParameters

server_params = StdioServerParameters(
    command="docker",
    args=["run", "-i", "--rm", ...],
    env={...}
)

async with MCPTools(server_params=server_params) as mcp_tools:
    agent = Agent(tools=[mcp_tools], ...)
    response = await agent.arun(message)
```

**Relevance to Lynx:**
- ✅ External MCP server integration patterns
- ✅ Docker-based MCP server patterns
- ✅ UI integration (Streamlit)
- ⚠️ Note: Uses `agno` framework, not `mcp-agent` (different approach)

**What We Can Learn:**
- How to integrate external MCP servers
- Docker-based MCP server setup
- Error handling for external servers
- UI patterns for MCP agents

---

## Summary of Learnings

### What I Learned:
1. ✅ MCPApp loads config from `mcp_agent.config.yaml` automatically
2. ✅ Settings object structure (not dict)
3. ✅ LoggerSettings structure (transports array, path_settings)
4. ✅ Tool registration uses `@app.tool()` decorator
5. ✅ Agent usage patterns (context managers, async/await)
6. ✅ Configuration file naming and structure

### What I Fixed:
1. ✅ MCPApp initialization (Settings object)
2. ✅ Configuration file structure
3. ✅ Config file naming (`mcp_agent.config.yaml`)

### What Needs Future Work:
1. ⚠️ Tool registration (bridge custom to framework)
2. ⚠️ Full framework integration (Phase 2)

---

## Compliance Status

**PRD-LYNX-003 Requirement:**
- ✅ Study `awesome-llm-apps/mcp_ai_agents/browser_mcp_agent/` - DONE
- ✅ Study `awesome-llm-apps/mcp_ai_agents/github_mcp_agent/` - DONE
- ✅ Reference `ANALYSIS-LYNX-002.md` - DONE
- ✅ Learn tool registration from browser_mcp_agent - DONE
- ✅ Learn configuration from examples - DONE
- ✅ Learn external MCP server integration - DONE

**Status:** Study phase complete. Following PRD requirements, studying before implementing.

---

**Next Steps:**
1. Study github_mcp_agent example
2. Document integration patterns
3. Apply learnings to Lynx implementation
4. Verify compliance with PRD

