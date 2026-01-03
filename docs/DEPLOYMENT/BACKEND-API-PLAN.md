# Backend API Development Plan

**Date:** 2026-01-27  
**Status:** ✅ **READY TO START**  
**Priority:** 🔴 **HIGH** - Unblocks UI work  
**Architecture:** Lynx API (separate from Kernel API)

---

## 🎯 Objective

Develop backend API endpoints for UI integration while maintaining proper separation from Kernel API.

**Key Principle:** Lynx API endpoints are **Lynx-specific** and stay in `lynx-ai/lynx/api/`. They may **call Kernel APIs** when needed, but are **separate services**.

---

## 🏗️ Architecture & Boundaries

### System Separation

```
┌─────────────────────────────────────────────────────────┐
│                    User Interface                        │
│                  (React/Next.js UI)                     │
└───────────────────────┬─────────────────────────────────┘
                        │
                        │ HTTP API Calls
                        │
┌───────────────────────▼─────────────────────────────────┐
│              Lynx API (FastAPI)                         │
│         lynx-ai/lynx/api/dashboard.py                    │
│                                                          │
│  Endpoints:                                             │
│  - POST /api/chat/query                                 │
│  - GET /api/drafts                                      │
│  - POST /api/drafts/{id}/approve                        │
│  - GET /api/audit/runs                                 │
└───────────────────────┬─────────────────────────────────┘
                        │
                        │ When needed: Calls Kernel API
                        │ (for metadata, permissions, etc.)
                        │
┌───────────────────────▼─────────────────────────────────┐
│            Kernel API (AIBOS-KERNEL)                    │
│         Separate Next.js Portal Service                 │
│                                                          │
│  Endpoints:                                             │
│  - GET /metadata/{entity_type}                         │
│  - GET /schema/{entity_type}                           │
│  - POST /permissions/check                             │
│  - GET /tenants/{id}/customizations                    │
└─────────────────────────────────────────────────────────┘
```

### Boundary Rules

**✅ Lynx API (This Plan):**
- **Location:** `lynx-ai/lynx/api/`
- **Purpose:** UI integration endpoints (chat, drafts, audit)
- **Scope:** Lynx-specific functionality
- **Can Call:** Kernel API when needed (metadata, permissions)
- **Owns:** Lynx Run tracking, draft management, audit logs

**✅ Kernel API (Separate System):**
- **Location:** AIBOS-KERNEL Next.js Portal (separate repo)
- **Purpose:** SSOT for metadata, schema, permissions
- **Scope:** Business logic, entity definitions
- **Owns:** Entity metadata, permissions, tenant configs

**❌ What NOT to Do:**
- ❌ Don't put Lynx UI endpoints in Kernel
- ❌ Don't duplicate Kernel functionality in Lynx
- ❌ Don't bypass Kernel API (Law 1: Kernel Supremacy)
- ❌ Don't mix concerns (Lynx UI ≠ Kernel SSOT)

---

## 📋 API Endpoint Specifications

### 1. Chat API Endpoints

**Location:** `lynx-ai/lynx/api/dashboard.py` (add to existing file)

#### POST /api/chat/query

**Purpose:** Submit a chat query to Lynx AI

**Request:**
```json
{
  "query": "What documents are pending approval?",
  "context": {
    "entity_type": "document",
    "entity_id": "doc_123"
  },
  "tenant_id": "tenant_abc"
}
```

**Response:**
```json
{
  "run_id": "run_xyz123",
  "response": "You have 3 documents pending approval...",
  "tool_calls": [
    {
      "tool_id": "docs.domain.registry.read",
      "status": "success",
      "result": "..."
    }
  ],
  "status": "completed",
  "created_at": "2026-01-27T10:00:00Z"
}
```

**Implementation Notes:**
- Calls Lynx core runtime to process query
- May call Kernel API for metadata/permissions (via `KernelAPI` client)
- Creates audit log entry (Lynx Run)
- Returns immediately with run_id (async processing)

**Boundary:** ✅ Lynx API endpoint, calls Kernel when needed

---

#### GET /api/chat/runs/{run_id}

**Purpose:** Get status of a chat run

**Response:**
```json
{
  "run_id": "run_xyz123",
  "status": "completed",
  "response": "You have 3 documents...",
  "tool_calls": [...],
  "created_at": "2026-01-27T10:00:00Z",
  "completed_at": "2026-01-27T10:00:15Z"
}
```

**Boundary:** ✅ Lynx API endpoint, reads from Lynx audit storage

---

### 2. Draft Management API Endpoints

**Location:** `lynx-ai/lynx/api/dashboard.py`

#### GET /api/drafts

**Purpose:** List drafts for a tenant

**Query Parameters:**
- `tenant_id` (required)
- `status` (optional): `draft`, `approved`, `rejected`
- `type` (optional): `document`, `workflow`, `payment`, etc.
- `limit` (optional, default: 50)
- `offset` (optional, default: 0)

**Response:**
```json
{
  "drafts": [
    {
      "draft_id": "draft_abc123",
      "type": "document",
      "status": "draft",
      "risk_level": "medium",
      "created_at": "2026-01-27T09:00:00Z",
      "created_by": "user_123"
    }
  ],
  "total": 15,
  "limit": 50,
  "offset": 0
}
```

**Implementation Notes:**
- Reads from Lynx draft storage (Supabase)
- Tenant-scoped (enforced in query)
- May call Kernel API to enrich with metadata (optional)

**Boundary:** ✅ Lynx API endpoint, reads from Lynx storage

---

#### GET /api/drafts/{draft_id}

**Purpose:** Get draft details

**Response:**
```json
{
  "draft_id": "draft_abc123",
  "type": "document",
  "payload": {
    "document_type": "request",
    "title": "New Document Request",
    ...
  },
  "status": "draft",
  "risk_level": "medium",
  "created_at": "2026-01-27T09:00:00Z",
  "created_by": "user_123",
  "metadata": {
    "tool_id": "docs.cluster.draft.create",
    "tool_version": "1.0.0"
  }
}
```

**Boundary:** ✅ Lynx API endpoint, reads from Lynx storage

---

#### POST /api/drafts/{draft_id}/approve

**Purpose:** Approve a draft (triggers execution if needed)

**Request:**
```json
{
  "approved_by": "user_123",
  "notes": "Looks good, approved"
}
```

**Response:**
```json
{
  "success": true,
  "draft_id": "draft_abc123",
  "status": "approved",
  "execution_id": "exec_xyz789",
  "executed_at": "2026-01-27T10:00:00Z"
}
```

**Implementation Notes:**
- Updates draft status in Lynx storage
- If execution required, calls appropriate Cell MCP tool
- Creates audit log entry
- May call Kernel API for permission check (via `KernelAPI`)

**Boundary:** ✅ Lynx API endpoint, may call Kernel for permissions

---

#### POST /api/drafts/{draft_id}/reject

**Purpose:** Reject a draft

**Request:**
```json
{
  "rejected_by": "user_123",
  "reason": "Does not meet requirements"
}
```

**Response:**
```json
{
  "success": true,
  "draft_id": "draft_abc123",
  "status": "rejected",
  "rejected_at": "2026-01-27T10:00:00Z"
}
```

**Boundary:** ✅ Lynx API endpoint, updates Lynx storage

---

### 3. Execution API Endpoints

**Location:** `lynx-ai/lynx/api/dashboard.py`

#### POST /api/executions/{execution_id}/confirm

**Purpose:** Confirm a high-risk execution

**Request:**
```json
{
  "confirmed_by": "user_123",
  "notes": "Confirmed after review"
}
```

**Response:**
```json
{
  "success": true,
  "execution_id": "exec_xyz789",
  "status": "confirmed",
  "confirmed_at": "2026-01-27T10:00:00Z"
}
```

**Implementation Notes:**
- Updates execution status
- May trigger actual execution (if pending)
- Creates audit log entry
- May call Kernel API for final permission check

**Boundary:** ✅ Lynx API endpoint, manages Lynx executions

---

#### GET /api/executions/{execution_id}

**Purpose:** Get execution details

**Response:**
```json
{
  "execution_id": "exec_xyz789",
  "status": "completed",
  "result": {
    "success": true,
    "output": "..."
  },
  "tool_calls": [...],
  "created_at": "2026-01-27T10:00:00Z",
  "completed_at": "2026-01-27T10:00:15Z"
}
```

**Boundary:** ✅ Lynx API endpoint, reads from Lynx audit storage

---

### 4. Audit Trail API Endpoints

**Location:** `lynx-ai/lynx/api/dashboard.py`

#### GET /api/audit/runs

**Purpose:** List Lynx Runs (audit trail)

**Query Parameters:**
- `tenant_id` (required)
- `limit` (optional, default: 50)
- `offset` (optional, default: 0)
- `from_date` (optional): ISO 8601 date
- `to_date` (optional): ISO 8601 date
- `user_id` (optional): Filter by user

**Response:**
```json
{
  "runs": [
    {
      "run_id": "run_xyz123",
      "user_id": "user_123",
      "tenant_id": "tenant_abc",
      "query": "What documents are pending?",
      "response": "You have 3 documents...",
      "tool_calls": [...],
      "created_at": "2026-01-27T10:00:00Z"
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

**Boundary:** ✅ Lynx API endpoint, reads from Lynx audit storage

---

#### GET /api/audit/runs/{run_id}

**Purpose:** Get detailed run information

**Response:**
```json
{
  "run_id": "run_xyz123",
  "user_id": "user_123",
  "tenant_id": "tenant_abc",
  "query": "What documents are pending?",
  "response": "You have 3 documents...",
  "tool_calls": [
    {
      "tool_id": "docs.domain.registry.read",
      "status": "success",
      "input": {...},
      "output": {...},
      "duration_ms": 150
    }
  ],
  "created_at": "2026-01-27T10:00:00Z",
  "completed_at": "2026-01-27T10:00:15Z"
}
```

**Boundary:** ✅ Lynx API endpoint, reads from Lynx audit storage

---

## 🏗️ Implementation Structure

### File Organization

```
lynx-ai/
├── lynx/
│   ├── api/
│   │   ├── dashboard.py              # Existing dashboard (extend this)
│   │   ├── chat_routes.py            # NEW: Chat endpoints
│   │   ├── draft_routes.py            # NEW: Draft endpoints
│   │   ├── execution_routes.py       # NEW: Execution endpoints
│   │   ├── audit_routes.py           # NEW: Audit endpoints
│   │   └── models.py                 # NEW: Request/Response models
│   │
│   └── integration/
│       └── kernel/
│           ├── client.py             # Existing: Kernel API client
│           └── lite.py               # Existing: Kernel lite mode
```

### Boundary Enforcement

**✅ Lynx API Layer (`lynx/api/`):**
- Handles HTTP requests/responses
- Validates input
- Calls Lynx core runtime
- Calls Kernel API when needed (via `KernelAPI` client)
- Manages Lynx-specific data (runs, drafts, executions)

**✅ Kernel Integration (`lynx/integration/kernel/`):**
- **DO NOT modify** - This is the boundary layer
- Use existing `KernelAPI` client when needed
- Follow Law 1: Kernel Supremacy (always call Kernel for SSOT)

---

## 📝 Implementation Plan

### Phase 1: Models & Structure (Day 1)

**Tasks:**
1. [ ] Create `lynx/api/models.py` with request/response models
2. [ ] Extend `dashboard_models.py` with chat/draft/audit models
3. [ ] Define data contracts (Pydantic models)
4. [ ] Document API contracts

**Deliverable:** Models defined, contracts documented

---

### Phase 2: Chat API (Day 2)

**Tasks:**
1. [ ] Create `lynx/api/chat_routes.py`
2. [ ] Implement `POST /api/chat/query`
   - Integrate with Lynx core runtime
   - Call Kernel API if needed (metadata/permissions)
   - Create audit log entry
3. [ ] Implement `GET /api/chat/runs/{run_id}`
4. [ ] Add routes to `dashboard.py`
5. [ ] Write API tests

**Deliverable:** Chat API working, tested

---

### Phase 3: Draft API (Day 3)

**Tasks:**
1. [ ] Create `lynx/api/draft_routes.py`
2. [ ] Implement `GET /api/drafts` (list)
3. [ ] Implement `GET /api/drafts/{id}` (details)
4. [ ] Implement `POST /api/drafts/{id}/approve`
   - Update draft status
   - Trigger execution if needed
   - Call Kernel API for permission check
5. [ ] Implement `POST /api/drafts/{id}/reject`
6. [ ] Add routes to `dashboard.py`
7. [ ] Write API tests

**Deliverable:** Draft API working, tested

---

### Phase 4: Execution & Audit API (Day 4)

**Tasks:**
1. [ ] Create `lynx/api/execution_routes.py`
2. [ ] Implement `POST /api/executions/{id}/confirm`
3. [ ] Implement `GET /api/executions/{id}`
4. [ ] Create `lynx/api/audit_routes.py`
5. [ ] Implement `GET /api/audit/runs` (list)
6. [ ] Implement `GET /api/audit/runs/{id}` (details)
7. [ ] Add routes to `dashboard.py`
8. [ ] Write API tests

**Deliverable:** Execution & Audit API working, tested

---

### Phase 5: Integration & Testing (Day 5)

**Tasks:**
1. [ ] Integrate all routes into `dashboard.py`
2. [ ] Add error handling
3. [ ] Add request validation
4. [ ] Add CORS configuration (already exists)
5. [ ] End-to-end API testing
6. [ ] Update API documentation

**Deliverable:** Complete API ready for UI integration

---

## 🔒 Boundary Enforcement Rules

### Rule 1: Kernel API Calls

**When to Call Kernel API:**
- ✅ Need entity metadata → `kernel_api.get_metadata(entity_type)`
- ✅ Need permission check → `kernel_api.check_permission(...)`
- ✅ Need schema → `kernel_api.get_schema(entity_type)`

**When NOT to Call Kernel API:**
- ❌ Lynx-specific data (runs, drafts) → Use Lynx storage
- ❌ UI-specific endpoints → Stay in Lynx API
- ❌ Chat processing → Use Lynx core runtime

---

### Rule 2: Data Ownership

**Lynx Owns:**
- ✅ Lynx Runs (audit logs)
- ✅ Drafts (pending actions)
- ✅ Executions (tool executions)
- ✅ Session data

**Kernel Owns:**
- ✅ Entity metadata
- ✅ Entity schemas
- ✅ Permissions
- ✅ Tenant configurations

**Never Duplicate:**
- ❌ Don't cache Kernel metadata in Lynx
- ❌ Don't store permissions in Lynx
- ❌ Always call Kernel for SSOT data

---

### Rule 3: Error Handling

**Kernel API Errors:**
- If Kernel API unavailable → Return degraded response (don't fail)
- If permission denied → Return 403 (from Kernel)
- If metadata missing → Return 404 (from Kernel)

**Lynx API Errors:**
- Invalid request → Return 400
- Draft not found → Return 404
- Execution failed → Return 500 with details

---

## 📊 Testing Strategy

### Unit Tests

**Location:** `lynx-ai/tests/api/`

**Test Files:**
- `test_chat_api.py` - Chat endpoint tests
- `test_draft_api.py` - Draft endpoint tests
- `test_execution_api.py` - Execution endpoint tests
- `test_audit_api.py` - Audit endpoint tests

**Test Coverage:**
- ✅ Request validation
- ✅ Response format
- ✅ Error handling
- ✅ Boundary enforcement (Kernel API calls mocked)

---

### Integration Tests

**Test Scenarios:**
- ✅ Chat query → Kernel API call → Response
- ✅ Draft approve → Permission check (Kernel) → Execution
- ✅ Audit trail → Tenant-scoped queries
- ✅ Error scenarios (Kernel unavailable, etc.)

---

## ✅ Acceptance Criteria

### API Endpoints
- [ ] All endpoints implemented
- [ ] All endpoints tested
- [ ] Request/response models validated
- [ ] Error handling complete
- [ ] Documentation complete

### Boundary Enforcement
- [ ] No Kernel functionality duplicated
- [ ] Kernel API calls properly scoped
- [ ] Lynx data stays in Lynx storage
- [ ] Clear separation maintained

### Integration
- [ ] Routes added to `dashboard.py`
- [ ] CORS configured
- [ ] Error handling consistent
- [ ] Ready for UI integration

---

## 📚 Related Documents

- **Kernel Compatibility:** `docs/DEPLOYMENT/LYNX-KERNEL-COMPATIBILITY.md`
- **UI Integration Plan:** `docs/DEPLOYMENT/UI-INTEGRATION-PLAN.md`
- **PRD Laws:** `docs/PRD/PRD-LYNX-001/doc.md` (Law 1: Kernel Supremacy)

---

**Status:** ✅ **READY TO START**  
**Estimated Completion:** 5 days  
**Priority:** 🔴 **HIGH** - Unblocks UI work  
**Boundary Status:** ✅ **CLEAR** - Proper separation defined

