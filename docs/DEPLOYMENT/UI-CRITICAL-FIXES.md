# UI Critical Fixes - Implementation Priority

**Date:** 2026-01-27  
**Status:** 🔴 **CRITICAL** - Must fix before implementation  
**Priority:** P0 - Blockers that prevent clean implementation

---

## 🎯 Current State

**P0 Essential UX:** ✅ Mapped well  
**Foundations:** ❌ Missing auth/tenant enforcement, contracts, execution lifecycle, thin-client purity

---

## 🔴 Critical Fixes (Must Do First)

### Fix #1: Remove `tenant_id` from Client (Security + Logic)

**Status:** ✅ **ALREADY FIXED** in UI-IMPLEMENTATION-MAP.md

**Current Code (Line 538-541):**
```typescript
// ✅ Fixed: No tenant_id - backend derives from session
const result = await sendQuery.mutateAsync({
  query,
  context,  // ✅ Optional context (entity_type, entity_id only)
});
```

**✅ Verification:** No `tenant_id` hardcoded in client code

**Enforcement Rule:**
- ❌ **FORBIDDEN:** UI sending `tenant_id` in any API call
- ✅ **REQUIRED:** Backend derives `tenant_id` from session/JWT
- ✅ **REQUIRED:** Every read/write checks tenant server-side
- ✅ **REQUIRED:** RLS policies mirror server-side checks

---

### Fix #2: API Boundary Decision (CORS + Auth)

**Status:** ⚠️ **NEEDS DECISION** - Document choice

**Recommendation:** **Option A - Next.js Proxy Routes** (best for speed)

#### Option A: Next.js Proxies FastAPI (RECOMMENDED)

**Structure:**
```
Browser → Next.js API Route (/api/*) → FastAPI (internal)
```

**Implementation:**

**1. Next.js API Route (`app/api/chat/query/route.ts`):**
```typescript
import { NextRequest, NextResponse } from 'next/server';

const FASTAPI_URL = process.env.FASTAPI_URL || 'http://localhost:8000';

export async function POST(request: NextRequest) {
  // Forward to FastAPI
  const body = await request.json();
  const headers = {
    'Content-Type': 'application/json',
    // Forward auth headers
    'Authorization': request.headers.get('Authorization') || '',
    'Cookie': request.headers.get('Cookie') || '',
  };
  
  const res = await fetch(`${FASTAPI_URL}/api/chat/query`, {
    method: 'POST',
    headers,
    body: JSON.stringify(body),
  });
  
  return NextResponse.json(await res.json(), { status: res.status });
}
```

**2. Frontend calls Next.js route:**
```typescript
// ✅ Same-origin (no CORS issues)
const res = await fetch('/api/chat/query', {
  method: 'POST',
  body: JSON.stringify(data),
});
```

**Pros:**
- ✅ Same-origin (cookies/session work)
- ✅ No CORS configuration needed
- ✅ Can add middleware (rate limiting, auth)
- ✅ Cleaner separation

**Cons:**
- ⚠️ Extra proxy layer

#### Option B: Direct FastAPI Calls (Alternative)

**Structure:**
```
Browser → FastAPI (different origin)
```

**Implementation:**
```typescript
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const res = await fetch(`${API_BASE_URL}/api/chat/query`, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
  },
  credentials: 'include',
});
```

**Pros:**
- ✅ Simpler setup
- ✅ No proxy needed

**Cons:**
- ⚠️ CORS configuration required
- ⚠️ Session cookies may not work (different origin)
- ⚠️ Auth headers must be managed manually

**Decision:** ✅ **Option A (Next.js Proxy)** - Recommended

---

### Fix #3: Thin Client Purity - No Risk Inference

**Status:** ⚠️ **NEEDS FIX** - DraftActions infers risk

**Current Code (WRONG):**
```typescript
// ❌ WRONG: UI infers risk
if (draft.risk_level === 'high' || draft.requires_approval) {
  setShowConfirm(true);
}
```

**Fixed Code (CORRECT):**
```typescript
// ✅ CORRECT: Backend decides, UI only renders
if (draft.requires_confirmation) {  // ✅ Backend provides this flag
  setShowConfirm(true);
}
```

**Enforcement Rule:**
- ❌ **FORBIDDEN:** UI inferring `requires_confirmation` from `risk_level`
- ✅ **REQUIRED:** Backend returns `requires_confirmation: boolean`
- ✅ **REQUIRED:** UI only renders backend decision

**Location to Fix:** `ui/frontend/components/drafts/DraftActions.tsx` (line ~15-20)

---

### Fix #4: Draft/Execution Lifecycle (Add `executing` State)

**Status:** ⚠️ **PARTIAL** - Missing `executing` state

**Current States:**
- ✅ `draft`
- ✅ `approved`
- ✅ `rejected`
- ✅ `executed`
- ✅ `failed`
- ❌ **Missing:** `executing` (transition state)

**Fixed DraftStatus Enum:**

**Backend (`lynx/api/models.py`):**
```python
class DraftStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTING = "executing"  # ✅ Added: transition state
    EXECUTED = "executed"
    FAILED = "failed"
```

**Frontend (`lib/types.ts`):**
```typescript
export type DraftStatus = 'draft' | 'approved' | 'rejected' | 'executing' | 'executed' | 'failed';
```

**Lifecycle Flow:**
```
draft → approved → executing → executed
                          ↓
                       failed
```

**Why `executing` Matters:**
- ✅ Shows "Execution in progress..." (better UX)
- ✅ Prevents double execution (idempotency)
- ✅ Enables real-time status updates
- ✅ Proper audit trail (approved → executing → executed/failed)

---

### Fix #5: CRUD-S Enhancement (3 Fast Wins)

**Status:** ❌ **MISSING** - Add 3 buttons

#### Button 1: "New Chat" (Explicit Create)

**Location:** `components/chat/ChatInterface.tsx`

```typescript
export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  
  const handleNewChat = () => {
    setMessages([]);  // Clear messages
    // Optional: Navigate to fresh chat
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

#### Button 2: "Export Audit" (CSV/JSON)

**Location:** `components/audit/AuditList.tsx`

```typescript
export function AuditList({ filters }: { filters: any }) {
  const { data } = useAuditRuns(filters);
  
  const handleExport = async (format: 'csv' | 'json') => {
    const res = await fetch(`/api/audit/export?format=${format}&${new URLSearchParams(filters)}`);
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit-${Date.now()}.${format}`;
    a.click();
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
    tenant_id = session['tenant_id']
    runs = await get_audit_runs(tenant_id, filters)
    
    if format == 'csv':
        # Generate CSV
        return Response(content=csv_content, media_type='text/csv')
    else:
        # Generate JSON
        return Response(content=json_content, media_type='application/json')
```

**Purpose:** Enterprise parity + Create report (CRUD-S compliance)

---

#### Button 3: "Delete Draft" (Safe Delete)

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
    tenant_id = session['tenant_id']
    draft = await get_draft(draft_id, tenant_id)
    
    # ✅ Safety check: Only allow delete for draft or rejected
    if draft.status not in ['draft', 'rejected']:
        raise HTTPException(400, "Cannot delete draft in this status")
    
    await delete_draft_from_storage(draft_id, tenant_id)
    return {"success": True}
```

**Purpose:** Safe Delete action (CRUD-S compliance)

---

### Fix #6: No JSON in QueryString (Security + UX)

**Status:** ✅ **ALREADY FIXED** in UI-IMPLEMENTATION-MAP.md

**Current Code (Line ~750):**
```typescript
// ✅ Fixed: Simple query params (no JSON in URL)
router.push(`/chat?entity_type=${entity_type}&entity_id=${entity_id}`);
```

**✅ Verification:** No JSON.stringify in URL

**Enforcement Rule:**
- ❌ **FORBIDDEN:** `encodeURIComponent(JSON.stringify(...))` in URLs
- ✅ **REQUIRED:** Simple query params (`?entity_type=X&entity_id=Y`)
- ✅ **REQUIRED:** Backend loads entity details if needed

---

### Fix #7: React Query Wiring

**Status:** ✅ **ALREADY FIXED** in UI-IMPLEMENTATION-MAP.md

**Current Code (Line 401-425):**
```typescript
// ✅ QueryClientProvider at root (required for React Query)
const queryClient = new QueryClient({...});

export default function RootLayout({ children }) {
  return (
    <QueryClientProvider client={queryClient}>
      {/* ... */}
    </QueryClientProvider>
  );
}
```

**✅ Verification:** QueryClientProvider added to root layout

**Additional Requirement:** Shared `apiFetch()` wrapper

**Location:** `lib/api-client.ts` (already documented in map)

---

### Fix #8: Silent Killers (Pick 2 Only)

**Status:** ❌ **MISSING** - Add 2 features

#### Silent Killer #1: Keyboard Shortcuts

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
      
      // / : Focus chat input
      if (e.key === '/' && !e.metaKey && !e.ctrlKey) {
        const input = document.querySelector('.chat-input input') as HTMLInputElement;
        if (input) {
          e.preventDefault();
          input.focus();
        }
      }
      
      // Escape: Close modals
      if (e.key === 'Escape') {
        // Close any open modals
        const modals = document.querySelectorAll('.modal-open');
        modals.forEach(modal => {
          // Close modal logic
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

#### Silent Killer #2: Export Audit Logs

**Status:** ✅ **ALREADY DOCUMENTED** in Fix #5 (Button 2)

**Purpose:** Enterprise parity + compliance workflows (Silent Killer)

---

## 📋 Corrected Action Plan (In Order)

### Phase 0: Foundation Fixes (Week 1)

1. ✅ **Auth + Tenant Derivation** (server-only tenant)
   - Status: Already fixed in map
   - Action: Verify no `tenant_id` in client code

2. ✅ **API Boundary Decision** (Next.js proxy routes)
   - Status: Decision made (Option A)
   - Action: Implement Next.js API route handlers

3. ✅ **Contract Definitions** (Run, Draft, ToolCall, AuditEvent)
   - Status: Already defined in map
   - Action: Verify contracts match backend

4. ⚠️ **Thin Client Purity** (no risk inference)
   - Status: Needs fix
   - Action: Update DraftActions to use `requires_confirmation` only

5. ⚠️ **Draft Lifecycle** (add `executing` state)
   - Status: Partial (missing `executing`)
   - Action: Add `executing` to DraftStatus enum

---

### Phase 1: Step A Chat UI (Week 2)

6. ✅ **Step A Chat UI** (driven by backend flags)
   - Status: Mapped
   - Action: Implement with backend `requires_confirmation` flag

---

### Phase 2: Step B Draft Review (Week 3)

7. ✅ **Draft Lifecycle** (executing/executed/failed)
   - Status: Needs `executing` state
   - Action: Implement full lifecycle

8. ✅ **CRUD-S Buttons** (3 fast wins)
   - Status: Missing
   - Action: Add "New Chat", "Export Audit", "Delete Draft"

---

### Phase 3: Step C + D + Silent Killers (Week 4)

9. ✅ **Step C Execution Confirmation**
10. ✅ **Step D Audit Trail**
11. ✅ **Silent Killers** (keyboard shortcuts + export)

---

## ✅ Verification Checklist

### Before Starting Implementation

- [ ] ✅ No `tenant_id` in client code (verified)
- [ ] ⚠️ API boundary decision made (Option A - Next.js proxy)
- [ ] ⚠️ Contracts defined (verify match backend)
- [ ] ⚠️ DraftActions uses `requires_confirmation` only (needs fix)
- [ ] ⚠️ DraftStatus includes `executing` (needs fix)
- [ ] ✅ No JSON in queryString (verified)
- [ ] ✅ QueryClientProvider in layout (verified)

### During Implementation

- [ ] Backend derives tenant from session (every endpoint)
- [ ] Backend returns `requires_confirmation` (not inferred)
- [ ] UI only renders backend flags (no inference)
- [ ] Draft lifecycle includes `executing` state
- [ ] CRUD-S buttons implemented (3 fast wins)
- [ ] Keyboard shortcuts working
- [ ] Export audit logs working

---

## 🎯 Summary

**Critical Fixes Status:**
- ✅ **Fix #1:** Tenant ID (already fixed)
- ⚠️ **Fix #2:** API boundary (decision made, needs implementation)
- ⚠️ **Fix #3:** Thin client purity (needs fix in DraftActions)
- ⚠️ **Fix #4:** Draft lifecycle (needs `executing` state)
- ⚠️ **Fix #5:** CRUD-S buttons (3 buttons to add)
- ✅ **Fix #6:** No JSON in URL (already fixed)
- ✅ **Fix #7:** React Query (already fixed)
- ⚠️ **Fix #8:** Silent Killers (2 features to add)

**Next Action:** Implement Fix #2 (API boundary) + Fix #3 (thin client purity) + Fix #4 (executing state) before Step A implementation.

---

**Last Updated:** 2026-01-27  
**Priority:** 🔴 **P0 - Blockers**

