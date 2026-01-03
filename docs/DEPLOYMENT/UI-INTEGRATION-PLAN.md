# UI Integration Plan — Phase 5 Completion

**Date:** 2026-01-27  
**PRD:** PRD-LYNX-003 (Phase 5)  
**Status:** ⏸️ **BLOCKED** - Waiting for new @aibos/design-system npm package  
**Goal:** Complete UI integration (5 components) before generating new PRD  
**Blocking Dependency:** New @aibos/design-system package (easier to apply)

---

## 🎯 Objective

Complete Phase 5 UI Integration to achieve 100% PRD-LYNX-003 compliance before drafting PRD-LYNX-004.

**Current Status:** 60% complete (Dashboard exists, UI components missing)  
**Target:** 100% complete (All 5 UI components implemented)

**⚠️ BLOCKING DEPENDENCY:** Waiting for new @aibos/design-system npm package that is much easier to apply. Implementation will proceed once the new package is available.

---

## 📋 Required Components (PRD Phase 5)

### 1. Global "Ask Lynx" Button
- **Purpose:** Universal access to Lynx AI from any page
- **Location:** Global header/navigation
- **Functionality:** Opens chat interface

### 2. Contextual "Ask Lynx about this" Buttons
- **Purpose:** Context-aware queries about specific entities
- **Location:** Entity detail pages (documents, workflows, payments, etc.)
- **Functionality:** Pre-fills context, opens chat with entity context

### 3. Draft Review Interface
- **Purpose:** Review and approve/reject drafts
- **Location:** Dedicated drafts page
- **Functionality:** List drafts, view details, approve/reject actions

### 4. Execution Confirmation Dialogs
- **Purpose:** Confirm high-risk executions before proceeding
- **Location:** Modal dialogs triggered before execution
- **Functionality:** Show execution details, require explicit confirmation

### 5. Basic Audit Trail Visibility
- **Purpose:** View recent Lynx Runs and tool calls
- **Location:** Audit trail page or sidebar
- **Functionality:** List recent runs, show tool calls, filter by date/tenant

---

## 🏗️ Architecture Decision

### Option A: Enhance Existing FastAPI Dashboard
- ✅ Already exists
- ✅ Fast to implement
- ❌ Not aligned with PRD (PRD specifies React/Next.js)
- ❌ Limited interactivity

### Option B: Create React/Next.js Frontend (PRD-Aligned)
- ✅ Matches PRD specification (React/Next.js + shadcn/ui + TanStack Query)
- ✅ Better UX with real-time updates
- ✅ Design system already installed (@aibos/design-system)
- ⚠️ More setup required

**Decision:** **Option B** - Create React/Next.js frontend to match PRD specification.

---

## 📐 Technical Stack (Per PRD)

- **Frontend Framework:** React/Next.js
- **UI Components:** shadcn/ui (or @aibos/design-system)
- **State Management:** TanStack Query
- **API Client:** Fetch/axios with TanStack Query
- **Styling:** Tailwind CSS (via design system)

---

## 🔌 Required API Endpoints

### Phase 1: Core Chat API

```
POST /api/chat/query
  Request: { query: string, context?: object, tenant_id: string }
  Response: { run_id: string, response: string, tool_calls: [] }

GET /api/chat/runs/{run_id}
  Response: { run_id, status, response, tool_calls, created_at }
```

### Phase 2: Draft Management API

```
GET /api/drafts
  Query: ?tenant_id=xxx&status=draft&limit=50
  Response: { drafts: [], total: number }

GET /api/drafts/{draft_id}
  Response: { draft_id, type, payload, status, risk_level, ... }

POST /api/drafts/{draft_id}/approve
  Request: { approved_by: string, notes?: string }
  Response: { success: true, execution_id?: string }

POST /api/drafts/{draft_id}/reject
  Request: { rejected_by: string, reason: string }
  Response: { success: true }
```

### Phase 3: Execution API

```
POST /api/executions/{execution_id}/confirm
  Request: { confirmed_by: string, notes?: string }
  Response: { success: true, status: string }

GET /api/executions/{execution_id}
  Response: { execution_id, status, result, tool_calls, ... }
```

### Phase 4: Audit Trail API

```
GET /api/audit/runs
  Query: ?tenant_id=xxx&limit=50&offset=0&from_date=xxx&to_date=xxx
  Response: { runs: [], total: number }

GET /api/audit/runs/{run_id}
  Response: { run_id, user_id, tenant_id, query, response, tool_calls, created_at }
```

---

## 📁 Project Structure

```
lynx-ai/
├── lynx/
│   └── api/
│       ├── dashboard.py          # Existing FastAPI dashboard
│       ├── api_routes.py          # NEW: API endpoints for UI
│       └── static/                # Static assets
│
└── ui/
    ├── package.json               # Existing
    ├── node_modules/              # @aibos/design-system installed
    └── frontend/                  # NEW: Next.js app
        ├── app/
        │   ├── layout.tsx         # Root layout with global "Ask Lynx" button
        │   ├── page.tsx           # Home page
        │   ├── chat/
        │   │   └── page.tsx       # Chat interface
        │   ├── drafts/
        │   │   ├── page.tsx       # Draft list
        │   │   └── [id]/
        │   │       └── page.tsx   # Draft review
        │   └── audit/
        │       └── page.tsx       # Audit trail
        ├── components/
        │   ├── AskLynxButton.tsx  # Global button
        │   ├── ContextualButton.tsx # Contextual button
        │   ├── ChatInterface.tsx   # Chat UI
        │   ├── DraftReview.tsx     # Draft review component
        │   ├── ExecutionDialog.tsx # Confirmation dialog
        │   └── AuditTrail.tsx     # Audit trail component
        ├── lib/
        │   └── api.ts             # API client with TanStack Query
        └── package.json
```

---

## 🚀 Implementation Phases

### Phase 1: API Endpoints (2-3 days)

**Goal:** Create backend API endpoints for UI integration

**Tasks:**
1. [ ] Create `lynx/api/api_routes.py` with chat endpoints
2. [ ] Add draft management endpoints
3. [ ] Add execution confirmation endpoints
4. [ ] Add audit trail endpoints
5. [ ] Add CORS configuration for frontend
6. [ ] Write API tests

**Deliverable:** All API endpoints working, tested

---

### Phase 2: Next.js Setup (1 day)

**Goal:** Initialize Next.js app with design system

**Tasks:**
1. [ ] Initialize Next.js app in `lynx-ai/ui/frontend/`
2. [ ] Install dependencies (TanStack Query, shadcn/ui or use @aibos/design-system)
3. [ ] Configure API client
4. [ ] Set up routing structure
5. [ ] Configure Tailwind CSS (if using shadcn/ui)

**Deliverable:** Next.js app running, connected to API

---

### Phase 3: Global "Ask Lynx" Button (1 day)

**Goal:** Implement global chat access

**Tasks:**
1. [ ] Create `AskLynxButton` component
2. [ ] Add to root layout (persistent across pages)
3. [ ] Implement click handler (opens chat modal/page)
4. [ ] Style with design system

**Deliverable:** Global button visible, opens chat

---

### Phase 4: Chat Interface (2-3 days)

**Goal:** Full chat interface for querying Lynx

**Tasks:**
1. [ ] Create `ChatInterface` component
2. [ ] Implement message input
3. [ ] Implement message display (user queries, Lynx responses)
4. [ ] Show tool calls in progress
5. [ ] Add loading states
6. [ ] Integrate with `/api/chat/query` endpoint
7. [ ] Add error handling

**Deliverable:** Working chat interface

---

### Phase 5: Contextual Buttons (1-2 days)

**Goal:** Context-aware "Ask Lynx about this" buttons

**Tasks:**
1. [ ] Create `ContextualButton` component
2. [ ] Accept context props (entity_type, entity_id, entity_data)
3. [ ] Pre-fill chat with context
4. [ ] Add to example entity pages (documents, workflows, payments)
5. [ ] Style with design system

**Deliverable:** Contextual buttons working on entity pages

---

### Phase 6: Draft Review Interface (3-4 days)

**Goal:** Complete draft review and approval workflow

**Tasks:**
1. [ ] Create `DraftList` component (list all drafts)
2. [ ] Create `DraftReview` component (view single draft)
3. [ ] Implement approve action
4. [ ] Implement reject action
5. [ ] Show draft details (type, payload, risk level)
6. [ ] Add filters (status, type, date)
7. [ ] Integrate with `/api/drafts` endpoints
8. [ ] Add loading/error states

**Deliverable:** Complete draft review interface

---

### Phase 7: Execution Confirmation Dialogs (2 days)

**Goal:** Confirm high-risk executions before proceeding

**Tasks:**
1. [ ] Create `ExecutionDialog` component (modal)
2. [ ] Show execution details (tool, input, risk level)
3. [ ] Require explicit confirmation
4. [ ] Integrate with `/api/executions/{id}/confirm`
5. [ ] Show execution status after confirmation
6. [ ] Add to draft approval flow (if execution required)

**Deliverable:** Execution confirmation dialogs working

---

### Phase 8: Audit Trail Visibility (2 days)

**Goal:** View recent Lynx Runs and tool calls

**Tasks:**
1. [ ] Create `AuditTrail` component
2. [ ] List recent runs (table/card view)
3. [ ] Show run details (query, response, tool calls)
4. [ ] Add filters (date range, tenant, user)
5. [ ] Add pagination
6. [ ] Integrate with `/api/audit/runs` endpoint
7. [ ] Style with design system

**Deliverable:** Audit trail page complete

---

### Phase 9: Integration & Polish (2-3 days)

**Goal:** Integrate all components, polish UX

**Tasks:**
1. [ ] Connect all components to API
2. [ ] Add error boundaries
3. [ ] Add loading states everywhere
4. [ ] Add toast notifications for actions
5. [ ] Test end-to-end flows
6. [ ] Fix styling issues
7. [ ] Add responsive design
8. [ ] Write component tests

**Deliverable:** Complete, polished UI integration

---

## 📊 Estimated Timeline

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: API Endpoints | 2-3 days | None |
| Phase 2: Next.js Setup | 1 day | Phase 1 |
| Phase 3: Global Button | 1 day | Phase 2 |
| Phase 4: Chat Interface | 2-3 days | Phase 1, 2, 3 |
| Phase 5: Contextual Buttons | 1-2 days | Phase 4 |
| Phase 6: Draft Review | 3-4 days | Phase 1, 2 |
| Phase 7: Execution Dialogs | 2 days | Phase 1, 2, 6 |
| Phase 8: Audit Trail | 2 days | Phase 1, 2 |
| Phase 9: Integration & Polish | 2-3 days | All phases |
| **Total** | **16-22 days** | **3-4 weeks** |

---

## ✅ Acceptance Criteria

### Global "Ask Lynx" Button
- [ ] Visible on all pages (persistent in header/nav)
- [ ] Opens chat interface on click
- [ ] Styled with design system
- [ ] Accessible (keyboard navigation, screen reader)

### Chat Interface
- [ ] User can type queries
- [ ] Shows Lynx responses
- [ ] Shows tool calls in progress
- [ ] Handles errors gracefully
- [ ] Responsive design

### Contextual Buttons
- [ ] Appears on entity pages (documents, workflows, payments)
- [ ] Pre-fills chat with entity context
- [ ] Opens chat interface
- [ ] Styled consistently

### Draft Review Interface
- [ ] Lists all drafts (filterable)
- [ ] Shows draft details
- [ ] Approve action works
- [ ] Reject action works
- [ ] Updates UI after actions

### Execution Confirmation Dialogs
- [ ] Shows before high-risk executions
- [ ] Displays execution details
- [ ] Requires explicit confirmation
- [ ] Shows execution status after confirmation

### Audit Trail Visibility
- [ ] Lists recent runs
- [ ] Shows run details
- [ ] Filterable by date/tenant/user
- [ ] Paginated for large datasets

---

## 🔧 Technical Decisions

### Design System Choice

**Option A: Use @aibos/design-system (Already Installed)**
- ✅ Already installed
- ✅ Matches project standards
- ⚠️ May need additional components

**Option B: Use shadcn/ui (PRD Specified)**
- ✅ PRD explicitly mentions shadcn/ui
- ✅ More components available
- ⚠️ Need to install

**Decision:** Start with @aibos/design-system, add shadcn/ui if needed for missing components.

### API Integration Pattern

**Use TanStack Query (PRD Specified)**
- ✅ PRD explicitly mentions TanStack Query
- ✅ Handles caching, loading states, error handling
- ✅ Perfect for React/Next.js

**Pattern:**
```typescript
// lib/api.ts
import { useQuery, useMutation } from '@tanstack/react-query';

export function useChatQuery() {
  return useMutation({
    mutationFn: async (query: string) => {
      const res = await fetch('/api/chat/query', {
        method: 'POST',
        body: JSON.stringify({ query }),
      });
      return res.json();
    },
  });
}
```

---

## 📝 Next Steps

### Immediate (This Week)
1. **Review this plan** - Confirm approach and timeline
2. **Start Phase 1** - Create API endpoints
3. **Set up development environment** - Next.js, dependencies

### Short-term (Next 2-4 Weeks)
1. **Complete all 9 phases** - Full UI integration
2. **Test end-to-end** - All flows working
3. **Update documentation** - Mark Phase 5 complete

### Before New PRD
1. **Verify 100% PRD-LYNX-003 compliance** - All phases complete
2. **Update PRD-STATUS-MATRIX.md** - Mark Phase 5 as 100%
3. **Generate PRD-LYNX-004** - Next phase PRD

---

## 🎯 Optimization Opportunities (From GitHub Research)

### 1. Leverage Existing Dashboard Infrastructure

**Current State:**
- ✅ FastAPI dashboard already exists (`lynx-ai/lynx/api/dashboard.py`)
- ✅ Design system installed (`@aibos/design-system` v1.1.0)
- ✅ Static file serving configured
- ✅ CORS middleware already set up

**Optimization:**
- **Reuse existing FastAPI routes** - Add new API endpoints to existing `dashboard.py` instead of creating separate `api_routes.py`
- **Leverage existing static file serving** - Use `/static/` for design system CSS
- **Incremental enhancement** - Start with enhancing dashboard, then add React components

**Time Savings:** 1-2 days (avoid duplicate setup)

---

### 2. Reference awesome-llm-apps UI Patterns

**From ANALYSIS-LYNX-002:**
- ✅ `browser_mcp_agent` - Shows MCP agent UI integration patterns
- ✅ `github_mcp_agent` - Shows Streamlit UI with natural language interface
- ✅ Configuration patterns (`mcp_agent.config.yaml`)

**Optimization:**
- **Study chat interface patterns** from `github_mcp_agent` (Streamlit example)
- **Adapt for React/Next.js** - Convert Streamlit patterns to React components
- **Reuse MCP tool display patterns** - Show tool calls in progress

**Time Savings:** 2-3 days (learning from examples vs. building from scratch)

**Action Items:**
1. [ ] Clone `awesome-llm-apps` repository (if not already)
2. [ ] Study `mcp_ai_agents/github_mcp_agent/` UI patterns
3. [ ] Study `mcp_ai_agents/browser_mcp_agent/` configuration patterns
4. [ ] Document key UI patterns for adaptation

---

### 3. Component Reuse Strategy

**Optimization:**
- **Start with @aibos/design-system** - Use existing components (Button, Card, StatusIndicator)
- **Add shadcn/ui incrementally** - Only for missing components (Dialog, Table, etc.)
- **Reuse existing dashboard components** - Extract reusable parts from current dashboard

**Time Savings:** 1 day (avoid installing unnecessary packages)

---

### 4. API Design Optimization

**Current State:**
- ✅ FastAPI already configured
- ✅ Dashboard models exist (`dashboard_models.py`)
- ✅ Status endpoints working (`/health`, `/api/status`)

**Optimization:**
- **Extend existing models** - Add chat/draft/audit models to `dashboard_models.py`
- **Reuse existing patterns** - Follow same structure as `/api/status` endpoint
- **Leverage existing middleware** - CORS, error handling already configured

**Time Savings:** 0.5-1 day (avoid duplicate setup)

---

### 5. Phased Integration Approach

**Optimization:**
Instead of building everything new, use **hybrid approach**:

**Phase 1 (Week 1):** Enhance existing dashboard
- Add chat API endpoints to existing `dashboard.py`
- Add basic chat UI using existing HTML/CSS patterns
- Use design system CSS classes

**Phase 2 (Week 2):** Add React components incrementally
- Create Next.js app alongside existing dashboard
- Migrate chat interface to React component
- Keep dashboard as fallback

**Phase 3 (Week 3):** Complete React migration
- Migrate remaining components to React
- Full Next.js frontend

**Time Savings:** 1 week (faster initial delivery, incremental migration)

---

### 6. TanStack Query Optimization

**Best Practices from Research:**
- Use **query invalidation** for real-time updates (draft status changes)
- Use **optimistic updates** for approve/reject actions
- Use **infinite queries** for audit trail pagination

**Pattern:**
```typescript
// Optimized pattern for draft approval
const approveDraft = useMutation({
  mutationFn: approveDraftAPI,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['drafts'] });
    toast.success('Draft approved');
  },
  onMutate: async (draftId) => {
    // Optimistic update
    await queryClient.cancelQueries({ queryKey: ['drafts'] });
    const previous = queryClient.getQueryData(['drafts']);
    queryClient.setQueryData(['drafts'], (old) => 
      old.map(d => d.id === draftId ? { ...d, status: 'approved' } : d)
    );
    return { previous };
  },
  onError: (err, draftId, context) => {
    queryClient.setQueryData(['drafts'], context.previous);
  },
});
```

**Time Savings:** 0.5 day (better UX, fewer bugs)

---

### 7. shadcn/ui Component Selection

**Optimization:**
Only install components we actually need:

**Must Have:**
- `dialog` - For execution confirmation dialogs
- `table` - For audit trail and draft lists
- `button` - If @aibos/design-system doesn't have enough variants
- `toast` - For notifications

**Nice to Have:**
- `card` - If @aibos/design-system Card is insufficient
- `badge` - For status indicators
- `input` - For chat input (if needed)

**Time Savings:** 0.5 day (smaller bundle, faster setup)

---

## 📊 Revised Timeline (Optimized)

| Phase | Original | Optimized | Savings |
|-------|----------|-----------|---------|
| Phase 1: API Endpoints | 2-3 days | 1.5-2 days | 0.5-1 day |
| Phase 2: Next.js Setup | 1 day | 0.5 day | 0.5 day |
| Phase 3: Global Button | 1 day | 0.5 day | 0.5 day |
| Phase 4: Chat Interface | 2-3 days | 1.5-2 days | 0.5-1 day |
| Phase 5: Contextual Buttons | 1-2 days | 1 day | 0-1 day |
| Phase 6: Draft Review | 3-4 days | 2-3 days | 1 day |
| Phase 7: Execution Dialogs | 2 days | 1.5 days | 0.5 day |
| Phase 8: Audit Trail | 2 days | 1.5 days | 0.5 day |
| Phase 9: Integration & Polish | 2-3 days | 2 days | 0-1 day |
| **Total** | **16-22 days** | **12-15 days** | **4-7 days** |

**New Estimate:** **2-3 weeks** (down from 3-4 weeks)

---

## 💻 Implementation Code Examples

### Example 1: Extending Existing Dashboard with Chat API

**File:** `lynx-ai/lynx/api/dashboard.py` (add to existing file)

```python
# Add to existing dashboard.py after line 520

from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional

# Request/Response models
class ChatQueryRequest(BaseModel):
    query: str
    context: Optional[dict] = None
    tenant_id: str

class ChatQueryResponse(BaseModel):
    run_id: str
    response: str
    tool_calls: list
    status: str

# Chat endpoint (reuses existing app instance)
@app.post("/api/chat/query", response_model=ChatQueryResponse)
async def chat_query(request: ChatQueryRequest):
    """Chat endpoint - leverages existing dashboard infrastructure."""
    try:
        # TODO: Integrate with Lynx AI core
        # For now, return mock response
        return ChatQueryResponse(
            run_id="run_123",
            response="Mock response - implement with Lynx core",
            tool_calls=[],
            status="success"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Benefits:**
- ✅ Reuses existing FastAPI app
- ✅ Reuses existing CORS middleware
- ✅ Follows existing pattern (`/api/status`)
- ✅ Can be tested immediately

---

### Example 2: React Component Using Existing Dashboard Models

**File:** `lynx-ai/ui/frontend/components/ChatInterface.tsx`

```typescript
'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Button, Card } from '@aibos/design-system/react';

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  tool_calls?: any[];
}

export function ChatInterface() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');

  const chatMutation = useMutation({
    mutationFn: async (query: string) => {
      const res = await fetch('/api/chat/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query,
          tenant_id: 'default', // TODO: Get from auth context
        }),
      });
      if (!res.ok) throw new Error('Chat failed');
      return res.json();
    },
    onSuccess: (data) => {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: data.response, tool_calls: data.tool_calls },
      ]);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    setMessages((prev) => [...prev, { role: 'user', content: input }]);
    chatMutation.mutate(input);
    setInput('');
  };

  return (
    <Card className="p-6">
      <h2 className="text-xl font-semibold mb-4">Ask Lynx</h2>
      
      <div className="space-y-4 mb-4" style={{ minHeight: '300px', maxHeight: '500px', overflowY: 'auto' }}>
        {messages.map((msg, i) => (
          <div key={i} className={msg.role === 'user' ? 'text-right' : 'text-left'}>
            <div className={`inline-block p-3 rounded-lg ${
              msg.role === 'user' ? 'bg-blue-600' : 'bg-gray-700'
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 px-4 py-2 bg-gray-800 rounded-lg border border-gray-700"
          placeholder="Ask Lynx anything..."
          disabled={chatMutation.isPending}
        />
        <Button 
          type="submit" 
          disabled={chatMutation.isPending || !input.trim()}
        >
          {chatMutation.isPending ? 'Sending...' : 'Send'}
        </Button>
      </form>
    </Card>
  );
}
```

**Benefits:**
- ✅ Uses existing design system components
- ✅ Follows TanStack Query patterns
- ✅ Reuses existing API endpoint structure
- ✅ Matches existing dashboard styling

---

### Example 3: Global "Ask Lynx" Button (Reusing Dashboard Header)

**File:** `lynx-ai/lynx/api/dashboard.py` (modify existing header)

```python
# Modify render_shell function (around line 262)
# Add "Ask Lynx" button to header

def render_shell(vm: DashboardViewModel, cockpit: DeveloperCockpitViewModel) -> str:
    status_enum = vm.get_status_enum()
    
    # Add Ask Lynx button to header
    ask_lynx_button = """
    <button 
        onclick="window.open('/chat', '_blank')" 
        class="na-card" 
        style="padding: 8px 16px; cursor: pointer; color: var(--color-lux); background: var(--color-paper-2); border: 1px solid var(--color-stroke);"
    >
        <span style="font-weight: 600;">Ask Lynx</span>
    </button>
    """
    
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    ...
    <header class="na-command-bar">
        <div class="na-bar-inner">
            ...
            <div class="flex-gap">
                {ask_lynx_button}
                ...
            </div>
        </div>
    </header>
    ...
    """
```

**Benefits:**
- ✅ Minimal changes to existing code
- ✅ Reuses existing header styling
- ✅ Works immediately (no React setup needed)
- ✅ Can be enhanced later with React component

---

### Example 4: Draft Review Component (Leveraging Dashboard Models Pattern)

**File:** `lynx-ai/lynx/api/dashboard_models.py` (extend existing models)

```python
# Add to existing dashboard_models.py

class DraftViewModel:
    """Stable contract for draft data (follows DashboardViewModel pattern)."""
    
    def __init__(self, raw_draft: Dict[str, Any]):
        self.draft_id: str = raw_draft.get("draft_id", "")
        self.type: str = raw_draft.get("type", "unknown")
        self.payload: Dict[str, Any] = raw_draft.get("payload", {})
        self.status: str = raw_draft.get("status", "draft")
        self.risk_level: str = raw_draft.get("risk_level", "low")
        self.created_at: datetime = raw_draft.get("created_at", datetime.now())
        self.created_by: str = raw_draft.get("created_by", "unknown")
    
    def get_risk_status(self) -> ServiceStatus:
        """Convert risk level to status enum (reuses existing enum)."""
        risk_map = {
            "low": ServiceStatus.OK,
            "medium": ServiceStatus.PENDING,
            "high": ServiceStatus.BAD,
        }
        return risk_map.get(self.risk_level, ServiceStatus.INFO)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict (follows DashboardViewModel pattern)."""
        return {
            "draft_id": self.draft_id,
            "type": self.type,
            "payload": self.payload,
            "status": self.status,
            "risk_level": self.risk_level,
            "risk_status": self.get_risk_status().value,
            "created_at": self.created_at.isoformat(),
            "created_by": self.created_by,
        }
```

**Benefits:**
- ✅ Follows existing model pattern
- ✅ Reuses ServiceStatus enum
- ✅ Consistent with dashboard architecture
- ✅ Easy to test and maintain

---

### Example 5: Quick-Start Implementation Checklist

**Week 1: Foundation (3-4 days)**

```bash
# Day 1: API Endpoints
# 1. Add chat endpoint to dashboard.py
# 2. Add draft endpoints to dashboard.py
# 3. Add audit endpoints to dashboard.py
# 4. Test endpoints with curl/Postman

# Day 2: Next.js Setup
cd lynx-ai/ui
npx create-next-app@latest frontend --typescript --tailwind --app
cd frontend
npm install @tanstack/react-query @aibos/design-system

# Day 3: Global Button
# 1. Add "Ask Lynx" button to dashboard header (HTML)
# 2. Create /chat route in Next.js
# 3. Test button opens chat page

# Day 4: Chat Interface
# 1. Create ChatInterface component
# 2. Connect to /api/chat/query
# 3. Test end-to-end chat flow
```

**Week 2: Core Components (5-6 days)**

```bash
# Day 5-6: Contextual Buttons
# 1. Create ContextualButton component
# 2. Add to example entity pages
# 3. Test context pre-filling

# Day 7-9: Draft Review
# 1. Create DraftList component
# 2. Create DraftReview component
# 3. Connect to /api/drafts endpoints
# 4. Test approve/reject flow

# Day 10: Execution Dialogs
# 1. Create ExecutionDialog component (shadcn/ui Dialog)
# 2. Integrate with draft approval flow
# 3. Test confirmation workflow
```

**Week 3: Polish & Integration (3-4 days)**

```bash
# Day 11-12: Audit Trail
# 1. Create AuditTrail component
# 2. Add filters and pagination
# 3. Connect to /api/audit/runs

# Day 13-14: Integration & Testing
# 1. End-to-end testing
# 2. Error handling
# 3. Loading states
# 4. Responsive design
# 5. Documentation
```

---

## 🔍 Reference Repositories

### awesome-llm-apps (From ANALYSIS-LYNX-002)

**Repository:** https://github.com/Shubhamsaboo/awesome-llm-apps

**Key Examples to Study:**
1. **`mcp_ai_agents/github_mcp_agent/`**
   - Streamlit UI integration
   - Natural language query interface
   - MCP tool usage examples
   - **Relevance:** Chat interface patterns

2. **`mcp_ai_agents/browser_mcp_agent/`**
   - MCP agent structure
   - Configuration patterns (`mcp_agent.config.yaml`)
   - Tool registration patterns
   - **Relevance:** Backend API structure

3. **`mcp_ai_agents/multi_mcp_agent/`**
   - Multiple MCP server coordination
   - Tool aggregation patterns
   - **Relevance:** Audit trail (showing multiple tool calls)

**Action Items:**
- [ ] Clone repository: `git clone https://github.com/Shubhamsaboo/awesome-llm-apps.git`
- [ ] Study `mcp_ai_agents/github_mcp_agent/` UI patterns
- [ ] Study `mcp_ai_agents/browser_mcp_agent/` configuration
- [ ] Document patterns for adaptation

---

## 📚 Related Documents

- **PRD:** `docs/PRD/PRD-LYNX-003/doc.md` - Phase 5 requirements
- **Status:** `docs/DEPLOYMENT/PRD-STATUS-MATRIX.md` - Current status (60%)
- **Remaining:** `docs/DEPLOYMENT/PRD-VERIFICATION-REMAINING.md` - Detailed gaps
- **Design System:** `lynx-ai/ui/DESIGN-SYSTEM-SETUP.md` - Design system docs
- **Analysis:** `docs/ANALYSIS/ANALYSIS-LYNX-002.md` - awesome-llm-apps analysis

---

**Status:** ⏸️ **BLOCKED** - Waiting for new @aibos/design-system package  
**Estimated Completion:** 2-3 weeks after package release (down from 3-4 weeks)  
**Priority:** 🔴 **HIGH** - Required for PRD-LYNX-003 completion  
**Optimization Level:** ⚡ **HIGH** - 4-7 days saved through reuse and best practices  
**Blocking Dependency:** New @aibos/design-system npm package (easier integration)

---

## 📋 Quick-Start Action Plan

### ⏸️ BLOCKED: Waiting for New @aibos/design-system Package

**Status:** Implementation paused until new @aibos/design-system npm package is available.

**Why Waiting:**
- New package will be "much easier to apply"
- Current package (v1.1.0) may have integration complexity
- New package likely has improved React/Next.js integration
- Better documentation and examples expected

**What to Do While Waiting:**

1. **Research & Planning** (Can proceed now)
   - [ ] Clone awesome-llm-apps: `git clone https://github.com/Shubhamsaboo/awesome-llm-apps.git`
   - [ ] Study `mcp_ai_agents/github_mcp_agent/` UI patterns
   - [ ] Study `mcp_ai_agents/browser_mcp_agent/` configuration
   - [ ] Document key patterns in `docs/ANALYSIS/UI-PATTERNS.md`
   - [ ] Review existing dashboard.py structure
   - [ ] Review dashboard_models.py patterns

2. **API Development** (Can proceed now - not blocked)
   - [ ] Design API endpoints structure
   - [ ] Create API endpoint specifications
   - [ ] Plan data models (can use existing DashboardViewModel pattern)

3. **Wait for New Package**
   - [ ] Monitor @aibos/design-system repository for updates
   - [ ] Review new package documentation when available
   - [ ] Test new package integration
   - [ ] Update this plan with new package details

### Week 1: Foundation (Days 1-4)

**Day 1: API Endpoints**
- [ ] Add chat endpoint to `dashboard.py` (see Example 1)
- [ ] Add draft endpoints to `dashboard.py`
- [ ] Add audit endpoints to `dashboard.py`
- [ ] Test all endpoints with curl/Postman

**Day 2: Next.js Setup**
- [ ] Initialize Next.js app in `lynx-ai/ui/frontend/`
- [ ] Install TanStack Query
- [ ] Configure API client
- [ ] Test connection to existing dashboard API

**Day 3: Global Button**
- [ ] Add "Ask Lynx" button to dashboard header (HTML)
- [ ] Create `/chat` route in Next.js
- [ ] Test button opens chat page

**Day 4: Chat Interface**
- [ ] Create ChatInterface component (see Example 2)
- [ ] Connect to `/api/chat/query`
- [ ] Test end-to-end chat flow

### Week 2: Core Components (Days 5-10)

**Days 5-6: Contextual Buttons**
- [ ] Create ContextualButton component
- [ ] Add to example entity pages
- [ ] Test context pre-filling

**Days 7-9: Draft Review**
- [ ] Create DraftViewModel (see Example 4)
- [ ] Create DraftList component
- [ ] Create DraftReview component
- [ ] Connect to `/api/drafts` endpoints
- [ ] Test approve/reject flow

**Day 10: Execution Dialogs**
- [ ] Install shadcn/ui Dialog component
- [ ] Create ExecutionDialog component
- [ ] Integrate with draft approval flow
- [ ] Test confirmation workflow

### Week 3: Polish & Integration (Days 11-14)

**Days 11-12: Audit Trail**
- [ ] Create AuditTrail component
- [ ] Add filters (date, tenant, user)
- [ ] Add pagination
- [ ] Connect to `/api/audit/runs`

**Days 13-14: Integration & Testing**
- [ ] End-to-end testing of all flows
- [ ] Error handling and loading states
- [ ] Responsive design testing
- [ ] Update documentation
- [ ] Mark Phase 5 as 100% complete

---

## 🎯 Success Metrics

### Phase 5 Completion Criteria

- [ ] **Global "Ask Lynx" Button** - Visible on all pages, opens chat
- [ ] **Chat Interface** - Users can query Lynx, see responses
- [ ] **Contextual Buttons** - Appear on entity pages, pre-fill context
- [ ] **Draft Review Interface** - List drafts, approve/reject actions work
- [ ] **Execution Dialogs** - High-risk executions require confirmation
- [ ] **Audit Trail** - View recent runs, filterable, paginated

### Technical Quality Criteria

- [ ] All API endpoints tested and documented
- [ ] React components use @aibos/design-system
- [ ] TanStack Query properly configured
- [ ] Error handling implemented
- [ ] Loading states everywhere
- [ ] Responsive design verified
- [ ] No console errors
- [ ] Accessibility basics (keyboard nav, screen reader)

---

## 📊 Risk Mitigation

### Potential Risks & Solutions

**Risk 1: API Integration Complexity**
- **Mitigation:** Start with mock responses, integrate incrementally
- **Fallback:** Use existing dashboard HTML as fallback

**Risk 2: Design System Limitations**
- **Mitigation:** Start with @aibos/design-system, add shadcn/ui only if needed
- **Fallback:** Use inline styles matching existing dashboard

**Risk 3: Timeline Overrun**
- **Mitigation:** Prioritize core chat interface first, others can follow
- **Fallback:** Deliver MVP (chat + global button) in Week 1, rest in Week 2-3

**Risk 4: awesome-llm-apps Patterns Don't Apply**
- **Mitigation:** Study patterns but adapt to our architecture
- **Fallback:** Build from scratch using existing dashboard patterns

---

## 🔗 Integration Points

### Existing Systems to Leverage

1. **Dashboard Infrastructure** (`lynx-ai/lynx/api/dashboard.py`)
   - FastAPI app instance
   - CORS middleware
   - Static file serving
   - View model patterns

2. **Design System** (`lynx-ai/ui/node_modules/@aibos/design-system/`)
   - Button, Card, StatusIndicator components
   - CSS classes (`.na-card`, `.na-btn`, etc.)
   - Design tokens

3. **Status System** (`lynx-ai/lynx/cli/status.py`)
   - `get_lynx_status()` function
   - Status data structure
   - Can be extended for chat/draft/audit data

4. **Storage Layer** (Supabase)
   - Draft storage already exists
   - Audit logging infrastructure
   - Can query for UI data

---

## 📝 Documentation Updates Required

After completion, update:

1. **PRD-STATUS-MATRIX.md** - Mark Phase 5 as 100%
2. **README.md** - Add UI integration section
3. **API Documentation** - Document new endpoints
4. **Component Documentation** - Document React components
5. **DEVELOPMENT-STATUS.md** - Update status

---

**Last Updated:** 2026-01-27  
**Next Review:** When new @aibos/design-system package is available  
**Owner:** Development Team  
**Status:** ⏸️ **BLOCKED** - Waiting for dependency

---

## 📦 Dependency Status

### Current Package
- **Package:** `@aibos/design-system` v1.1.0
- **Status:** Installed but waiting for improved version
- **Location:** `lynx-ai/ui/node_modules/@aibos/design-system/`

### New Package (Expected)
- **Status:** ⏳ **AWAITING RELEASE**
- **Expected Improvements:**
  - Easier to apply/integrate
  - Better React/Next.js support
  - Improved documentation
  - Simplified setup process

### Action Items
- [ ] Monitor @aibos/design-system repository for new release
- [ ] Review new package documentation when available
- [ ] Test new package with Next.js integration
- [ ] Update this plan with new package details
- [ ] Proceed with implementation once package is available

