# Next.js Foundation - Complete

**Date:** 2026-01-27  
**Status:** ✅ **COMPLETE** - Next.js app, proxy routes, and API client ready  
**Progress:** Phase 0 Complete (10/10 tasks) - Ready for UI components

---

## ✅ Completed (Phase 0 - All Tasks)

### 1. Next.js App Structure ✅

**Files Created:**
- ✅ `ui/frontend/package.json` - Next.js 14 + TanStack Query
- ✅ `ui/frontend/tsconfig.json` - TypeScript configuration
- ✅ `ui/frontend/next.config.js` - Next.js configuration
- ✅ `ui/frontend/app/layout.tsx` - Root layout with QueryClientProvider
- ✅ `ui/frontend/app/globals.css` - Neo-Analog theme CSS variables

**Key Features:**
- ✅ QueryClientProvider in root layout (required for React Query)
- ✅ Neo-Analog theme CSS variables (void/paper/lux/gold)
- ✅ TypeScript configured with path aliases (`@/*`)

---

### 2. API Client Wrapper ✅

**File:** `ui/frontend/lib/apiClient.ts`

**Features:**
- ✅ `apiFetch()` - Single wrapper for all API calls
- ✅ Same-origin (calls Next.js proxy routes, not FastAPI directly)
- ✅ Automatically includes auth cookies (same-origin)
- ✅ Preserves `request_id` from backend errors (for debugging)
- ✅ Throws typed errors
- ✅ `getRequestId()` helper for error debugging

**Usage:**
```typescript
import { apiFetch } from '@/lib/apiClient';

const data = await apiFetch<ChatQueryResponse>('/api/chat/query', {
  method: 'POST',
  body: { query: '...' },
});
```

---

### 3. Next.js Proxy Routes ✅

**All proxy routes created (thin proxies, no business logic):**

#### Chat Routes
- ✅ `app/api/chat/query/route.ts` - Proxies to FastAPI `/api/chat/query`

#### Draft Routes
- ✅ `app/api/drafts/route.ts` - Proxies to FastAPI `/api/drafts`
- ✅ `app/api/drafts/[draftId]/route.ts` - Proxies to FastAPI `/api/drafts/{draftId}`
- ✅ `app/api/drafts/[draftId]/approve/route.ts` - Proxies to FastAPI `/api/drafts/{draftId}/approve`
- ✅ `app/api/drafts/[draftId]/reject/route.ts` - Proxies to FastAPI `/api/drafts/{draftId}/reject`

#### Audit Routes
- ✅ `app/api/audit/runs/route.ts` - Proxies to FastAPI `/api/audit/runs`
- ✅ `app/api/audit/runs/[runId]/route.ts` - Proxies to FastAPI `/api/audit/runs/{runId}`
- ✅ `app/api/audit/runs/export/route.ts` - Proxies to FastAPI `/api/audit/runs/export`

**All Proxy Routes:**
- ✅ Forward body/query params to FastAPI
- ✅ Forward auth cookies automatically (same-origin)
- ✅ Add `X-Request-ID` header for debugging
- ✅ Handle errors with request_id preservation
- ✅ Use `FASTAPI_URL` env variable (default: `http://localhost:8000`)

---

## 🔐 Critical Fixes Applied

### Fix A: No `tenant_id` in Client ✅

**Rule:** Tenant comes from session **only** (backend derives).

**Implementation:**
- ✅ All API calls use `apiFetch()` (no tenant_id in payload)
- ✅ Proxy routes forward to FastAPI (backend derives tenant from session)
- ✅ No `tenant_id` in any client code

**Example (CORRECT):**
```typescript
// ✅ Client sends only query + context (no tenant_id)
await apiFetch('/api/chat/query', {
  method: 'POST',
  body: { query: '...', context: {...} },  // No tenant_id
});
```

**Example (WRONG - NOT IMPLEMENTED):**
```typescript
// ❌ NEVER DO THIS:
body: { query: '...', tenant_id: 'current-tenant' }  // FORBIDDEN
```

---

### Fix B: No Risk Inference on Client ✅

**Rule:** UI only uses backend `requires_confirmation` boolean.

**Implementation:**
- ✅ Backend returns `policy.requires_confirmation` in chat responses
- ✅ Backend returns `requires_confirmation` in draft models
- ✅ UI will only check `requires_confirmation` (not `risk_level === 'high'`)

**Example (CORRECT - to be implemented in components):**
```typescript
// ✅ UI only renders backend decision
if (draft.requires_confirmation) {  // Backend provides this
  setShowConfirm(true);
}
```

**Example (WRONG - NOT IMPLEMENTED):**
```typescript
// ❌ NEVER DO THIS:
if (draft.risk_level === 'high' || draft.requires_approval) {  // FORBIDDEN
  setShowConfirm(true);
}
```

---

## 📋 Environment Configuration

### Required Environment Variables

**File:** `ui/frontend/.env.local` (create from `.env.local.example`)

```bash
# FastAPI Backend URL (for Next.js proxy routes)
FASTAPI_URL=http://localhost:8000

# Next.js Configuration
NEXT_PUBLIC_APP_URL=http://localhost:3000
```

**Production:**
- Set `FASTAPI_URL` to your FastAPI deployment URL (Railway, Vercel, etc.)

---

## 🎯 Next Steps (UI Components)

### Implementation Order (Per Methodology)

1. **Step A: Chat Page** (P0 Essential)
   - Global "Ask Lynx" button
   - Chat interface
   - Tool call indicators

2. **Step D: Audit Page** (P0 Essential + Silent Killer)
   - Audit list with filters
   - Run detail view
   - Export button (CSV/JSON) - **Silent Killer feature**

3. **Step B: Draft List** (P0 Essential)
   - Draft list with filters
   - Draft detail view
   - Approve/reject actions

4. **Step C: Execution Dialog** (P0 Essential)
   - Confirmation modal
   - Driven by backend `requires_confirmation` flag

---

## ✅ Verification Checklist

### Foundation
- [x] ✅ Next.js app created
- [x] ✅ QueryClientProvider in layout
- [x] ✅ API client wrapper created
- [x] ✅ All proxy routes created
- [x] ✅ Environment variables documented

### Security & Doctrine
- [x] ✅ No `tenant_id` in client code
- [x] ✅ Proxy routes forward auth cookies
- [x] ✅ Backend derives tenant from session
- [x] ✅ Thin client doctrine preserved

### Ready for UI
- [x] ✅ API client ready for React Query hooks
- [x] ✅ Proxy routes ready for frontend calls
- [x] ✅ Theme CSS variables defined
- [x] ✅ TypeScript configured

---

## 📊 Files Created

### Next.js App
- ✅ `ui/frontend/package.json`
- ✅ `ui/frontend/tsconfig.json`
- ✅ `ui/frontend/next.config.js`
- ✅ `ui/frontend/app/layout.tsx`
- ✅ `ui/frontend/app/globals.css`

### API Client
- ✅ `ui/frontend/lib/apiClient.ts`

### Proxy Routes (8 routes)
- ✅ `app/api/chat/query/route.ts`
- ✅ `app/api/drafts/route.ts`
- ✅ `app/api/drafts/[draftId]/route.ts`
- ✅ `app/api/drafts/[draftId]/approve/route.ts`
- ✅ `app/api/drafts/[draftId]/reject/route.ts`
- ✅ `app/api/audit/runs/route.ts`
- ✅ `app/api/audit/runs/[runId]/route.ts`
- ✅ `app/api/audit/runs/export/route.ts`

---

## 🚀 Ready to Start UI Implementation

**Phase 0 Status:** ✅ **100% COMPLETE** (10/10 tasks)

**Next Action:** Implement Step A (Chat Page) with:
- Global "Ask Lynx" button
- Chat interface using `apiFetch()`
- Tool call indicators
- Backend-driven `requires_confirmation` flag

---

**Last Updated:** 2026-01-27  
**Status:** ✅ **FOUNDATION COMPLETE** - Ready for UI components

