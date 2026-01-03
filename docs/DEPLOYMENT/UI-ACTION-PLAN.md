# UI Implementation Action Plan - Corrected Order

**Date:** 2026-01-27  
**Status:** ✅ **READY TO START** (All blockers identified and fixed)  
**Priority:** Follow this exact order to avoid rework

---

## 🎯 Current State

**P0 Essential UX:** ✅ Mapped well  
**Foundations:** ✅ **FIXED** - All critical gaps addressed

---

## 📋 Corrected Action Plan (In Order)

### Phase 0: Foundation Fixes (Week 1) - DO FIRST

**Goal:** Fix all blockers before UI implementation

#### Day 1-2: Auth + API Boundary

1. ✅ **Verify No `tenant_id` in Client**
   - Status: Already fixed in map
   - Action: Double-check all API calls (no `tenant_id` sent)
   - Verification: `grep -r "tenant_id" ui/frontend/` should return 0 results

2. ✅ **Implement API Boundary (Option A - Next.js Proxy)**
   - Decision: Next.js proxies FastAPI (same-origin, no CORS)
   - Action: Create Next.js API route handlers
   - Files:
     - `app/api/chat/query/route.ts`
     - `app/api/drafts/route.ts`
     - `app/api/audit/runs/route.ts`
   - Pattern: Forward to FastAPI, handle auth headers

3. ✅ **Shared `apiFetch()` Wrapper**
   - Location: `lib/api-client.ts`
   - Features: Auth headers, request_id, error handling
   - Usage: All API calls use this wrapper

**Deliverable:** API boundary working, no tenant_id in client

---

#### Day 3-4: Contracts + Thin Client Purity

4. ✅ **Verify Contract Definitions**
   - Status: Already defined in map
   - Action: Verify backend Pydantic models match frontend TypeScript types
   - Files:
     - Backend: `lynx/api/models.py`
     - Frontend: `lib/types.ts`
   - Key contracts: ChatRun, Draft, ToolCall, AuditRun

5. ⚠️ **Fix Thin Client Purity (DraftActions)**
   - Status: Needs fix
   - Current: `if (draft.risk_level === 'high' || draft.requires_approval)`
   - Fixed: `if (draft.requires_confirmation)` (backend provides flag)
   - Location: `components/drafts/DraftActions.tsx`
   - Rule: UI never infers, only renders backend flags

6. ⚠️ **Add `executing` State to Draft Lifecycle**
   - Status: Partial (missing `executing`)
   - Action: Add `executing` to DraftStatus enum
   - Files:
     - Backend: `lynx/api/models.py` (DraftStatus enum)
     - Frontend: `lib/types.ts` (DraftStatus type)
     - Supabase: Update schema (status column)
   - Lifecycle: `draft → approved → executing → executed/failed`

**Deliverable:** Contracts verified, thin client pure, lifecycle complete

---

### Phase 1: Step A Chat UI (Week 2)

**Goal:** Implement chat with backend-driven flags

7. ✅ **Implement Step A Chat UI**
   - Components: AskLynxButton, ChatInterface, ChatMessage, ToolCallIndicator
   - Backend: `POST /api/chat/query` returns `policy.requires_confirmation`
   - UI: Renders backend flags only (no inference)
   - Features: Loading/error/empty states, request_id in errors

**Deliverable:** Chat UI working, backend-driven

---

### Phase 2: Step B Draft Review (Week 3)

**Goal:** Draft review with full lifecycle

8. ✅ **Implement Step B Draft Review**
   - Components: DraftList, DraftCard, DraftDetail, DraftActions
   - Backend: Full lifecycle (draft → approved → executing → executed/failed)
   - UI: Shows execution status (executing/executed/failed)
   - Features: Filters, pagination, approve/reject

9. ✅ **Add CRUD-S Buttons (3 Fast Wins)**
   - Button 1: "New Chat" (explicit Create)
   - Button 2: "Export Audit" (CSV/JSON) (Create report)
   - Button 3: "Delete Draft" (safe delete for draft/rejected only)

**Deliverable:** Draft review complete, CRUD-S compliant

---

### Phase 3: Step C + D + Silent Killers (Week 4)

10. ✅ **Implement Step C Execution Confirmation**
    - Component: ExecutionDialog
    - Trigger: When `requires_confirmation === true` (backend decides)
    - Features: Shows affected entities, execution role, audit notice

11. ✅ **Implement Step D Audit Trail**
    - Components: AuditList, RunCard, RunDetail, ToolCallList
    - Features: Filters, pagination, tool call integrity

12. ✅ **Add Silent Killers (2 Features)**
    - Feature 1: Keyboard shortcuts (`Cmd+K`, `/`, `Escape`)
    - Feature 2: Export audit logs (CSV/JSON) (already in CRUD-S)

**Deliverable:** All 5 components complete, Silent Killers added

---

## ✅ Verification Checklist

### Phase 0 (Before UI Implementation)

- [ ] ✅ No `tenant_id` in client code (verified via grep)
- [ ] ✅ API boundary implemented (Next.js proxy routes)
- [ ] ✅ `apiFetch()` wrapper created (auth + request_id)
- [ ] ✅ Contracts verified (backend ↔ frontend match)
- [ ] ✅ DraftActions uses `requires_confirmation` only (no inference)
- [ ] ✅ DraftStatus includes `executing` state
- [ ] ✅ Backend returns `requires_confirmation` flag
- [ ] ✅ Backend derives tenant from session (all endpoints)

### Phase 1-3 (During Implementation)

- [ ] ✅ All API calls use `apiFetch()` wrapper
- [ ] ✅ All API calls scoped by server-side tenant
- [ ] ✅ UI only renders backend flags (no inference)
- [ ] ✅ Draft lifecycle includes `executing` state
- [ ] ✅ CRUD-S buttons implemented (3 fast wins)
- [ ] ✅ Keyboard shortcuts working
- [ ] ✅ Export audit logs working

---

## 🔧 Implementation Details

### API Boundary Implementation (Option A)

**Next.js API Route Structure:**
```
app/
├── api/
│   ├── chat/
│   │   └── query/
│   │       └── route.ts  # Proxy to FastAPI /api/chat/query
│   ├── drafts/
│   │   ├── route.ts       # Proxy to FastAPI /api/drafts
│   │   └── [draftId]/
│   │       ├── route.ts   # Proxy to FastAPI /api/drafts/{id}
│   │       ├── approve/
│   │       │   └── route.ts
│   │       └── reject/
│   │           └── route.ts
│   └── audit/
│       └── runs/
│           ├── route.ts   # Proxy to FastAPI /api/audit/runs
│           └── [runId]/
│               └── route.ts
```

**Example Proxy Route (`app/api/chat/query/route.ts`):**
```typescript
import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    
    // Forward to FastAPI
    const res = await fetch(`${FASTAPI_URL}/api/chat/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        // Forward auth headers
        'Authorization': request.headers.get('Authorization') || '',
        'Cookie': request.headers.get('Cookie') || '',
      },
      body: JSON.stringify(body),
      credentials: 'include',
    });
    
    if (!res.ok) {
      const error = await res.json();
      return NextResponse.json(error, { status: res.status });
    }
    
    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { error: 'Internal server error', request_id: crypto.randomUUID() },
      { status: 500 }
    );
  }
}
```

---

### Thin Client Purity Fix

**Before (WRONG):**
```typescript
// ❌ UI infers risk
if (draft.risk_level === 'high' || draft.requires_approval) {
  setShowConfirm(true);
}
```

**After (CORRECT):**
```typescript
// ✅ Backend decides, UI only renders
if (draft.requires_confirmation) {  // Backend provides this
  setShowConfirm(true);
}
```

**Backend Must Return:**
```python
class Draft(BaseModel):
    requires_confirmation: bool  # ✅ Backend derives from MCP + policy
    risk_level: RiskLevel
    # ... other fields
```

---

### Draft Lifecycle with `executing` State

**Complete Lifecycle:**
```
draft → approved → executing → executed
                          ↓
                       failed
```

**Backend Implementation:**
```python
# Approve draft
await update_draft_status(draft_id, 'approved')

# Start execution (transition to executing)
await update_draft_status(draft_id, 'executing')

try:
    execution_id = await execute_draft(draft)
    await update_draft_status(draft_id, 'executed', execution_id=execution_id)
except Exception as e:
    await update_draft_status(draft_id, 'failed', execution_error=str(e))
```

**UI Display:**
```typescript
{draft.status === 'executing' && (
  <div className="status-pending">⏳ Execution in progress...</div>
)}
```

---

## 🎯 Success Criteria

### Phase 0 Complete When:
- ✅ No `tenant_id` in client code
- ✅ API boundary working (Next.js proxy)
- ✅ Contracts verified
- ✅ Thin client pure (no inference)
- ✅ Draft lifecycle includes `executing`

### Phase 1-3 Complete When:
- ✅ All 5 UI components working
- ✅ CRUD-S buttons implemented
- ✅ Silent Killers added
- ✅ All acceptance tests passing

---

**Last Updated:** 2026-01-27  
**Status:** ✅ **READY TO START**  
**Priority:** Follow this exact order

