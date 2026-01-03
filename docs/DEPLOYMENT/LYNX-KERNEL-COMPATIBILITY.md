# Lynx-Kernel Compatibility Guide

**Version:** 1.0.1  
**Date:** 2026-01-27  
**Purpose:** Ensure Kernel API compatibility with Lynx AI requirements

---

## Architecture Overview

**Kernel System Components:**
1. **NEXUS-KERNEL** (`@aibos/kernel` npm package) - Data/metadata definitions
2. **AIBOS-KERNEL** (Next.js Portal) - HTTP API server that uses the data package

**Lynx connects to:** AIBOS-KERNEL Next.js Portal (HTTP API endpoints)

---

## Executive Summary

**Lynx does NOT perform traditional "sync" with Kernel.** Instead, Lynx makes **on-demand, real-time API calls** to Kernel when it needs information. This ensures:

- ✅ Always up-to-date data (no stale cache)
- ✅ Tenant-scoped queries (security)
- ✅ Real-time permission checks
- ✅ No data drift

**Kernel API Server:** AIBOS-KERNEL Next.js Portal (`apps/portal`)

---

## How Lynx Interacts with Kernel

### 1. **On-Demand API Calls (Not Batch Sync)**

Lynx makes HTTP API calls to Kernel **when needed**, not on a schedule:

```python
# Example: When user asks about workflows
kernel_api = KernelAPI(tenant_id=context.tenant_id)
workflow_metadata = await kernel_api.get_metadata("workflow")
```

**Pattern:**
- User query → Lynx needs data → API call to Kernel → Response → User answer
- No background sync jobs
- No cached data (except for performance optimization)
- Every request is tenant-scoped

---

## Required Kernel API Endpoints

Lynx requires the following Kernel API endpoints to function:

### 1. **Metadata Endpoint**

**Endpoint:** `GET /metadata/{entity_type}`

**Required For:**
- Reading entity definitions
- Understanding business rules
- Getting entity relationships

**Entity Types Used:**
- `document` - Document metadata
- `workflow` - Workflow metadata
- `vendor` - Vendor metadata
- `payment` - Payment metadata
- `tenant` - Tenant metadata

**Request Headers:**
```
X-Tenant-Id: {tenant_id}
Authorization: Bearer {api_key}
```

**Expected Response:**
```json
{
  "entity_type": "workflow",
  "metadata": {
    "active_count": 5,
    "pending_approvals": 2,
    "lifecycle_states": ["draft", "active", "archived"]
  }
}
```

**Implementation:**
```47:59:lynx-ai/lynx/integration/kernel/client.py
    async def get_metadata(self, entity_type: str) -> Dict[str, Any]:
        """
        Read metadata from Kernel SSOT.
        
        Args:
            entity_type: Entity type (e.g., "document", "workflow", "vendor")
        
        Returns:
            Metadata dictionary
        """
        response = await self.client.get(f"/metadata/{entity_type}")
        response.raise_for_status()
        return response.json()
```

---

### 2. **Schema Endpoint**

**Endpoint:** `GET /schema/{entity_type}`

**Required For:**
- Validating input data
- Understanding data structure
- Type checking

**Entity Types Used:**
- All entity types that Lynx interacts with

**Request Headers:**
```
X-Tenant-Id: {tenant_id}
Authorization: Bearer {api_key}
```

**Expected Response:**
```json
{
  "entity_type": "document",
  "schema": {
    "properties": {
      "document_id": {"type": "string"},
      "document_type": {"type": "string", "enum": ["invoice", "contract"]},
      "status": {"type": "string"}
    },
    "required": ["document_id", "document_type"]
  }
}
```

**Implementation:**
```61:73:lynx-ai/lynx/integration/kernel/client.py
    async def get_schema(self, entity_type: str) -> Dict[str, Any]:
        """
        Read schema from Kernel SSOT.
        
        Args:
            entity_type: Entity type
        
        Returns:
            Schema dictionary
        """
        response = await self.client.get(f"/schema/{entity_type}")
        response.raise_for_status()
        return response.json()
```

---

### 3. **Permission Check Endpoint**

**Endpoint:** `POST /permissions/check`

**Required For:**
- Validating user permissions
- Enforcing role-based access
- Security checks before execution

**Request Body:**
```json
{
  "user_id": "user-123",
  "tenant_id": "tenant-456",
  "action": "document.cluster.request.draft",
  "resource_type": "document"
}
```

**Request Headers:**
```
X-Tenant-Id: {tenant_id}
Authorization: Bearer {api_key}
```

**Expected Response:**
```json
{
  "allowed": true,
  "reason": null,
  "source": "kernel",
  "required_role": ["admin", "manager"],
  "required_scope": ["documents:write"]
}
```

**Implementation:**
```75:102:lynx-ai/lynx/integration/kernel/client.py
    async def check_permission(
        self,
        user_id: str,
        action: str,
        resource_type: str,
    ) -> Dict[str, Any]:
        """
        Check permission via Kernel.
        
        Args:
            user_id: User ID
            action: Action to check (tool ID)
            resource_type: Resource type (domain)
        
        Returns:
            Permission check result with "allowed" field
        """
        response = await self.client.post(
            "/permissions/check",
            json={
                "user_id": user_id,
                "tenant_id": self.tenant_id,
                "action": action,
                "resource_type": resource_type,
            },
        )
        response.raise_for_status()
        return response.json()
```

**Usage Example:**
```64:69:lynx-ai/lynx/mcp/domain/security/permission_read.py
        if kernel_api:
            permission_result = await kernel_api.check_permission(
                user_id=context.user_id,
                action=action,
                resource_type=input.tool_id.split(".")[0],  # Extract domain from tool_id
            )
```

---

### 4. **Tenant Customizations Endpoint**

**Endpoint:** `GET /tenants/{tenant_id}/customizations`

**Required For:**
- Reading tenant-specific configurations
- Understanding tenant customizations
- Adapting advice to tenant context

**Request Headers:**
```
X-Tenant-Id: {tenant_id}
Authorization: Bearer {api_key}
```

**Expected Response:**
```json
{
  "tenant_id": "tenant-456",
  "customizations": {
    "schema_extensions": {
      "document": {
        "custom_fields": ["custom_field_1", "custom_field_2"]
      }
    },
    "workflow_policies": {
      "approval_required": true,
      "auto_approve_threshold": 1000
    }
  }
}
```

**Implementation:**
```104:113:lynx-ai/lynx/integration/kernel/client.py
    async def get_tenant_customizations(self) -> Dict[str, Any]:
        """
        Get tenant customizations.
        
        Returns:
            Tenant customizations dictionary
        """
        response = await self.client.get(f"/tenants/{self.tenant_id}/customizations")
        response.raise_for_status()
        return response.json()
```

**Usage Example:**
```71:71:lynx-ai/lynx/mcp/domain/tenant/profile_read.py
            tenant_customizations = await kernel_api.get_tenant_customizations()
```

---

## Required Request Headers

**All Kernel API requests MUST include:**

1. **X-Tenant-Id** (Required)
   - Purpose: Tenant isolation
   - Value: Current tenant ID
   - Enforced by: Kernel API

2. **Authorization** (Required)
   - Purpose: Authentication
   - Value: `Bearer {KERNEL_API_KEY}`
   - Format: Standard Bearer token

**Implementation:**
```38:45:lynx-ai/lynx/integration/kernel/client.py
        self.client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={
                "X-Tenant-Id": tenant_id,
                "Authorization": f"Bearer {self.api_key}",
            },
            timeout=30.0,
        )
```

---

## Compatibility Requirements

### 1. **API Contract Compatibility**

**Kernel MUST provide:**

| Endpoint | Method | Required | Purpose |
|----------|--------|----------|---------|
| `/metadata/{entity_type}` | GET | ✅ Yes | Entity metadata |
| `/schema/{entity_type}` | GET | ✅ Yes | Entity schema |
| `/permissions/check` | POST | ✅ Yes | Permission validation |
| `/tenants/{tenant_id}/customizations` | GET | ✅ Yes | Tenant configs |

**All endpoints MUST:**
- Accept `X-Tenant-Id` header
- Accept `Authorization: Bearer {token}` header
- Return JSON responses
- Enforce tenant isolation
- Return 401 if unauthorized
- Return 403 if forbidden
- Return 404 if resource not found

---

### 2. **Response Format Compatibility**

**All endpoints MUST return:**

```json
{
  // Endpoint-specific data
  // MUST be valid JSON
  // MUST be tenant-scoped
}
```

**Error Responses MUST follow:**
```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

---

### 3. **Performance Requirements**

**Kernel API MUST meet:**

| Metric | Requirement | Impact |
|--------|------------|--------|
| Response Time (p95) | < 2 seconds | User experience |
| Availability | > 99.5% | System reliability |
| Timeout | < 30 seconds | Lynx timeout setting |

**Lynx Configuration:**
```44:44:lynx-ai/lynx/integration/kernel/client.py
            timeout=30.0,
```

---

### 4. **Security Requirements**

**Kernel MUST enforce:**

1. **Tenant Isolation**
   - Requests with `X-Tenant-Id: tenant-A` MUST NOT return data from `tenant-B`
   - Cross-tenant access MUST return 403 Forbidden

2. **Authentication**
   - Invalid `Authorization` header MUST return 401 Unauthorized
   - Expired tokens MUST return 401 Unauthorized

3. **Authorization**
   - Permission checks MUST be enforced
   - Unauthorized actions MUST return 403 Forbidden

---

## Compatibility Checklist

### ✅ Kernel API Must Provide

- [ ] `GET /metadata/{entity_type}` endpoint
- [ ] `GET /schema/{entity_type}` endpoint
- [ ] `POST /permissions/check` endpoint
- [ ] `GET /tenants/{tenant_id}/customizations` endpoint
- [ ] `X-Tenant-Id` header support
- [ ] `Authorization: Bearer {token}` header support
- [ ] JSON response format
- [ ] Tenant isolation enforcement
- [ ] < 2 second response time (p95)
- [ ] > 99.5% availability

### ✅ Kernel API Must Enforce

- [ ] Tenant isolation (no cross-tenant data)
- [ ] Authentication (401 for invalid tokens)
- [ ] Authorization (403 for unauthorized actions)
- [ ] Input validation (400 for invalid requests)
- [ ] Error handling (proper HTTP status codes)

---

## Testing Compatibility

### 1. **Health Check**

```bash
# Test Kernel API reachability
curl -H "X-Tenant-Id: test-tenant" \
     -H "Authorization: Bearer {KERNEL_API_KEY}" \
     {KERNEL_API_URL}/health
```

**Expected: `200 OK`

---

### 2. **Metadata Endpoint Test**

```bash
# Test metadata endpoint
curl -H "X-Tenant-Id: test-tenant" \
     -H "Authorization: Bearer {KERNEL_API_KEY}" \
     {KERNEL_API_URL}/metadata/workflow
```

**Expected:**
```json
{
  "entity_type": "workflow",
  "metadata": { ... }
}
```

---

### 3. **Permission Check Test**

```bash
# Test permission check
curl -X POST \
     -H "X-Tenant-Id: test-tenant" \
     -H "Authorization: Bearer {KERNEL_API_KEY}" \
     -H "Content-Type: application/json" \
     -d '{
       "user_id": "user-123",
       "tenant_id": "test-tenant",
       "action": "document.cluster.request.draft",
       "resource_type": "document"
     }' \
     {KERNEL_API_URL}/permissions/check
```

**Expected:**
```json
{
  "allowed": true,
  "reason": null,
  "source": "kernel"
}
```

---

### 4. **Tenant Isolation Test**

```bash
# Test tenant A cannot access tenant B data
curl -H "X-Tenant-Id: tenant-A" \
     -H "Authorization: Bearer {KERNEL_API_KEY}" \
     {KERNEL_API_URL}/metadata/workflow

# Should NOT return data from tenant-B
```

**Expected:** Only tenant-A data

---

## Lynx Configuration

### Environment Variables

Lynx requires these environment variables:

```bash
# Required
KERNEL_API_URL=https://your-kernel-api.example.com
KERNEL_API_KEY=your-kernel-api-key

# Optional (for testing)
KERNEL_API_TIMEOUT=30  # seconds (default: 30)
```

**Validation:**
```68:72:lynx-ai/lynx/config.py
    @classmethod
    def validate(self) -> None:
        """Validate configuration."""
        if self.KERNEL_API_URL is None:
            raise ValueError("KERNEL_API_URL environment variable is required")
```

---

## Error Handling

### Lynx Handles Kernel Errors

**If Kernel API is unavailable:**
- Lynx gracefully degrades
- Returns error message to user
- Logs error for debugging
- Does NOT crash

**Example:**
```65:71:lynx-ai/lynx/mcp/domain/workflow/status_read.py
    kernel_api = None
    try:
        kernel_api = KernelAPI(tenant_id=context.tenant_id)
    except (ValueError, Exception):
        # Kernel API not available (e.g., in tests) - use mock data
        pass
```

**If Kernel API returns error:**
- Lynx propagates error to user
- Explains why action failed
- Suggests alternatives
- Logs for audit

---

## Version Compatibility

### API Versioning

**Current Lynx Version:** `0.1.0`

**Kernel API Compatibility:**
- Lynx expects Kernel API v1.0+ (or compatible)
- Kernel API changes MUST be backward compatible
- Breaking changes require Lynx update

**Version Check:**
- Kernel API SHOULD provide version endpoint: `GET /version`
- Lynx can check version on startup (future enhancement)

---

## Summary

### Key Points

1. **No Traditional Sync:** Lynx makes on-demand API calls, not batch sync
2. **4 Required Endpoints:** Metadata, Schema, Permissions, Tenant Customizations
3. **Tenant Isolation:** All requests MUST include `X-Tenant-Id` header
4. **Authentication:** All requests MUST include `Authorization: Bearer {token}` header
5. **Performance:** < 2 second response time (p95), > 99.5% availability
6. **Error Handling:** Graceful degradation if Kernel unavailable

### Compatibility Verification

Run the compatibility checklist above to ensure Kernel API meets all requirements.

---

**End of Compatibility Guide**

