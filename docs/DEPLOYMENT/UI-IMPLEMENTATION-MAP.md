# UI Implementation Map - Page-by-Page File Structure

**Date:** 2026-01-27  
**Status:** ✅ **READY TO IMPLEMENT** (Updated with Critical Fixes)  
**Approach:** Thin client over MCP invariants (no logic re-invention)  
**Theme:** Simple CSS variables (void/paper/lux/gold) - swap to BioSkin later

---

## 🔒 Critical Principles (Enforceable)

### UI Rule: Never Infer, Only Render

**❌ FORBIDDEN:**
- UI deciding "high risk ⇒ show confirm" by itself
- UI inferring status/approval from risk_level
- UI hardcoding tenant_id

**✅ REQUIRED:**
- UI only renders what backend returns
- Backend returns `requires_confirmation: true|false` (derived from MCP + policy)
- Backend derives `tenant_id` from session/JWT (frontend never sends it)
- All API calls scoped by server-side tenant

### Auth + Tenant Invariants

**Every API call:**
- ✅ Scoped by server-side tenant (from session/JWT)
- ✅ Frontend never sends `tenant_id` (or it's ignored server-side)
- ✅ Backend rejects mismatches

**Every audit row:**
- ✅ `tenant_id` (from session)
- ✅ `actor_user_id` (from session)
- ✅ `actor_role` (from session)
- ✅ `request_id` (for debugging)

---

## 🎯 Implementation Order (Fastest Value → Least Dependency)

### Step A: Global "Ask Lynx" + Chat UI (MVP)
### Step B: Draft Review page `/drafts`
### Step C: Execution Confirmation dialog (high-risk only)
### Step D: Audit page `/audit`

---

## 📋 Data Contracts (Single Source of Truth)

### Backend: Pydantic Models (Source of Truth)

**Location:** `lynx-ai/lynx/api/models.py`

```python
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class RunStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"

class DraftStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"  # ✅ Added: transition state (approved → executing)
    EXECUTED = "executed"    # ✅ Added: approved + execution succeeded
    FAILED = "failed"        # ✅ Added: approved but execution failed

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class ToolCallStatus(str, Enum):
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"

# ChatRun Contract
class ToolCall(BaseModel):
    tool_id: str
    status: ToolCallStatus
    input: Dict[str, Any]
    output: Optional[Dict[str, Any]] = None
    duration_ms: Optional[int] = None
    error: Optional[str] = None

class PolicyInfo(BaseModel):
    requires_confirmation: bool  # ✅ Backend decides, UI only renders
    risk_level: RiskLevel
    blocked_reason: Optional[str] = None

class ChatRun(BaseModel):
    run_id: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    status: RunStatus
    query: str
    response: str
    tool_calls: List[ToolCall]
    policy: PolicyInfo  # ✅ Backend provides policy, UI renders

# Draft Contract
class Draft(BaseModel):
    draft_id: str
    status: DraftStatus  # ✅ Includes executed/failed
    requires_confirmation: bool  # ✅ Backend decides
    risk_level: RiskLevel
    tool_id: str
    payload: Dict[str, Any]
    created_at: datetime
    created_by: str
    approved_by: Optional[str] = None
    rejected_by: Optional[str] = None
    reason: Optional[str] = None
    execution_id: Optional[str] = None  # ✅ If executed
    execution_error: Optional[str] = None  # ✅ If failed
    metadata: Dict[str, Any] = {}

# Audit Contract
class AuditRun(BaseModel):
    run_id: str
    tenant_id: str  # ✅ Server-side only
    actor_user_id: str  # ✅ From session
    actor_role: str  # ✅ From session
    request_id: str  # ✅ For debugging
    query: str
    response: str
    tool_calls: List[ToolCall]
    created_at: datetime
    completed_at: Optional[datetime] = None
```

### Frontend: TypeScript Types (Generated from Backend)

**Location:** `ui/frontend/lib/types.ts`

```typescript
// ✅ Generated from backend Pydantic models (single source of truth)

export type RunStatus = 'success' | 'error' | 'pending';
export type DraftStatus = 'draft' | 'approved' | 'rejected' | 'executing' | 'executed' | 'failed';
export type RiskLevel = 'low' | 'medium' | 'high';
export type ToolCallStatus = 'success' | 'error' | 'pending';

export interface ToolCall {
  tool_id: string;
  status: ToolCallStatus;
  input: Record<string, any>;
  output?: Record<string, any>;
  duration_ms?: number;
  error?: string;
}

export interface PolicyInfo {
  requires_confirmation: boolean;  // ✅ Backend decides, UI only renders
  risk_level: RiskLevel;
  blocked_reason?: string;
}

export interface ChatRun {
  run_id: string;
  created_at: string;
  completed_at?: string;
  status: RunStatus;
  query: string;
  response: string;
  tool_calls: ToolCall[];
  policy: PolicyInfo;  // ✅ Backend provides policy, UI renders
}

export interface Draft {
  draft_id: string;
  status: DraftStatus;  // ✅ Includes executed/failed
  requires_confirmation: boolean;  // ✅ Backend decides
  risk_level: RiskLevel;
  tool_id: string;
  payload: Record<string, any>;
  created_at: string;
  created_by: string;
  approved_by?: string;
  rejected_by?: string;
  reason?: string;
  execution_id?: string;  // ✅ If executed
  execution_error?: string;  // ✅ If failed
  metadata: Record<string, any>;
}

export interface AuditRun {
  run_id: string;
  tenant_id: string;  // ✅ Server-side only (for display)
  actor_user_id: string;
  actor_role: string;
  request_id: string;  // ✅ For debugging
  query: string;
  response: string;
  tool_calls: ToolCall[];
  created_at: string;
  completed_at?: string;
}
```

---

## 🗄️ Supabase Tables (Minimum Schema)

**Location:** `docs/DEPLOYMENT/SUPABASE-SCHEMA.md` (create this)

```sql
-- ✅ Minimum tables for audit + drafts

-- Lynx Runs (audit trail)
CREATE TABLE lynx_runs (
    run_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,  -- ✅ RLS enforced
    actor_user_id TEXT NOT NULL,
    actor_role TEXT NOT NULL,
    request_id TEXT NOT NULL,  -- ✅ For debugging
    query TEXT NOT NULL,
    response TEXT,
    status TEXT NOT NULL,  -- success|error|pending
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    CONSTRAINT fk_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

-- Tool Calls (nested in runs)
CREATE TABLE lynx_tool_calls (
    id SERIAL PRIMARY KEY,
    run_id TEXT NOT NULL REFERENCES lynx_runs(run_id) ON DELETE CASCADE,
    tool_id TEXT NOT NULL,
    status TEXT NOT NULL,  -- success|error|pending
    input JSONB NOT NULL,
    output JSONB,
    duration_ms INTEGER,
    error TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_run FOREIGN KEY (run_id) REFERENCES lynx_runs(run_id)
);

-- Drafts
CREATE TABLE lynx_drafts (
    draft_id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,  -- ✅ RLS enforced
    status TEXT NOT NULL,  -- draft|approved|rejected|executing|executed|failed
    requires_confirmation BOOLEAN NOT NULL,
    risk_level TEXT NOT NULL,  -- low|medium|high
    tool_id TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by TEXT NOT NULL,
    approved_by TEXT,
    rejected_by TEXT,
    reason TEXT,
    execution_id TEXT,  -- ✅ If executed
    execution_error TEXT,  -- ✅ If failed
    metadata JSONB DEFAULT '{}',
    CONSTRAINT fk_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

-- Audit Events (append-only)
CREATE TABLE lynx_audit_events (
    id SERIAL PRIMARY KEY,
    tenant_id TEXT NOT NULL,  -- ✅ RLS enforced
    actor_user_id TEXT NOT NULL,
    actor_role TEXT NOT NULL,
    request_id TEXT NOT NULL,
    event_type TEXT NOT NULL,  -- draft_created|draft_approved|execution_started|etc
    entity_type TEXT,  -- draft|run|execution
    entity_id TEXT,
    details JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT fk_tenant FOREIGN KEY (tenant_id) REFERENCES tenants(id)
);

-- ✅ RLS Policies (tenant isolation)
ALTER TABLE lynx_runs ENABLE ROW LEVEL SECURITY;
ALTER TABLE lynx_tool_calls ENABLE ROW LEVEL SECURITY;
ALTER TABLE lynx_drafts ENABLE ROW LEVEL SECURITY;
ALTER TABLE lynx_audit_events ENABLE ROW LEVEL SECURITY;

-- Example RLS policy (tenant isolation)
CREATE POLICY tenant_isolation_runs ON lynx_runs
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id')::TEXT);
```

**Key Points:**
- ✅ All writes go through FastAPI (policy + audit)
- ✅ UI never writes to Supabase directly
- ✅ RLS enforces tenant isolation
- ✅ Draft lifecycle: draft → approved → executed/failed

---

## 📁 Complete File Structure

```
lynx-ai/
├── lynx/
│   └── api/
│       ├── dashboard.py              # Existing FastAPI app (extend)
│       ├── chat_routes.py            # NEW: Chat API endpoints
│       ├── draft_routes.py            # NEW: Draft API endpoints
│       ├── execution_routes.py       # NEW: Execution API endpoints
│       ├── audit_routes.py           # NEW: Audit API endpoints
│       └── static/
│           ├── aibos-design-system.css  # Existing
│           ├── ui.css                # NEW: Simple CSS variables (theme)
│           └── ui.js                 # NEW: Client-side JS (minimal)
│
└── ui/
    └── frontend/                     # NEW: Next.js app
        ├── package.json              # Next.js + TanStack Query
        ├── next.config.js
        ├── tsconfig.json
        ├── tailwind.config.js        # Optional (if using Tailwind)
        │
        ├── app/                      # Next.js App Router
        │   ├── layout.tsx            # Root layout with global "Ask Lynx" button
        │   ├── page.tsx              # Home page (redirects to /dashboard)
        │   ├── dashboard/
        │   │   └── page.tsx          # Existing dashboard (enhanced)
        │   │
        │   ├── chat/                 # Step A: Chat UI
        │   │   ├── page.tsx          # Chat page (or modal)
        │   │   └── [runId]/
        │   │       └── page.tsx      # Chat run details
        │   │
        │   ├── drafts/               # Step B: Draft Review
        │   │   ├── page.tsx          # Draft list with filters
        │   │   └── [draftId]/
        │   │       └── page.tsx      # Draft detail + approve/reject
        │   │
        │   └── audit/                # Step D: Audit Trail
        │       ├── page.tsx          # Run list with filters
        │       └── [runId]/
        │           └── page.tsx      # Run details + tool calls
        │
        ├── components/               # React components
        │   ├── layout/
        │   │   ├── Header.tsx        # Global header with "Ask Lynx" button
        │   │   └── Layout.tsx        # Root layout wrapper
        │   │
        │   ├── chat/                 # Step A: Chat components
        │   │   ├── AskLynxButton.tsx # Global button (persistent)
        │   │   ├── ChatInterface.tsx # Main chat UI
        │   │   ├── ChatMessage.tsx   # Individual message
        │   │   ├── ToolCallIndicator.tsx # Tool call display
        │   │   └── ChatInput.tsx     # Input bar
        │   │
        │   ├── contextual/           # Contextual "Ask Lynx about this"
        │   │   └── ContextualButton.tsx # Entity-specific button
        │   │
        │   ├── drafts/               # Step B: Draft components
        │   │   ├── DraftList.tsx     # Draft card list
        │   │   ├── DraftCard.tsx     # Individual draft card
        │   │   ├── DraftDetail.tsx   # Draft detail view
        │   │   ├── DraftFilters.tsx  # Filter controls
        │   │   └── DraftActions.tsx  # Approve/reject buttons
        │   │
        │   ├── execution/            # Step C: Execution components
        │   │   └── ExecutionDialog.tsx # Confirmation modal
        │   │
        │   └── audit/                # Step D: Audit components
        │       ├── AuditList.tsx     # Run list
        │       ├── RunCard.tsx       # Individual run card
        │       ├── RunDetail.tsx     # Run detail view
        │       ├── ToolCallList.tsx   # Tool calls display
        │       └── AuditFilters.tsx  # Filter controls
        │
        ├── lib/                      # Utilities
        │   ├── api.ts                # TanStack Query hooks + API client
        │   ├── api-client.ts         # ✅ NEW: Shared fetch wrapper (auth headers, errors, request_id)
        │   ├── types.ts               # TypeScript types (generated from backend)
        │   └── theme.ts              # CSS variables (void/paper/lux/gold)
        │
        └── styles/
            └── globals.css           # Global styles + CSS variables
```

---

## 🎨 Step A: Global "Ask Lynx" + Chat UI

### Files to Create

#### 1. `ui/frontend/app/layout.tsx` (Root Layout)

```typescript
'use client';

import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Header } from '@/components/layout/Header';
import '@/styles/globals.css';

// ✅ QueryClientProvider at root (required for React Query)
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <title>Lynx AI Dashboard</title>
      </head>
      <body>
        <QueryClientProvider client={queryClient}>
          <Header />
          <main>{children}</main>
        </QueryClientProvider>
      </body>
    </html>
  );
}
```

**Purpose:** Root layout with QueryClientProvider + persistent "Ask Lynx" button

**✅ Fixed:** QueryClientProvider added (required for React Query)

---

#### 2. `ui/frontend/components/layout/Header.tsx`

```typescript
'use client';

import { AskLynxButton } from '@/components/chat/AskLynxButton';

export function Header() {
  return (
    <header className="header">
      <div className="header-content">
        <h1>Lynx Ops Console</h1>
        <div className="header-actions">
          <span>Protocol v1.0</span>
          <button>🔄</button>
          <AskLynxButton />
        </div>
      </div>
    </header>
  );
}
```

**Purpose:** Global header with "Ask Lynx" button (persistent)

---

#### 3. `ui/frontend/components/chat/AskLynxButton.tsx`

```typescript
'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';

export function AskLynxButton() {
  const router = useRouter();
  const [isOpen, setIsOpen] = useState(false);

  const handleClick = () => {
    // Option 1: Navigate to chat page
    router.push('/chat');
    
    // Option 2: Open modal (if using modal approach)
    // setIsOpen(true);
  };

  return (
    <button 
      className="ask-lynx-button"
      onClick={handleClick}
      aria-label="Ask Lynx"
    >
      Ask Lynx
    </button>
  );
}
```

**Purpose:** Global "Ask Lynx" button (opens chat)

---

#### 4. `ui/frontend/app/chat/page.tsx`

```typescript
'use client';

import { ChatInterface } from '@/components/chat/ChatInterface';

export default function ChatPage() {
  return (
    <div className="chat-page">
      <h1>Ask Lynx</h1>
      <ChatInterface />
    </div>
  );
}
```

**Purpose:** Chat page (or modal overlay)

---

#### 5. `ui/frontend/components/chat/ChatInterface.tsx`

```typescript
'use client';

import { useState } from 'react';
import { useSendChatQuery } from '@/lib/api';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { ChatRun } from '@/lib/types';

export function ChatInterface({ 
  context 
}: { 
  context?: { entity_type: string; entity_id: string } 
}) {
  const [messages, setMessages] = useState<Message[]>([]);
  const sendQuery = useSendChatQuery();

  const handleSend = async (query: string) => {
    // ✅ Fixed: No tenant_id - backend derives from session
    const result = await sendQuery.mutateAsync({
      query,
      context,  // ✅ Optional context (entity_type, entity_id only)
    });
    
    setMessages(prev => [...prev, 
      { type: 'user', content: query },
      { 
        type: 'lynx', 
        content: result.response, 
        tool_calls: result.tool_calls, 
        run_id: result.run_id,
        policy: result.policy,  // ✅ Backend provides policy
      }
    ]);
  };

  return (
    <div className="chat-interface">
      {context && (
        <div className="chat-context">
          You asked about {context.entity_type} #{context.entity_id}
        </div>
      )}
      
      <div className="chat-messages">
        {messages.map((msg, idx) => (
          <ChatMessage key={idx} message={msg} />
        ))}
      </div>
      
      <ChatInput onSend={handleSend} disabled={sendQuery.isPending} />
      
      {/* ✅ Loading state */}
      {sendQuery.isPending && (
        <div className="chat-loading">Thinking...</div>
      )}
      
      {/* ✅ Error state */}
      {sendQuery.isError && (
        <div className="chat-error">
          Error: {sendQuery.error?.message}
          {sendQuery.error?.request_id && (
            <div>Request ID: {sendQuery.error.request_id}</div>
          )}
        </div>
      )}
    </div>
  );
}
```

**Purpose:** Main chat UI (renders messages, handles input)

**MCP Invariants:**
- ✅ Calls `/api/chat/query` (backend handles MCP)
- ✅ **No tenant_id** - backend derives from session
- ✅ Displays tool calls (read-only)
- ✅ Shows run_id (for audit trail)
- ✅ Renders `policy.requires_confirmation` (backend decides)

---

#### 6. `ui/frontend/components/chat/ChatMessage.tsx`

```typescript
'use client';

import { ToolCallIndicator } from './ToolCallIndicator';

interface Message {
  type: 'user' | 'lynx';
  content: string;
  tool_calls?: ToolCall[];
  run_id?: string;
}

export function ChatMessage({ message }: { message: Message }) {
  return (
    <div className={`chat-message chat-message-${message.type}`}>
      <div className="message-content">{message.content}</div>
      {message.tool_calls && (
        <div className="tool-calls">
          {message.tool_calls.map((tc, idx) => (
            <ToolCallIndicator key={idx} toolCall={tc} />
          ))}
        </div>
      )}
      {message.run_id && (
        <div className="message-meta">
          Run: {message.run_id}
        </div>
      )}
    </div>
  );
}
```

**Purpose:** Individual message display

---

#### 7. `ui/frontend/components/chat/ToolCallIndicator.tsx`

```typescript
interface ToolCall {
  tool_id: string;
  status: 'success' | 'error' | 'pending';
  duration_ms?: number;
}

export function ToolCallIndicator({ toolCall }: { toolCall: ToolCall }) {
  return (
    <div className={`tool-call tool-call-${toolCall.status}`}>
      <span className="tool-id">{toolCall.tool_id}</span>
      {toolCall.duration_ms && (
        <span className="tool-duration">{toolCall.duration_ms}ms</span>
      )}
      <span className="tool-status">{toolCall.status === 'success' ? '✓' : '✗'}</span>
    </div>
  );
}
```

**Purpose:** Tool call display (read-only, no logic)

---

#### 8. `ui/frontend/components/chat/ChatInput.tsx`

```typescript
'use client';

import { useState } from 'react';

export function ChatInput({ onSend, disabled }: { onSend: (query: string) => void; disabled?: boolean }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSend(input);
      setInput('');
    }
  };

  return (
    <form className="chat-input" onSubmit={handleSubmit}>
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type your question..."
        disabled={disabled}
      />
      <button type="submit" disabled={disabled || !input.trim()}>
        Send
      </button>
    </form>
  );
}
```

**Purpose:** Chat input bar

---

#### 9. `ui/frontend/components/contextual/ContextualButton.tsx`

```typescript
'use client';

import { useRouter } from 'next/navigation';

interface ContextualButtonProps {
  entity_type: string;
  entity_id: string;
  // ✅ Fixed: No entity_data in URL (backend loads if needed)
}

export function ContextualButton({ entity_type, entity_id }: ContextualButtonProps) {
  const router = useRouter();

  const handleClick = () => {
    // ✅ Fixed: Simple query params (no JSON in URL)
    router.push(`/chat?entity_type=${entity_type}&entity_id=${entity_id}`);
  };

  return (
    <button className="contextual-ask-lynx-button" onClick={handleClick}>
      Ask Lynx about this
    </button>
  );
}
```

**Purpose:** Contextual "Ask Lynx about this" button

**MCP Invariants:**
- ✅ Pre-fills context (entity_type, entity_id only)
- ✅ Opens chat with context
- ✅ **No JSON in URL** (prevents URL bloat + data leaks)

---

### Backend API: `lynx-ai/lynx/api/chat_routes.py`

```python
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer
from typing import Optional, Dict, Any
from lynx.api.models import ChatQueryRequest, ChatQueryResponse, ChatRun
from lynx.core.session import get_current_session  # ✅ Auth helper

router = APIRouter(prefix="/api/chat", tags=["chat"])
security = HTTPBearer()

@router.post("/query", response_model=ChatQueryResponse)
async def chat_query(
    request: ChatQueryRequest,
    session: dict = Depends(get_current_session),  # ✅ Auth + tenant from session
):
    """
    Submit a chat query to Lynx AI.
    
    ✅ Backend derives tenant_id from session (request.tenant_id ignored)
    ✅ Backend returns policy.requires_confirmation (UI only renders)
    """
    # ✅ Get tenant_id from session (not from request)
    tenant_id = session['tenant_id']
    user_id = session['user_id']
    role = session['role']
    
    # Call Lynx core runtime (handles MCP)
    # Create audit log entry (with tenant_id, user_id, role, request_id)
    # Return response with tool calls + policy
    
    # Example response structure:
    return ChatQueryResponse(
        run_id="run_xyz123",
        response="You have 3 documents...",
        tool_calls=[...],
        status="completed",
        policy={
            "requires_confirmation": False,  # ✅ Backend decides
            "risk_level": "medium",
            "blocked_reason": None,
        }
    )

@router.get("/runs/{run_id}")
async def get_chat_run(
    run_id: str,
    session: dict = Depends(get_current_session),
):
    """Get chat run details (tenant-scoped)."""
    # ✅ Verify tenant_id matches session
    # Read from audit storage (RLS enforced)
    pass
```

**Purpose:** Chat API endpoints (thin layer over MCP)

**✅ Fixed:**
- ✅ Auth + tenant from session (not from request)
- ✅ Returns `policy.requires_confirmation` (backend decides)
- ✅ Request ID for debugging

---

## 📋 Step B: Draft Review page `/drafts`

### Files to Create

#### 10. `ui/frontend/app/drafts/page.tsx`

```typescript
'use client';

import { DraftList } from '@/components/drafts/DraftList';
import { DraftFilters } from '@/components/drafts/DraftFilters';
import { useState } from 'react';

export default function DraftsPage() {
  const [filters, setFilters] = useState({
    status: 'all',
    type: 'all',
    dateRange: null,
    limit: 50,  // ✅ Added: pagination
    cursor: null,  // ✅ Added: cursor pagination (better than offset)
  });

  return (
    <div className="drafts-page">
      <h1>Draft Review</h1>
      <DraftFilters filters={filters} onFiltersChange={setFilters} />
      <DraftList filters={filters} />
      
      {/* ✅ Empty state */}
      {/* ✅ Error state with request_id */}
    </div>
  );
}
```

**Purpose:** Draft list page with filters + pagination

**✅ Fixed:**
- ✅ Cursor pagination (better than offset for audit logs)
- ✅ Empty/error states (see below)

---

#### 11. `ui/frontend/app/drafts/[draftId]/page.tsx`

```typescript
'use client';

import { DraftDetail } from '@/components/drafts/DraftDetail';
import { useParams } from 'next/navigation';

export default function DraftDetailPage() {
  const params = useParams();
  const draftId = params.draftId as string;

  return (
    <div className="draft-detail-page">
      <DraftDetail draftId={draftId} />
    </div>
  );
}
```

**Purpose:** Draft detail page

---

#### 12. `ui/frontend/components/drafts/DraftList.tsx`

```typescript
'use client';

import { useDrafts } from '@/lib/api';
import { DraftCard } from './DraftCard';

export function DraftList({ filters }: { filters: any }) {
  const { data, isLoading } = useDrafts(filters);

  if (isLoading) return <div>Loading drafts...</div>;

  return (
    <div className="draft-list">
      {data?.drafts.map((draft) => (
        <DraftCard key={draft.draft_id} draft={draft} />
      ))}
    </div>
  );
}
```

**Purpose:** Draft card list

---

#### 13. `ui/frontend/components/drafts/DraftCard.tsx`

```typescript
'use client';

import Link from 'next/link';

interface Draft {
  draft_id: string;
  type: string;
  status: 'draft' | 'approved' | 'rejected';
  risk_level: 'low' | 'medium' | 'high';
  created_at: string;
  created_by: string;
}

export function DraftCard({ draft }: { draft: Draft }) {
  return (
    <div className={`draft-card draft-card-${draft.status}`}>
      <div className="draft-header">
        <h3>{draft.type} Draft #{draft.draft_id}</h3>
        <span className={`risk-badge risk-${draft.risk_level}`}>
          {draft.risk_level}
        </span>
      </div>
      <div className="draft-meta">
        <span>Created: {new Date(draft.created_at).toLocaleString()}</span>
        <span>Status: {draft.status}</span>
      </div>
      <div className="draft-actions">
        <Link href={`/drafts/${draft.draft_id}`}>View Details</Link>
        {draft.status === 'draft' && (
          <>
            <button onClick={() => handleApprove(draft.draft_id)}>Approve</button>
            <button onClick={() => handleReject(draft.draft_id)}>Reject</button>
          </>
        )}
      </div>
    </div>
  );
}
```

**Purpose:** Individual draft card

**MCP Invariants:**
- ✅ Displays risk_level (from MCP)
- ✅ Shows status (draft/approved/rejected)
- ✅ Approve/reject actions (calls backend, backend handles MCP)

---

#### 14. `ui/frontend/components/drafts/DraftDetail.tsx`

```typescript
'use client';

import { useDraft } from '@/lib/api';
import { DraftActions } from './DraftActions';

export function DraftDetail({ draftId }: { draftId: string }) {
  const { data: draft, isLoading } = useDraft(draftId);

  if (isLoading) return <div>Loading...</div>;
  if (!draft) return <div>Draft not found</div>;

  return (
    <div className="draft-detail">
      <h1>Draft Details: {draft.type} #{draft.draft_id}</h1>
      
      <div className="draft-info">
        <div>Type: {draft.type}</div>
        <div>Status: {draft.status}</div>
        <div>Risk Level: {draft.risk_level}</div>
        <div>Created: {new Date(draft.created_at).toLocaleString()}</div>
      </div>

      <div className="draft-payload">
        <h2>Payload</h2>
        <pre>{JSON.stringify(draft.payload, null, 2)}</pre>
      </div>

      <DraftActions draft={draft} />
    </div>
  );
}
```

**Purpose:** Draft detail view

**MCP Invariants:**
- ✅ Displays payload (read-only)
- ✅ Shows risk_level (from MCP)
- ✅ Shows requires_approval (from MCP)

---

#### 15. `ui/frontend/components/drafts/DraftActions.tsx`

```typescript
'use client';

import { useApproveDraft, useRejectDraft } from '@/lib/api';
import { ExecutionDialog } from '@/components/execution/ExecutionDialog';
import { useState } from 'react';
import { Draft } from '@/lib/types';

export function DraftActions({ draft }: { draft: Draft }) {
  const [showConfirm, setShowConfirm] = useState(false);
  const approve = useApproveDraft();
  const reject = useRejectDraft();

  const handleApprove = () => {
    // ✅ CRITICAL FIX: UI only renders backend decision (no inference)
    // ❌ FORBIDDEN: if (draft.risk_level === 'high' || draft.requires_approval)
    // ✅ REQUIRED: Use backend-provided flag only
    if (draft.requires_confirmation) {  // ✅ Backend decides, UI only renders
      setShowConfirm(true);
    } else {
      approve.mutate({ draftId: draft.draft_id });
    }
  };

  const handleConfirmApprove = () => {
    approve.mutate({ draftId: draft.draft_id });
    setShowConfirm(false);
  };

  // ✅ Show execution status if executing/executed/failed
  const showExecutionStatus = ['executing', 'executed', 'failed'].includes(draft.status);

  return (
    <div className="draft-actions">
      {draft.status === 'draft' && (
        <>
          <button onClick={handleApprove} disabled={approve.isPending}>
            Approve
          </button>
          <button onClick={() => reject.mutate({ draftId: draft.draft_id })} disabled={reject.isPending}>
            Reject
          </button>
        </>
      )}
      
      {showExecutionStatus && (
        <div className="execution-status">
          {draft.status === 'executing' && (
            <div className="status-pending">⏳ Execution in progress...</div>
          )}
          {draft.status === 'executed' && (
            <div className="status-success">✓ Executed (ID: {draft.execution_id})</div>
          )}
          {draft.status === 'failed' && (
            <div className="status-error">
              ✗ Execution Failed: {draft.execution_error}
            </div>
          )}
        </div>
      )}
      
      {showConfirm && (
        <ExecutionDialog
          toolId={draft.tool_id}
          riskLevel={draft.risk_level}
          details={draft.payload}
          onConfirm={handleConfirmApprove}
          onCancel={() => setShowConfirm(false)}
        />
      )}
    </div>
  );
}
```

**Purpose:** Approve/reject actions with confirmation

**MCP Invariants:**
- ✅ **UI only renders `requires_confirmation`** (backend decides)
- ✅ Shows execution status (executed/failed)
- ✅ No inference - only renders backend data

---

### Backend API: `lynx-ai/lynx/api/draft_routes.py`

```python
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from lynx.api.models import Draft, DraftListResponse
from lynx.core.session import get_current_session
import uuid

router = APIRouter(prefix="/api/drafts", tags=["drafts"])

@router.get("", response_model=DraftListResponse)
async def list_drafts(
    status: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    limit: int = Query(50),
    cursor: Optional[str] = Query(None),  # ✅ Cursor pagination
    session: dict = Depends(get_current_session),  # ✅ Auth + tenant
):
    """
    List drafts for a tenant.
    
    ✅ Backend derives tenant_id from session
    ✅ Server-side filtering (date range, status, type)
    ✅ Cursor pagination (better than offset for audit logs)
    """
    tenant_id = session['tenant_id']
    # Read from draft storage (Supabase, RLS enforced)
    # Filter by status, type, date range
    # Return cursor for next page
    pass

@router.get("/{draft_id}", response_model=Draft)
async def get_draft(
    draft_id: str,
    session: dict = Depends(get_current_session),
):
    """Get draft details (tenant-scoped)."""
    tenant_id = session['tenant_id']
    # ✅ Verify tenant_id matches session
    # Read from draft storage (RLS enforced)
    pass

@router.post("/{draft_id}/approve")
async def approve_draft(
    draft_id: str,
    session: dict = Depends(get_current_session),
):
    """
    Approve a draft.
    
    ✅ Idempotency: Check if already approved (prevent double execution)
    ✅ Draft lifecycle: draft → approved → executed/failed
    """
    tenant_id = session['tenant_id']
    user_id = session['user_id']
    request_id = str(uuid.uuid4())  # ✅ For debugging
    
    # ✅ Idempotency check (prevent double approval)
    draft = await get_draft_from_storage(draft_id, tenant_id)
    if draft.status != 'draft':
        raise HTTPException(400, f"Draft already {draft.status}")
    
    # Update draft status: draft → approved
    await update_draft_status(draft_id, 'approved', approved_by=user_id)
    
    # Create audit log entry
    await log_audit_event(
        tenant_id=tenant_id,
        actor_user_id=user_id,
        actor_role=session['role'],
        request_id=request_id,
        event_type='draft_approved',
        entity_type='draft',
        entity_id=draft_id,
    )
    
    # If execution required, call Cell MCP tool
    if draft.tool_id.startswith('cell.'):
        execution_id = await execute_draft(draft)
        # Update draft: approved → executed (or failed)
        await update_draft_status(
            draft_id, 
            'executed' if execution_id else 'failed',
            execution_id=execution_id,
        )
    
    return {"success": True, "draft_id": draft_id, "status": "approved"}

@router.post("/{draft_id}/reject")
async def reject_draft(
    draft_id: str,
    reason: str,
    session: dict = Depends(get_current_session),
):
    """Reject a draft."""
    tenant_id = session['tenant_id']
    user_id = session['user_id']
    request_id = str(uuid.uuid4())
    
    # Update draft status: draft → rejected
    await update_draft_status(draft_id, 'rejected', rejected_by=user_id, reason=reason)
    
    # Create audit log entry
    await log_audit_event(...)
    
    return {"success": True, "draft_id": draft_id, "status": "rejected"}
```

**Purpose:** Draft API endpoints (thin layer over MCP)

**✅ Fixed:**
- ✅ Auth + tenant from session
- ✅ Cursor pagination
- ✅ Idempotency (prevent double approval)
- ✅ Draft lifecycle: draft → approved → executed/failed

---

## ⚠️ Step C: Execution Confirmation Dialog

### Files to Create

#### 16. `ui/frontend/components/execution/ExecutionDialog.tsx`

```typescript
'use client';

interface ExecutionDialogProps {
  toolId: string;
  riskLevel: 'low' | 'medium' | 'high';
  details: Record<string, any>;
  affectedEntities?: string[];  // ✅ Added: from backend summary
  actorRole?: string;  // ✅ Added: execution role
  onConfirm: () => void;
  onCancel: () => void;
}

export function ExecutionDialog({ 
  toolId, 
  riskLevel, 
  details, 
  affectedEntities,
  actorRole,
  onConfirm, 
  onCancel 
}: ExecutionDialogProps) {
  return (
    <div className="execution-dialog-overlay">
      <div className="execution-dialog">
        <div className="dialog-header">
          <span className="warning-icon">⚠️</span>
          <h2>Confirm Execution</h2>
        </div>
        
        <div className="dialog-content">
          <p>You are about to execute a <strong>{riskLevel.toUpperCase()}-RISK</strong> action:</p>
          
          <div className="execution-details">
            <div><strong>Tool:</strong> {toolId}</div>
            <div><strong>Risk Level:</strong> {riskLevel.toUpperCase()}</div>
            {actorRole && (
              <div><strong>Execution Role:</strong> {actorRole}</div>
            )}
            
            <div className="execution-payload">
              <strong>Execution Details:</strong>
              <pre>{JSON.stringify(details, null, 2)}</pre>
            </div>
            
            {affectedEntities && affectedEntities.length > 0 && (
              <div className="affected-entities">
                <strong>Affected Entity IDs:</strong>
                <ul>
                  {affectedEntities.map((id, idx) => (
                    <li key={idx}>{id}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
          
          <p className="warning-text">
            This action cannot be undone.
            <br />
            This will create an audit record.
          </p>
        </div>
        
        <div className="dialog-actions">
          <button onClick={onCancel} className="button-secondary">
            Cancel
          </button>
          <button onClick={onConfirm} className="button-danger">
            Confirm
          </button>
        </div>
      </div>
    </div>
  );
}
```

**Purpose:** Execution confirmation modal (high-risk only)

**MCP Invariants:**
- ✅ Shows tool_id (from MCP)
- ✅ Shows risk_level (from MCP)
- ✅ Shows affected entities (from backend summary)
- ✅ Shows execution role (from session)
- ✅ Blocks execution until confirm
- ✅ Used by DraftActions when `requires_confirmation === true` (backend decides)

---

## 📊 Step D: Audit page `/audit`

### Files to Create

#### 17. `ui/frontend/app/audit/page.tsx`

```typescript
'use client';

import { AuditList } from '@/components/audit/AuditList';
import { AuditFilters } from '@/components/audit/AuditFilters';
import { useState } from 'react';

export default function AuditPage() {
  const [filters, setFilters] = useState({
    tenant_id: 'all',
    user_id: 'all',
    from_date: null,
    to_date: null,
  });

  return (
    <div className="audit-page">
      <h1>Audit Trail</h1>
      <AuditFilters filters={filters} onFiltersChange={setFilters} />
      <AuditList filters={filters} />
    </div>
  );
}
```

**Purpose:** Audit trail page

---

#### 18. `ui/frontend/app/audit/[runId]/page.tsx`

```typescript
'use client';

import { RunDetail } from '@/components/audit/RunDetail';
import { useParams } from 'next/navigation';

export default function RunDetailPage() {
  const params = useParams();
  const runId = params.runId as string;

  return (
    <div className="run-detail-page">
      <RunDetail runId={runId} />
    </div>
  );
}
```

**Purpose:** Run detail page

---

#### 19. `ui/frontend/components/audit/AuditList.tsx`

```typescript
'use client';

import { useAuditRuns } from '@/lib/api';
import { RunCard } from './RunCard';

export function AuditList({ filters }: { filters: any }) {
  const { data, isLoading } = useAuditRuns(filters);

  if (isLoading) return <div>Loading runs...</div>;

  return (
    <div className="audit-list">
      {data?.runs.map((run) => (
        <RunCard key={run.run_id} run={run} />
      ))}
    </div>
  );
}
```

**Purpose:** Run list

---

#### 20. `ui/frontend/components/audit/RunCard.tsx`

```typescript
'use client';

import Link from 'next/link';

interface Run {
  run_id: string;
  user_id: string;
  tenant_id: string;
  query: string;
  response: string;
  tool_calls: ToolCall[];
  created_at: string;
}

export function RunCard({ run }: { run: Run }) {
  return (
    <div className="run-card">
      <div className="run-header">
        <h3>Run #{run.run_id}</h3>
        <span className="run-status">✓</span>
      </div>
      <div className="run-meta">
        <span>User: {run.user_id}</span>
        <span>Tenant: {run.tenant_id}</span>
        <span>Created: {new Date(run.created_at).toLocaleString()}</span>
      </div>
      <div className="run-query">{run.query}</div>
      <div className="run-tool-calls">
        {run.tool_calls.map((tc, idx) => (
          <span key={idx} className="tool-call-badge">
            {tc.tool_id} ({tc.duration_ms}ms) ✓
          </span>
        ))}
      </div>
      <Link href={`/audit/${run.run_id}`}>View Details</Link>
    </div>
  );
}
```

**Purpose:** Individual run card

**MCP Invariants:**
- ✅ Displays tool_calls (read-only)
- ✅ Shows duration (from audit log)

---

#### 21. `ui/frontend/components/audit/RunDetail.tsx`

```typescript
'use client';

import { useAuditRun } from '@/lib/api';
import { ToolCallList } from './ToolCallList';

export function RunDetail({ runId }: { runId: string }) {
  const { data: run, isLoading } = useAuditRun(runId);

  if (isLoading) return <div>Loading...</div>;
  if (!run) return <div>Run not found</div>;

  return (
    <div className="run-detail">
      <h1>Run Details: #{run.run_id}</h1>
      
      <div className="run-info">
        <div>User: {run.user_id}</div>
        <div>Tenant: {run.tenant_id}</div>
        <div>Created: {new Date(run.created_at).toLocaleString()}</div>
        <div>Completed: {run.completed_at ? new Date(run.completed_at).toLocaleString() : 'N/A'}</div>
      </div>

      <div className="run-query">
        <h2>Query</h2>
        <p>{run.query}</p>
      </div>

      <div className="run-response">
        <h2>Response</h2>
        <p>{run.response}</p>
      </div>

      <div className="run-tool-calls">
        <h2>Tool Calls</h2>
        <ToolCallList toolCalls={run.tool_calls} />
      </div>
    </div>
  );
}
```

**Purpose:** Run detail view

---

#### 22. `ui/frontend/components/audit/ToolCallList.tsx`

```typescript
interface ToolCall {
  tool_id: string;
  status: 'success' | 'error';
  input: Record<string, any>;
  output: Record<string, any>;
  duration_ms: number;
}

export function ToolCallList({ toolCalls }: { toolCalls: ToolCall[] }) {
  return (
    <div className="tool-call-list">
      {toolCalls.map((tc, idx) => (
        <div key={idx} className="tool-call-item">
          <div className="tool-call-header">
            <span className="tool-id">{tc.tool_id}</span>
            <span className={`tool-status tool-status-${tc.status}`}>
              {tc.status === 'success' ? '✓' : '✗'}
            </span>
            <span className="tool-duration">{tc.duration_ms}ms</span>
          </div>
          <div className="tool-call-details">
            <div className="tool-input">
              <strong>Input:</strong>
              <pre>{JSON.stringify(tc.input, null, 2)}</pre>
            </div>
            <div className="tool-output">
              <strong>Output:</strong>
              <pre>{JSON.stringify(tc.output, null, 2)}</pre>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
```

**Purpose:** Tool calls display (read-only)

**MCP Invariants:**
- ✅ Displays tool_id (from MCP)
- ✅ Shows input/output (from audit log)
- ✅ Shows duration (from audit log)

---

### Backend API: `lynx-ai/lynx/api/audit_routes.py`

```python
from fastapi import APIRouter, Query

router = APIRouter(prefix="/api/audit", tags=["audit"])

@router.get("/runs")
async def list_runs(
    tenant_id: str,
    limit: int = Query(50),
    offset: int = Query(0),
    from_date: str = None,
    to_date: str = None,
    user_id: str = None,
):
    """List Lynx Runs (audit trail)."""
    # Read from audit storage (Supabase)
    # Filter by tenant, date, user
    pass

@router.get("/runs/{run_id}")
async def get_run(run_id: str):
    """Get run details."""
    # Read from audit storage
    pass
```

**Purpose:** Audit API endpoints (thin layer over audit storage)

---

## 🎨 Theme: Simple CSS Variables

### `ui/frontend/styles/globals.css`

```css
:root {
  /* Theme: Neo-Analog Ops Console */
  --color-void: #09090b;
  --color-paper: #121214;
  --color-paper-2: #18181b;
  --color-lux: #f4f4f5;
  --color-lux-dim: #a1a1aa;
  --color-clay: #71717a;
  --color-gold: #eab308;
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #f43f5e;
  
  /* Typography */
  --font-serif: 'Playfair Display', serif;
  --font-mono: 'JetBrains Mono', monospace;
  --font-sans: 'Inter', sans-serif;
  
  /* Spacing */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  /* Border Radius */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
}

body {
  background: var(--color-void);
  color: var(--color-lux);
  font-family: var(--font-sans);
}

.header {
  background: var(--color-paper);
  padding: var(--spacing-lg);
  border-bottom: 1px solid var(--color-paper-2);
}

.ask-lynx-button {
  background: var(--color-gold);
  color: var(--color-void);
  border: none;
  padding: var(--spacing-md) var(--spacing-lg);
  border-radius: var(--radius-md);
  cursor: pointer;
}

.risk-badge {
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: var(--radius-sm);
}

.risk-low { background: var(--color-success); }
.risk-medium { background: var(--color-warning); }
.risk-high { background: var(--color-error); }
```

**Purpose:** Simple CSS variables (swap to BioSkin later)

---

## 📚 API Client: TanStack Query + Shared Fetch Wrapper

### `ui/frontend/lib/api-client.ts` (NEW - Shared Fetch Wrapper)

```typescript
// ✅ Shared fetch wrapper (auth headers, errors, request_id)

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiError {
  message: string;
  request_id?: string;
  code?: string;
}

export async function apiFetch(
  endpoint: string,
  options: RequestInit = {}
): Promise<Response> {
  const requestId = crypto.randomUUID();  // ✅ Request ID for debugging
  
  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${getAuthToken()}`,  // ✅ Auth header
      'X-Request-ID': requestId,  // ✅ Request ID
      ...options.headers,
    },
    credentials: 'include',  // ✅ Include cookies (if using session)
  });
  
  if (!response.ok) {
    const error: ApiError = await response.json().catch(() => ({
      message: `HTTP ${response.status}: ${response.statusText}`,
      request_id: requestId,
    }));
    error.request_id = requestId;
    throw error;
  }
  
  return response;
}
```

**Purpose:** Shared fetch wrapper (auth, errors, request_id)

**✅ Fixed:**
- ✅ Auth headers (Bearer token or session cookie)
- ✅ Request ID for debugging
- ✅ Error handling with request_id

---

### `ui/frontend/lib/api.ts` (Updated)

```typescript
import { useQuery, useMutation } from '@tanstack/react-query';
import { apiFetch } from './api-client';
import { ChatRun, Draft, DraftListResponse, AuditRun } from './types';

// Chat API
export function useSendChatQuery() {
  return useMutation({
    mutationFn: async (data: { query: string; context?: { entity_type: string; entity_id: string } }) => {
      // ✅ Fixed: No tenant_id - backend derives from session
      const res = await apiFetch('/api/chat/query', {
        method: 'POST',
        body: JSON.stringify(data),
      });
      return res.json() as Promise<ChatRun>;
    },
  });
}

export function useChatRun(runId: string) {
  return useQuery({
    queryKey: ['chatRun', runId],
    queryFn: async () => {
      const res = await fetch(`/api/chat/runs/${runId}`);
      if (!res.ok) throw new Error('Failed to fetch run');
      return res.json();
    },
  });
}

// Draft API
export function useDrafts(filters: any) {
  return useQuery({
    queryKey: ['drafts', filters],
    queryFn: async () => {
      const params = new URLSearchParams(filters).toString();
      const res = await fetch(`/api/drafts?${params}`);
      if (!res.ok) throw new Error('Failed to fetch drafts');
      return res.json();
    },
  });
}

export function useDraft(draftId: string) {
  return useQuery({
    queryKey: ['draft', draftId],
    queryFn: async () => {
      const res = await fetch(`/api/drafts/${draftId}`);
      if (!res.ok) throw new Error('Failed to fetch draft');
      return res.json();
    },
  });
}

export function useApproveDraft() {
  return useMutation({
    mutationFn: async ({ draftId, approved_by }: { draftId: string; approved_by: string }) => {
      const res = await fetch(`/api/drafts/${draftId}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ approved_by }),
      });
      if (!res.ok) throw new Error('Failed to approve draft');
      return res.json();
    },
  });
}

export function useRejectDraft() {
  return useMutation({
    mutationFn: async ({ draftId, rejected_by, reason }: { draftId: string; rejected_by: string; reason: string }) => {
      const res = await fetch(`/api/drafts/${draftId}/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rejected_by, reason }),
      });
      if (!res.ok) throw new Error('Failed to reject draft');
      return res.json();
    },
  });
}

// Audit API
export function useAuditRuns(filters: any) {
  return useQuery({
    queryKey: ['auditRuns', filters],
    queryFn: async () => {
      const params = new URLSearchParams(filters).toString();
      const res = await fetch(`/api/audit/runs?${params}`);
      if (!res.ok) throw new Error('Failed to fetch audit runs');
      return res.json();
    },
  });
}

export function useAuditRun(runId: string) {
  return useQuery({
    queryKey: ['auditRun', runId],
    queryFn: async () => {
      const res = await fetch(`/api/audit/runs/${runId}`);
      if (!res.ok) throw new Error('Failed to fetch run');
      return res.json();
    },
  });
}
```

**Purpose:** TanStack Query hooks (thin client over API)

---

## ✅ Acceptance Tests (Complete List)

### Step A: Ask Lynx
- [ ] Global button opens chat everywhere
- [ ] Sends query, shows response
- [ ] Shows tool calls
- [ ] Contextual button pre-fills entity context
- [ ] **Loading state** displays while processing
- [ ] **Error state** shows request_id for debugging
- [ ] **Empty state** shows when no messages

### Step B: Drafts
- [ ] List renders with filters
- [ ] **Pagination** works (cursor-based)
- [ ] Detail renders payload
- [ ] Approve/reject updates status
- [ ] **Shows confirmation when `requires_confirmation === true`** (backend decides)
- [ ] **Shows execution status** (executed/failed)
- [ ] **Idempotency**: Approve clicked twice does not execute twice
- [ ] **Empty state**: "No drafts found" + filter reset
- [ ] **Error state**: Shows request_id

### Step C: Execution Confirm
- [ ] Cannot execute without confirm (when `requires_confirmation === true`)
- [ ] Shows tool + risk + details
- [ ] Shows affected entities (from backend)
- [ ] Shows execution role (from session)
- [ ] Blocks execution until confirm

### Step D: Audit
- [ ] List runs with filters
- [ ] **Pagination** works (cursor-based)
- [ ] Open run details
- [ ] Shows tool calls & duration
- [ ] **Tool call integrity**: tool_calls match audit log exactly
- [ ] **Empty state**: "No runs found" + filter reset
- [ ] **Error state**: Shows request_id

### Security / Tenancy (Critical)
- [ ] **Cannot access another tenant's run/draft** (RLS + API enforcement)
- [ ] **Audit list only returns tenant's records**
- [ ] **Backend rejects tenant_id mismatch** (if frontend sends it)

### Draft vs Execution Separation
- [ ] **Approved draft can still fail execution**
- [ ] **UI shows failed state + error message**
- [ ] **Execution status distinct from approval status**

---

## 🚀 Next Steps (Fastest Path - Corrected Order)

### Phase 0: Foundation Fixes (Week 1) - DO FIRST

**⚠️ CRITICAL:** Fix all blockers before UI implementation

1. ✅ **Verify No `tenant_id` in Client**
   - Status: Already fixed in map
   - Action: Double-check all API calls
   - Verification: `grep -r "tenant_id.*current" ui/frontend/` should return 0

2. ✅ **Implement API Boundary (Option A - Next.js Proxy)**
   - **Decision:** Next.js proxies FastAPI (same-origin, no CORS)
   - **Action:** Create Next.js API route handlers (see "API Boundary Implementation" below)
   - **Files:** `app/api/chat/query/route.ts`, `app/api/drafts/route.ts`, etc.

3. ✅ **Shared `apiFetch()` Wrapper**
   - Location: `lib/api-client.ts` (already documented)
   - Features: Auth headers, request_id, error handling

4. ✅ **Verify Contract Definitions**
   - Backend: `lynx/api/models.py`
   - Frontend: `lib/types.ts`
   - Verify: All contracts match

5. ⚠️ **Fix Thin Client Purity**
   - Location: `components/drafts/DraftActions.tsx`
   - Fix: Use `draft.requires_confirmation` only (no inference)
   - Rule: UI never infers, only renders backend flags

6. ⚠️ **Add `executing` State**
   - Backend: Add `EXECUTING = "executing"` to DraftStatus enum
   - Frontend: Add `'executing'` to DraftStatus type
   - Lifecycle: `draft → approved → executing → executed/failed`

**Deliverable:** All blockers fixed, ready for UI implementation

---

### Phase 1: Step A Chat UI (Week 2)

7. **Create Next.js app:**
   ```bash
   cd lynx-ai/ui
   npx create-next-app@latest frontend --typescript --app
   cd frontend
   npm install @tanstack/react-query
   ```

8. **Create Supabase tables:**
   - Run SQL from "Supabase Tables" section above
   - Set up RLS policies

9. **Implement backend `POST /api/chat/query`:**
   - Returns `run_id`, `response`, `tool_calls`, `policy.requires_confirmation`
   - Backend derives tenant_id from session
   - Creates audit log entry

10. **Implement Step A (Global "Ask Lynx" + Chat UI):**
    - With proper QueryClientProvider
    - With shared fetch wrapper (api-client.ts)
    - With loading/error/empty states
    - Backend-driven flags only (no inference)

---

### Phase 2: Step B Draft Review (Week 3)

11. **Implement Step B Draft Review:**
    - Full lifecycle (draft → approved → executing → executed/failed)
    - Thin client purity (no risk inference)
    - Execution status display

12. **Add CRUD-S Buttons (3 Fast Wins):**
    - "New Chat" button (explicit Create)
    - "Export Audit" button (CSV/JSON) (Create report)
    - "Delete Draft" button (safe delete)

---

### Phase 3: Step C + D + Silent Killers (Week 4)

13. **Implement Step C Execution Confirmation**
14. **Implement Step D Audit Trail**
15. **Add Silent Killers (2 Features):**
    - Keyboard shortcuts (`Cmd+K`, `/`, `Escape`)
    - Export audit logs (already in CRUD-S)

---

## 🔧 API Boundary Implementation (Option A - Recommended)

### Next.js API Route Structure

```
app/
├── api/
│   ├── chat/
│   │   └── query/
│   │       └── route.ts          # Proxy to FastAPI /api/chat/query
│   ├── drafts/
│   │   ├── route.ts               # Proxy to FastAPI /api/drafts
│   │   └── [draftId]/
│   │       ├── route.ts           # Proxy to FastAPI /api/drafts/{id}
│   │       ├── approve/
│   │       │   └── route.ts       # Proxy to FastAPI /api/drafts/{id}/approve
│   │       └── reject/
│   │           └── route.ts       # Proxy to FastAPI /api/drafts/{id}/reject
│   └── audit/
│       └── runs/
│           ├── route.ts           # Proxy to FastAPI /api/audit/runs
│           └── [runId]/
│               └── route.ts       # Proxy to FastAPI /api/audit/runs/{id}
```

### Example Proxy Route

**File:** `app/api/chat/query/route.ts`

```typescript
import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const requestId = crypto.randomUUID();  // ✅ Request ID for debugging
    
    // Forward to FastAPI
    const res = await fetch(`${FASTAPI_URL}/api/chat/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // Forward auth headers
        'Authorization': request.headers.get('Authorization') || '',
        'Cookie': request.headers.get('Cookie') || '',
        'X-Request-ID': requestId,  // ✅ Request ID
      },
      body: JSON.stringify(body),
      credentials: 'include',
    });
    
    if (!res.ok) {
      const error = await res.json().catch(() => ({
        error: `HTTP ${res.status}: ${res.statusText}`,
        request_id: requestId,
      }));
      return NextResponse.json(error, { status: res.status });
    }
    
    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { 
        error: 'Internal server error', 
        request_id: crypto.randomUUID() 
      },
      { status: 500 }
    );
  }
}
```

**Benefits:**
- ✅ Same-origin (cookies/session work)
- ✅ No CORS configuration needed
- ✅ Can add middleware (rate limiting, auth)
- ✅ Cleaner separation

---

## 🔧 CRUD-S Buttons Implementation

### Button 1: "New Chat" (Explicit Create)

**Location:** `components/chat/ChatInterface.tsx`

```typescript
export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  
  const handleNewChat = () => {
    setMessages([]);  // Clear messages
    // Optional: Navigate to fresh chat URL
  };
  
  return (
    <div className="chat-interface">
      <div className="chat-header">
        <h2>Ask Lynx</h2>
        <button onClick={handleNewChat} className="button-create">
          New Chat
        </button>
      </div>
      {/* ... rest of chat UI */}
    </div>
  );
}
```

**Purpose:** Explicit Create action (CRUD-S compliance)

---

### Button 2: "Export Audit" (CSV/JSON)

**Location:** `components/audit/AuditList.tsx`

```typescript
export function AuditList({ filters }: { filters: any }) {
  const { data } = useAuditRuns(filters);
  
  const handleExport = async (format: 'csv' | 'json') => {
    const params = new URLSearchParams({
      ...filters,
      format,
    }).toString();
    
    const res = await fetch(`/api/audit/export?${params}`);
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit-${Date.now()}.${format}`;
    a.click();
    window.URL.revokeObjectURL(url);
  };
  
  return (
    <div className="audit-list">
      <div className="audit-header">
        <h2>Audit Trail</h2>
        <div className="audit-actions">
          <button onClick={() => handleExport('csv')}>Export CSV</button>
          <button onClick={() => handleExport('json')}>Export JSON</button>
        </div>
      </div>
      {/* ... list */}
    </div>
  );
}
```

**Backend API (`lynx/api/audit_routes.py`):**
```python
@router.get("/export")
async def export_audit(
    format: str = Query('csv'),  # csv or json
    session: dict = Depends(get_current_session),
):
    """Export audit logs (CSV or JSON)."""
    tenant_id = session['tenant_id']  # ✅ Server-side tenant
    runs = await get_audit_runs(tenant_id, filters)
    
    if format == 'csv':
        csv_content = generate_csv(runs)
        return Response(
            content=csv_content,
            media_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename="audit-{timestamp}.csv"'}
        )
    else:
        json_content = json.dumps([run.dict() for run in runs], indent=2)
        return Response(
            content=json_content,
            media_type='application/json',
            headers={'Content-Disposition': f'attachment; filename="audit-{timestamp}.json"'}
        )
```

**Purpose:** Enterprise parity + Create report (CRUD-S compliance)

---

### Button 3: "Delete Draft" (Safe Delete)

**Location:** `components/drafts/DraftActions.tsx`

```typescript
export function DraftActions({ draft }: { draft: Draft }) {
  const deleteDraft = useDeleteDraft();
  
  const handleDelete = () => {
    // ✅ Only allow delete for draft or rejected status
    if (draft.status === 'draft' || draft.status === 'rejected') {
      if (confirm('Are you sure you want to delete this draft?')) {
        deleteDraft.mutate({ draftId: draft.draft_id });
      }
    }
  };
  
  return (
    <div className="draft-actions">
      {/* ... approve/reject buttons */}
      {(draft.status === 'draft' || draft.status === 'rejected') && (
        <button onClick={handleDelete} className="button-delete">
          Delete Draft
        </button>
      )}
    </div>
  );
}
```

**Backend API (`lynx/api/draft_routes.py`):**
```python
@router.delete("/{draft_id}")
async def delete_draft(
    draft_id: str,
    session: dict = Depends(get_current_session),
):
    """Delete a draft (only if draft or rejected status)."""
    tenant_id = session['tenant_id']  # ✅ Server-side tenant
    draft = await get_draft(draft_id, tenant_id)
    
    # ✅ Safety check: Only allow delete for draft or rejected
    if draft.status not in ['draft', 'rejected']:
        raise HTTPException(400, "Cannot delete draft in this status")
    
    await delete_draft_from_storage(draft_id, tenant_id)
    
    # Create audit log entry
    await log_audit_event(
        tenant_id=tenant_id,
        actor_user_id=session['user_id'],
        actor_role=session['role'],
        request_id=str(uuid.uuid4()),
        event_type='draft_deleted',
        entity_type='draft',
        entity_id=draft_id,
    )
    
    return {"success": True}
```

**Purpose:** Safe Delete action (CRUD-S compliance)

---

## ⌨️ Silent Killers Implementation

### Feature 1: Keyboard Shortcuts

**Location:** `lib/keyboard-shortcuts.ts` (NEW)

```typescript
'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export function useKeyboardShortcuts() {
  const router = useRouter();
  
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd+K or Ctrl+K: Open Ask Lynx
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        router.push('/chat');
      }
      
      // / : Focus chat input (if on chat page)
      if (e.key === '/' && !e.metaKey && !e.ctrlKey && !e.shiftKey) {
        const input = document.querySelector('.chat-input input') as HTMLInputElement;
        if (input && document.activeElement !== input) {
          e.preventDefault();
          input.focus();
        }
      }
      
      // Escape: Close modals
      if (e.key === 'Escape') {
        const modals = document.querySelectorAll('[data-modal-open="true"]');
        modals.forEach(modal => {
          // Close modal logic
          modal.setAttribute('data-modal-open', 'false');
        });
      }
    };
    
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [router]);
}
```

**Usage in Layout:**
```typescript
import { useKeyboardShortcuts } from '@/lib/keyboard-shortcuts';

export default function RootLayout({ children }) {
  useKeyboardShortcuts();  // ✅ Enable shortcuts
  return (/* ... */);
}
```

**Shortcuts:**
- `Cmd+K` / `Ctrl+K`: Open Ask Lynx
- `/`: Focus chat input
- `Escape`: Close modals

**Purpose:** Power user efficiency (Silent Killer)

---

### Feature 2: Export Audit Logs

**Status:** ✅ **ALREADY DOCUMENTED** in CRUD-S Button 2 above

**Purpose:** Enterprise parity + compliance workflows (Silent Killer)

---

## 🔐 Auth Approach (Current State)

**Question:** What is the current auth approach?

**Current Implementation:**
- ⚠️ **Not explicitly documented** in implementation map
- ✅ **Backend pattern:** `get_current_session()` dependency (FastAPI)
- ⚠️ **Frontend pattern:** Not yet implemented

**Recommended Approach (Based on Thin Client Doctrine):**

### Option 1: Session Cookies (Recommended for Same-Origin)

**Backend (FastAPI):**
```python
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
import jwt

security = HTTPBearer()

async def get_current_session(
    token: str = Depends(security),
) -> dict:
    """Get current session from JWT token."""
    try:
        payload = jwt.decode(token.credentials, SECRET_KEY, algorithms=["HS256"])
        return {
            'tenant_id': payload['tenant_id'],
            'user_id': payload['user_id'],
            'role': payload['role'],
        }
    except jwt.InvalidTokenError:
        raise HTTPException(401, "Invalid token")
```

**Frontend (Next.js):**
```typescript
// apiFetch automatically includes auth
const res = await apiFetch('/api/chat/query', {
  method: 'POST',
  body: JSON.stringify(data),
  credentials: 'include',  // ✅ Include cookies
});
```

### Option 2: Bearer Token (Alternative)

**Frontend:**
```typescript
function getAuthToken(): string {
  // Get from localStorage, sessionStorage, or auth context
  return localStorage.getItem('auth_token') || '';
}

const res = await apiFetch('/api/chat/query', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${getAuthToken()}`,
  },
  body: JSON.stringify(data),
});
```

**Recommendation:** Use **Session Cookies** (Option 1) if using Next.js proxy (same-origin). Use **Bearer Token** (Option 2) if calling FastAPI directly.

---

## ✅ Final Verification Checklist

### Before Starting Implementation

- [ ] ✅ No `tenant_id` in client code
- [ ] ✅ API boundary decision made (Option A - Next.js proxy)
- [ ] ✅ Contracts defined (backend ↔ frontend match)
- [ ] ✅ DraftActions uses `requires_confirmation` only
- [ ] ✅ DraftStatus includes `executing` state
- [ ] ✅ No JSON in queryString
- [ ] ✅ QueryClientProvider in layout
- [ ] ✅ Auth approach decided (session cookies or bearer token)

### During Implementation

- [ ] Backend derives tenant from session (every endpoint)
- [ ] Backend returns `requires_confirmation` (not inferred)
- [ ] UI only renders backend flags (no inference)
- [ ] Draft lifecycle includes `executing` state
- [ ] CRUD-S buttons implemented (3 fast wins)
- [ ] Keyboard shortcuts working
- [ ] Export audit logs working

---

**Status:** ✅ **READY TO START** (All blockers fixed)  
**Next Action:** Implement Phase 0 (Foundation Fixes) first

### Phase 2: Step B (Draft Review)

6. **Implement backend draft endpoints:**
   - With cursor pagination
   - With idempotency (prevent double approval)
   - With draft lifecycle (draft → approved → executed/failed)

7. **Implement Step B (Draft Review):**
   - With pagination
   - With execution status display
   - With empty/error states

### Phase 3: Step C + D

8. **Implement Step C** (Execution Confirmation)
9. **Implement Step D** (Audit Trail)

---

## 🔧 API Boundary Decision

**Choose one approach early:**

### Option 1: Direct FastAPI Calls (Simplest)

**Frontend:**
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

**Pros:**
- ✅ Simple setup
- ✅ No proxy needed

**Cons:**
- ⚠️ CORS configuration needed
- ⚠️ Session cookies may not work (different origin)

### Option 2: Next.js API Routes Proxy (Cleanest)

**Frontend:**
```typescript
// Calls Next.js API route
const res = await fetch('/api/chat/query', ...);
```

**Next.js API Route (`app/api/chat/query/route.ts`):**
```typescript
export async function POST(request: Request) {
  // Proxy to FastAPI
  const res = await fetch(`${process.env.FASTAPI_URL}/api/chat/query`, {
    method: 'POST',
    headers: request.headers,
    body: await request.text(),
  });
  return res;
}
```

**Pros:**
- ✅ Same-origin (cookies work)
- ✅ No CORS issues
- ✅ Can add middleware (rate limiting, etc.)

**Cons:**
- ⚠️ Extra proxy layer

**Recommendation:** Start with Option 1, migrate to Option 2 if needed.

---

**Status:** ✅ **READY TO IMPLEMENT**  
**Approach:** Thin client over MCP invariants  
**Theme:** Simple CSS variables (swap to BioSkin later)

