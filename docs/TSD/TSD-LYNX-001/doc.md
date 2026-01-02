<!-- BEGIN: AIBOS_MANAGED -->
| Field | Value |
|---|---|
| **Document ID** | TSD-LYNX-001 |
| **Document Type** | TSD |
| **Classification** | STANDARD |
| **Title** | Technical Specification Document — LYNX AI |
| **Status** | DRAFT |
| **Authority** | DERIVED |
| **Scope** | MULTI_TENANT_PRODUCTION_MVP |
| **Derived From** | `PRD-LYNX-001`, `PRD-LYNX-003`, `ADR-LYNX-001`, `SRS-LYNX-001` |
| **Version** | 1.0.0 |
| **Owners** | `Chief Architect`, `Lead Engineer` |
| **Created** | 2026-01-01 |
| **Updated** | 2026-01-01 |

<!-- END: AIBOS_MANAGED -->

# Technical Specification Document — LYNX AI

**Derived from:** PRD-LYNX-001, PRD-LYNX-003, ADR-LYNX-001, SRS-LYNX-001  
**Timeline:** 6-8 weeks  
**Status:** DRAFT

---

## 1. Introduction

### 1.1 Purpose

This Technical Specification Document (TSD) defines the **technical implementation details** for Lynx AI, including:
- System architecture
- Technology stack
- Component specifications
- API contracts
- Data models
- Integration patterns

### 1.2 Document Relationships

| Document | Relationship |
|----------|-------------|
| **PRD-LYNX-001** | Defines *what* to build (requirements) |
| **SRS-LYNX-001** | Defines *functional* requirements |
| **ADR-LYNX-001** | Defines *architectural* decisions |
| **TSD-LYNX-001** | Defines *technical* implementation (this document) |
| **SOP-LYNX-001** | Defines *operational* procedures |
| **IMPLEMENTATION-LYNX-001** | Defines *implementation* plan |

---

## 2. System Architecture

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface Layer                  │
│  (NexusCanon UI - React/Next.js)                        │
└────────────────────┬────────────────────────────────────┘
                      │ HTTP/REST
┌─────────────────────▼────────────────────────────────────┐
│                  Lynx AI Service Layer                    │
│  ┌────────────────────────────────────────────────────┐  │
│  │  mcp-agent Runtime                                  │  │
│  │  - MCPApp                                          │  │
│  │  - Agent                                           │  │
│  │  - AugmentedLLM                                    │  │
│  └────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Lynx Core Components                              │  │
│  │  - Session Manager (tenant-scoped)                 │  │
│  │  - MCP Tool Registry                               │  │
│  │  - Permission Checker                               │  │
│  │  - Risk Classifier                                 │  │
│  │  - Audit Logger                                    │  │
│  └────────────────────────────────────────────────────┘  │
└─────────────────────┬────────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
┌───────▼──────┐ ┌────▼────┐ ┌──────▼──────┐
│ Kernel APIs  │ │ LLM API │ │  Supabase   │
│ (SSOT)       │ │ (OpenAI)│ │  (Audit DB) │
└──────────────┘ └─────────┘ └─────────────┘
```

### 2.2 Component Architecture

```
lynx-ai/
├── core/
│   ├── runtime/           # mcp-agent integration
│   │   ├── app.py         # MCPApp initialization
│   │   ├── agent.py       # Agent configuration
│   │   └── llm.py         # LLM integration
│   ├── session/           # Session management
│   │   ├── manager.py     # Session manager
│   │   └── tenant.py      # Tenant isolation
│   ├── registry/          # MCP tool registry
│   │   ├── registry.py    # Tool registration
│   │   ├── validator.py   # Schema validation
│   │   └── classifier.py  # Risk classification
│   ├── permissions/       # Permission checking
│   │   ├── checker.py     # Permission checker
│   │   └── kernel.py      # Kernel API integration
│   └── audit/             # Audit logging
│       ├── logger.py      # Audit logger
│       └── storage.py     # Audit storage
├── mcp/
│   ├── domain/            # Domain MCPs (read-only)
│   │   ├── finance/
│   │   ├── vendor/
│   │   ├── workflow/
│   │   └── compliance/
│   ├── cluster/           # Cluster MCPs (drafts)
│   │   ├── document/
│   │   ├── workflow/
│   │   └── portal/
│   └── cell/              # Cell MCPs (execution)
│       ├── document/
│       ├── workflow/
│       └── vpm/
├── integration/
│   ├── kernel/            # Kernel SSOT integration
│   │   ├── metadata.py
│   │   ├── schema.py
│   │   └── permissions.py
│   └── ui/                # UI integration
│       └── api.py         # REST API endpoints
└── config/
    ├── config.yaml        # Application config
    └── secrets.yaml       # Secrets (gitignored)
```

---

## 3. Technology Stack

### 3.1 Core Framework

**mcp-agent** (lastmile-ai/mcp-agent)
- **Version:** Latest stable (0.2.5+)
- **License:** Apache 2.0
- **Purpose:** MCP runtime, agent framework, LLM integration
- **Installation:** `uv add "mcp-agent[openai]"`

### 3.2 Language & Runtime

- **Python:** 3.10+
- **Package Manager:** uv (recommended) or pip
- **Runtime:** AsyncIO (mcp-agent default)

### 3.3 LLM Provider

**Primary:** OpenAI
- **Model:** GPT-4o (default) or GPT-4o-mini (cost-effective)
- **API:** OpenAI Python SDK (via mcp-agent)
- **Fallback:** Anthropic Claude (via mcp-agent)

### 3.4 Data Validation

- **Zod (via Pydantic):** Input/output schema validation
- **Pydantic:** Python data validation

### 3.5 Database

- **Supabase:** Audit log storage
- **PostgreSQL:** Via Supabase

### 3.6 Configuration

- **YAML:** Configuration files
- **Environment Variables:** Secrets management

---

## 4. Component Specifications

### 4.1 Lynx Core Runtime

#### 4.1.1 MCPApp Initialization

**File:** `core/runtime/app.py`

```python
from mcp_agent.app import MCPApp
from lynx.core.session import SessionManager
from lynx.core.registry import MCPToolRegistry
from lynx.core.audit import AuditLogger

app = MCPApp(
    name="lynx",
    settings={
        "execution_engine": "asyncio",
        "logger": {
            "transports": ["console", "file"],
            "level": "info"
        }
    }
)

# Initialize core components
session_manager = SessionManager()
tool_registry = MCPToolRegistry()
audit_logger = AuditLogger()
```

---

#### 4.1.2 Agent Configuration

**File:** `core/runtime/agent.py`

```python
from mcp_agent.agents.agent import Agent
from mcp_agent.workflows.llm.augmented_llm_openai import OpenAIAugmentedLLM

async def create_lynx_agent(context: ExecutionContext) -> Agent:
    agent = Agent(
        name="lynx",
        instruction="""
        You are Lynx AI, the intelligence layer of NexusCanon.
        You guide users toward correct, auditable, and optimal system behavior.
        
        Rules:
        1. You may think freely and reason broadly
        2. You may act only through MCP tools
        3. You must respect tenant boundaries
        4. You must log all actions
        5. You must suggest first, execute with consent
        """,
        server_names=["lynx_mcp_server"]  # Our MCP server
    )
    return agent
```

---

### 4.2 MCP Tool Registry

#### 4.2.1 Tool Registration

**File:** `core/registry/registry.py`

```python
from typing import Dict, List
from pydantic import BaseModel
from zod import ZodSchema

class MCPTool:
    id: str
    name: str
    description: str
    layer: str  # "domain" | "cluster" | "cell"
    risk: str   # "low" | "medium" | "high"
    domain: str
    input_schema: ZodSchema
    output_schema: ZodSchema
    required_role: List[str]
    required_scope: List[str]
    handler: Callable

class MCPToolRegistry:
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
    
    def register(self, tool: MCPTool):
        """Register an MCP tool"""
        if tool.id in self.tools:
            raise ValueError(f"Tool {tool.id} already registered")
        self.tools[tool.id] = tool
    
    def get(self, tool_id: str) -> MCPTool:
        """Get a tool by ID"""
        if tool_id not in self.tools:
            raise ValueError(f"Tool {tool_id} not found")
        return self.tools[tool_id]
    
    def list_by_layer(self, layer: str) -> List[MCPTool]:
        """List tools by layer"""
        return [t for t in self.tools.values() if t.layer == layer]
```

---

#### 4.2.2 Tool Execution

**File:** `core/registry/executor.py`

```python
async def execute_tool(
    tool_id: str,
    input_data: dict,
    context: ExecutionContext
) -> dict:
    """Execute an MCP tool with full validation and audit"""
    
    # 1. Get tool from registry
    tool = registry.get(tool_id)
    
    # 2. Validate input
    validated_input = tool.input_schema.parse(input_data)
    
    # 3. Check permissions
    if not permission_checker.check(tool, context):
        audit_logger.log_refusal(context, tool, "insufficient_permissions")
        raise PermissionError("Insufficient permissions")
    
    # 4. Check risk level
    if tool.risk == "high" and not context.explicit_approval:
        audit_logger.log_refusal(context, tool, "approval_required")
        raise ApprovalRequiredError("Explicit approval required")
    
    # 5. Log execution start
    audit_logger.log_execution_start(context, tool, validated_input)
    
    # 6. Execute tool
    try:
        result = await tool.handler(validated_input, context)
        
        # 7. Validate output
        validated_output = tool.output_schema.parse(result)
        
        # 8. Log execution success
        audit_logger.log_execution_success(context, tool, validated_output)
        
        return validated_output
    except Exception as e:
        # 9. Log execution failure
        audit_logger.log_execution_failure(context, tool, str(e))
        raise
```

---

### 4.3 Session Management

#### 4.3.1 Session Manager

**File:** `core/session/manager.py`

```python
from typing import Optional
from uuid import uuid4

class Session:
    session_id: str
    user_id: str
    tenant_id: str
    user_role: str
    user_scope: List[str]
    created_at: datetime
    expires_at: datetime

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, Session] = {}
    
    def create_session(
        self,
        user_id: str,
        tenant_id: str,
        user_role: str,
        user_scope: List[str]
    ) -> Session:
        """Create a new tenant-scoped session"""
        session = Session(
            session_id=str(uuid4()),
            user_id=user_id,
            tenant_id=tenant_id,
            user_role=user_role,
            user_scope=user_scope,
            created_at=datetime.now(),
            expires_at=datetime.now() + timedelta(hours=8)
        )
        self.sessions[session.session_id] = session
        return session
    
    def get_session(self, session_id: str) -> Optional[Session]:
        """Get session by ID"""
        session = self.sessions.get(session_id)
        if session and session.expires_at > datetime.now():
            return session
        return None
```

---

### 4.4 Permission Checking

#### 4.4.1 Permission Checker

**File:** `core/permissions/checker.py`

```python
from lynx.integration.kernel import KernelAPI

class PermissionChecker:
    def __init__(self, kernel_api: KernelAPI):
        self.kernel_api = kernel_api
    
    async def check(
        self,
        tool: MCPTool,
        context: ExecutionContext
    ) -> bool:
        """Check if user has permission to execute tool"""
        
        # 1. Check role requirement
        if tool.required_role:
            if context.user_role not in tool.required_role:
                return False
        
        # 2. Check scope requirement
        if tool.required_scope:
            if not any(s in context.user_scope for s in tool.required_scope):
                return False
        
        # 3. Check Kernel permissions
        kernel_permission = await self.kernel_api.check_permission(
            user_id=context.user_id,
            tenant_id=context.tenant_id,
            action=tool.id,
            resource_type=tool.domain
        )
        
        return kernel_permission.allowed
```

---

### 4.5 Audit Logging

#### 4.5.1 Audit Logger

**File:** `core/audit/logger.py`

```python
from supabase import create_client
from typing import Dict, Any

class AuditLogger:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase = create_client(supabase_url, supabase_key)
    
    async def log_lynx_run(
        self,
        run_id: str,
        user_id: str,
        tenant_id: str,
        user_query: str,
        lynx_response: str
    ):
        """Log a Lynx Run (user interaction)"""
        self.supabase.table("lynx_runs").insert({
            "run_id": run_id,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "user_query": user_query,
            "lynx_response": lynx_response,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }).execute()
    
    async def log_tool_call(
        self,
        run_id: str,
        tool_id: str,
        user_id: str,
        tenant_id: str,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        risk_level: str,
        approved: bool
    ):
        """Log an MCP tool call"""
        self.supabase.table("audit_logs").insert({
            "run_id": run_id,
            "tool_id": tool_id,
            "user_id": user_id,
            "tenant_id": tenant_id,
            "input": input_data,
            "output": output_data,
            "risk_level": risk_level,
            "approved": approved,
            "timestamp": datetime.now().isoformat()
        }).execute()
    
    async def log_refusal(
        self,
        context: ExecutionContext,
        tool: MCPTool,
        reason: str
    ):
        """Log a refused/blocked action"""
        self.supabase.table("audit_logs").insert({
            "run_id": context.lynx_run_id,
            "tool_id": tool.id,
            "user_id": context.user_id,
            "tenant_id": context.tenant_id,
            "input": {},
            "output": {},
            "risk_level": tool.risk,
            "approved": False,
            "refused": True,
            "refusal_reason": reason,
            "timestamp": datetime.now().isoformat()
        }).execute()
```

---

## 5. MCP Tool Implementation

### 5.1 Domain MCP Example

**File:** `mcp/domain/finance/health_read.py`

```python
from mcp_agent.app import MCPApp
from pydantic import BaseModel
from lynx.core.registry import MCPTool
from lynx.integration.kernel import KernelAPI

app = MCPApp(name="lynx")

class FinanceHealthInput(BaseModel):
    period: str = "current_month"  # Optional

class FinanceHealthOutput(BaseModel):
    health_score: int
    status: str
    risks: List[str]
    recommendations: List[str]

@app.tool(
    id="finance.domain.health.read",
    name="Read Financial Health",
    description="Provides a summary of the company's financial health",
    layer="domain",
    risk="low",
    domain="finance"
)
async def finance_health_read(
    input: FinanceHealthInput,
    context: ExecutionContext
) -> FinanceHealthOutput:
    """Read financial health summary"""
    
    # 1. Read from Kernel API (tenant-scoped)
    kernel_api = KernelAPI(context.tenant_id)
    financial_data = await kernel_api.get_financial_summary(
        period=input.period
    )
    
    # 2. Analyze and generate summary
    health_score = calculate_health_score(financial_data)
    risks = identify_risks(financial_data)
    recommendations = generate_recommendations(financial_data)
    
    # 3. Return structured output
    return FinanceHealthOutput(
        health_score=health_score,
        status="good" if health_score > 80 else "needs_attention",
        risks=risks,
        recommendations=recommendations
    )
```

---

### 5.2 Cluster MCP Example

**File:** `mcp/cluster/document/request_draft.py`

```python
class DocumentRequestDraftInput(BaseModel):
    vendor_id: str
    document_types: List[str]  # ["PO", "GRN", "Invoice"]
    due_date: Optional[str]

class DocumentRequestDraftOutput(BaseModel):
    draft_id: str
    vendor_id: str
    requests: List[Dict]
    message: str
    status: str  # "draft"

@app.tool(
    id="document.cluster.request.draft",
    name="Draft Document Request",
    description="Creates a draft document request batch",
    layer="cluster",
    risk="medium",
    domain="document",
    required_role=["admin", "procurement_manager"]
)
async def document_request_draft(
    input: DocumentRequestDraftInput,
    context: ExecutionContext
) -> DocumentRequestDraftOutput:
    """Create a draft document request"""
    
    # 1. Validate vendor exists (tenant-scoped)
    kernel_api = KernelAPI(context.tenant_id)
    vendor = await kernel_api.get_vendor(input.vendor_id)
    
    # 2. Create draft (not executed)
    draft_id = str(uuid4())
    requests = [
        {
            "document_type": doc_type,
            "vendor_id": input.vendor_id,
            "due_date": input.due_date or calculate_due_date(doc_type)
        }
        for doc_type in input.document_types
    ]
    
    # 3. Generate vendor message
    message = generate_vendor_message(vendor, requests)
    
    # 4. Store draft (not published)
    await kernel_api.create_draft(
        draft_id=draft_id,
        type="document_request",
        data={
            "vendor_id": input.vendor_id,
            "requests": requests,
            "message": message
        }
    )
    
    return DocumentRequestDraftOutput(
        draft_id=draft_id,
        vendor_id=input.vendor_id,
        requests=requests,
        message=message,
        status="draft"
    )
```

---

### 5.3 Cell MCP Example

**File:** `mcp/cell/document/request_publish.py`

```python
class DocumentRequestPublishInput(BaseModel):
    draft_id: str

class DocumentRequestPublishOutput(BaseModel):
    request_ids: List[str]
    status: str  # "published"

@app.tool(
    id="document.cell.request.publish",
    name="Publish Document Request",
    description="Publishes a draft document request batch",
    layer="cell",
    risk="high",
    domain="document",
    required_role=["admin"],
    required_scope=["document.publish"]
)
async def document_request_publish(
    input: DocumentRequestPublishInput,
    context: ExecutionContext
) -> DocumentRequestPublishOutput:
    """Publish a draft document request (requires explicit approval)"""
    
    # 1. Check explicit approval (enforced by Kernel)
    if not context.explicit_approval:
        raise ApprovalRequiredError("High-risk action requires explicit approval")
    
    # 2. Get draft
    kernel_api = KernelAPI(context.tenant_id)
    draft = await kernel_api.get_draft(input.draft_id)
    
    # 3. Validate draft belongs to tenant
    if draft.tenant_id != context.tenant_id:
        raise PermissionError("Draft belongs to different tenant")
    
    # 4. Publish (execute)
    request_ids = await kernel_api.publish_document_requests(
        draft_id=input.draft_id,
        published_by=context.user_id
    )
    
    return DocumentRequestPublishOutput(
        request_ids=request_ids,
        status="published"
    )
```

---

## 6. Kernel Integration

### 6.1 Kernel API Client

**File:** `integration/kernel/client.py`

```python
import httpx
from typing import Dict, Any, Optional

class KernelAPI:
    def __init__(self, tenant_id: str, api_key: str):
        self.tenant_id = tenant_id
        self.api_key = api_key
        self.base_url = os.getenv("KERNEL_API_URL")
        self.client = httpx.AsyncClient()
    
    async def get_metadata(self, entity_type: str) -> Dict[str, Any]:
        """Read metadata from Kernel SSOT"""
        response = await self.client.get(
            f"{self.base_url}/metadata/{entity_type}",
            headers={
                "X-Tenant-Id": self.tenant_id,
                "Authorization": f"Bearer {self.api_key}"
            }
        )
        return response.json()
    
    async def get_schema(self, entity_type: str) -> Dict[str, Any]:
        """Read schema from Kernel SSOT"""
        response = await self.client.get(
            f"{self.base_url}/schema/{entity_type}",
            headers={
                "X-Tenant-Id": self.tenant_id,
                "Authorization": f"Bearer {self.api_key}"
            }
        )
        return response.json()
    
    async def check_permission(
        self,
        user_id: str,
        action: str,
        resource_type: str
    ) -> Dict[str, Any]:
        """Check permission via Kernel"""
        response = await self.client.post(
            f"{self.base_url}/permissions/check",
            json={
                "user_id": user_id,
                "tenant_id": self.tenant_id,
                "action": action,
                "resource_type": resource_type
            },
            headers={
                "Authorization": f"Bearer {self.api_key}"
            }
        )
        return response.json()
```

---

## 7. Data Models

### 7.1 Execution Context

```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ExecutionContext:
    # User & Tenant
    user_id: str
    tenant_id: str
    user_role: str
    user_scope: List[str]
    
    # Session
    session_id: str
    lynx_run_id: str
    
    # Kernel
    kernel_metadata: Dict[str, Any]
    tenant_customizations: Dict[str, Any]
    
    # Approval
    explicit_approval: Optional[bool] = False
    
    # Audit
    audit_logger: AuditLogger
```

---

### 7.2 Database Schema

#### 7.2.1 Lynx Runs Table

```sql
CREATE TABLE lynx_runs (
    run_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    user_query TEXT NOT NULL,
    lynx_response TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_lynx_runs_tenant ON lynx_runs(tenant_id);
CREATE INDEX idx_lynx_runs_user ON lynx_runs(user_id);
CREATE INDEX idx_lynx_runs_timestamp ON lynx_runs(timestamp);
```

#### 7.2.2 Audit Logs Table

```sql
CREATE TABLE audit_logs (
    audit_id UUID PRIMARY KEY,
    run_id UUID REFERENCES lynx_runs(run_id),
    tool_id VARCHAR(100) NOT NULL,
    user_id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    input JSONB NOT NULL,
    output JSONB,
    risk_level VARCHAR(10) NOT NULL,
    approved BOOLEAN NOT NULL,
    approved_by UUID,
    refused BOOLEAN DEFAULT FALSE,
    refusal_reason TEXT,
    timestamp TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_tenant ON audit_logs(tenant_id);
CREATE INDEX idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_tool ON audit_logs(tool_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
```

---

## 8. API Specifications

### 8.1 REST API Endpoints

#### 8.1.1 Chat Endpoint

```
POST /api/lynx/chat
Content-Type: application/json
Authorization: Bearer <token>
X-Tenant-Id: <tenant_id>

Request:
{
  "message": "What is our financial health?",
  "session_id": "optional-session-id"
}

Response:
{
  "run_id": "uuid",
  "response": "Our financial health score is 85...",
  "tool_calls": [
    {
      "tool_id": "finance.domain.health.read",
      "input": {},
      "output": {...}
    }
  ],
  "suggestions": [...],
  "drafts": []
}
```

#### 8.1.2 Tool Execution Endpoint

```
POST /api/lynx/tools/execute
Content-Type: application/json
Authorization: Bearer <token>
X-Tenant-Id: <tenant_id>

Request:
{
  "tool_id": "document.cluster.request.draft",
  "input": {
    "vendor_id": "vendor-123",
    "document_types": ["PO", "GRN"]
  },
  "approval_token": "optional-for-high-risk"
}

Response:
{
  "success": true,
  "result": {...},
  "audit_id": "uuid"
}
```

---

## 9. Configuration

### 9.1 Application Configuration

**File:** `config/config.yaml`

```yaml
execution_engine: asyncio

logger:
  transports: [console, file]
  level: info
  path: "logs/lynx.jsonl"

mcp:
  servers:
    lynx_mcp_server:
      command: "python"
      args: ["-m", "lynx.mcp.server"]

openai:
  default_model: gpt-4o
  api_key: "${OPENAI_API_KEY}"

kernel:
  api_url: "${KERNEL_API_URL}"
  api_key: "${KERNEL_API_KEY}"

supabase:
  url: "${SUPABASE_URL}"
  key: "${SUPABASE_KEY}"

tenant:
  isolation:
    enabled: true
    strict: true
```

---

## 10. Testing Specifications

### 10.1 Unit Test Structure

```python
# tests/test_mcp_tools/test_finance_health_read.py

import pytest
from lynx.mcp.domain.finance.health_read import finance_health_read
from lynx.core.registry import ExecutionContext

@pytest.mark.asyncio
async def test_finance_health_read():
    context = create_test_context(tenant_id="test-tenant")
    input_data = FinanceHealthInput(period="current_month")
    
    result = await finance_health_read(input_data, context)
    
    assert result.health_score >= 0
    assert result.health_score <= 100
    assert result.status in ["good", "needs_attention", "critical"]
    assert isinstance(result.risks, list)
```

---

## 11. Deployment Specifications

### 11.1 Environment Variables

```bash
# LLM
OPENAI_API_KEY=sk-...

# Kernel
KERNEL_API_URL=https://kernel.nexuscanon.com/api
KERNEL_API_KEY=...

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=...

# Application
LOG_LEVEL=info
ENVIRONMENT=production
```

---

## 12. References

- **PRD-LYNX-001** - Master PRD
- **PRD-LYNX-003** - Implementation Strategy
- **ADR-LYNX-001** - Architecture Decisions
- **SRS-LYNX-001** - Software Requirements
- **SOP-LYNX-001** - Standard Operating Procedures
- **IMPLEMENTATION-LYNX-001** - Implementation Plan

---

**End of TSD**

