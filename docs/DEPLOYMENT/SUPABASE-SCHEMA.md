# Supabase Schema — Lynx AI

**Version:** 0.1.0  
**Last Updated:** 2026-01-27

---

## Overview

This document defines the Supabase schema for Lynx AI storage backends:
- Draft Storage
- Execution Storage
- Settlement Intent Storage
- Audit Tables

**Design Principles:**
- Minimal columns (only what's needed)
- RLS (Row Level Security) by tenant
- Migration scripts included
- Indexes for performance

---

## Tables

### 1. `lynx_drafts`

Stores all draft objects (docs, workflow, payment).

```sql
CREATE TABLE lynx_drafts (
    draft_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    draft_type TEXT NOT NULL, -- 'docs', 'workflow', 'vpm_payment'
    payload JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft', -- 'draft', 'submitted', 'approved', 'rejected', 'cancelled', 'published', 'executed'
    risk_level TEXT NOT NULL, -- 'low', 'medium', 'high'
    created_by TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    source_context JSONB NOT NULL,
    recommended_approvers TEXT[] DEFAULT ARRAY[]::TEXT[],
    request_id TEXT,
    
    -- Indexes
    CONSTRAINT lynx_drafts_status_check CHECK (status IN ('draft', 'submitted', 'approved', 'rejected', 'cancelled', 'published', 'executed')),
    CONSTRAINT lynx_drafts_risk_level_check CHECK (risk_level IN ('low', 'medium', 'high')),
    CONSTRAINT lynx_drafts_draft_type_check CHECK (draft_type IN ('docs', 'workflow', 'vpm_payment'))
);

-- Indexes
CREATE INDEX idx_lynx_drafts_tenant_id ON lynx_drafts(tenant_id);
CREATE INDEX idx_lynx_drafts_status ON lynx_drafts(tenant_id, status);
CREATE INDEX idx_lynx_drafts_request_id ON lynx_drafts(tenant_id, request_id) WHERE request_id IS NOT NULL;
CREATE INDEX idx_lynx_drafts_created_at ON lynx_drafts(tenant_id, created_at DESC);

-- RLS Policy
ALTER TABLE lynx_drafts ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Tenant isolation for drafts"
    ON lynx_drafts
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id', true));
```

### 2. `lynx_executions`

Stores all Cell MCP execution records.

```sql
CREATE TABLE lynx_executions (
    execution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    draft_id UUID NOT NULL REFERENCES lynx_drafts(draft_id) ON DELETE CASCADE,
    tool_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'started', -- 'started', 'succeeded', 'failed', 'denied'
    result_payload JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    rollback_instructions JSONB,
    request_id TEXT,
    source_context JSONB DEFAULT '{}'::JSONB,
    
    -- Indexes
    CONSTRAINT lynx_executions_status_check CHECK (status IN ('started', 'succeeded', 'failed', 'denied'))
);

-- Indexes
CREATE INDEX idx_lynx_executions_tenant_id ON lynx_executions(tenant_id);
CREATE INDEX idx_lynx_executions_draft_id ON lynx_executions(tenant_id, draft_id);
CREATE INDEX idx_lynx_executions_tool_id ON lynx_executions(tenant_id, tool_id);
CREATE INDEX idx_lynx_executions_status ON lynx_executions(tenant_id, status);
CREATE INDEX idx_lynx_executions_request_id ON lynx_executions(tenant_id, request_id) WHERE request_id IS NOT NULL;
CREATE INDEX idx_lynx_executions_created_at ON lynx_executions(tenant_id, created_at DESC);

-- Unique constraint for exactly-once semantics
CREATE UNIQUE INDEX idx_lynx_executions_draft_tool_unique 
    ON lynx_executions(tenant_id, draft_id, tool_id) 
    WHERE status = 'succeeded';

-- RLS Policy
ALTER TABLE lynx_executions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Tenant isolation for executions"
    ON lynx_executions
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id', true));
```

### 3. `settlement_intents`

Stores settlement intent objects for payment executions.

```sql
CREATE TABLE settlement_intents (
    payment_id TEXT NOT NULL PRIMARY KEY,
    settlement_status TEXT NOT NULL DEFAULT 'queued', -- 'queued', 'processing', 'completed', 'failed'
    provider TEXT NOT NULL DEFAULT 'none', -- 'none', 'manual', 'bank_x'
    tenant_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::JSONB,
    
    -- Indexes
    CONSTRAINT settlement_intents_status_check CHECK (settlement_status IN ('queued', 'processing', 'completed', 'failed')),
    CONSTRAINT settlement_intents_provider_check CHECK (provider IN ('none', 'manual', 'bank_x'))
);

-- Indexes
CREATE INDEX idx_settlement_intents_tenant_id ON settlement_intents(tenant_id);
CREATE INDEX idx_settlement_intents_status ON settlement_intents(tenant_id, settlement_status);
CREATE INDEX idx_settlement_intents_created_at ON settlement_intents(tenant_id, created_at DESC);

-- RLS Policy
ALTER TABLE settlement_intents ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Tenant isolation for settlement intents"
    ON settlement_intents
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id', true));
```

### 4. `lynx_audit_events`

Stores audit events (Lynx runs, tool calls, refusals).

```sql
CREATE TABLE lynx_audit_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    tool_id TEXT,
    event_type TEXT NOT NULL, -- 'run_start', 'run_success', 'run_failure', 'tool_call', 'refusal'
    status TEXT, -- 'started', 'succeeded', 'failed', 'denied'
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    
    -- Indexes
    CONSTRAINT lynx_audit_events_event_type_check CHECK (event_type IN ('run_start', 'run_success', 'run_failure', 'tool_call', 'refusal'))
);

-- Indexes
CREATE INDEX idx_lynx_audit_events_tenant_id ON lynx_audit_events(tenant_id);
CREATE INDEX idx_lynx_audit_events_run_id ON lynx_audit_events(tenant_id, run_id);
CREATE INDEX idx_lynx_audit_events_tool_id ON lynx_audit_events(tenant_id, tool_id) WHERE tool_id IS NOT NULL;
CREATE INDEX idx_lynx_audit_events_created_at ON lynx_audit_events(tenant_id, created_at DESC);

-- RLS Policy
ALTER TABLE lynx_audit_events ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Tenant isolation for audit events"
    ON lynx_audit_events
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id', true));
```

---

## Migration Script

### Initial Migration: `001_initial_schema.sql`

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables (see above)

-- Set up RLS (see above)

-- Grant permissions (adjust based on your service role)
GRANT ALL ON lynx_drafts TO service_role;
GRANT ALL ON lynx_executions TO service_role;
GRANT ALL ON settlement_intents TO service_role;
GRANT ALL ON lynx_audit_events TO service_role;
```

---

## Usage Notes

### Setting Tenant Context

When executing queries, set tenant context:

```sql
SET app.tenant_id = 'tenant-123';
SELECT * FROM lynx_drafts;
```

### Service Role Access

For service role (bypasses RLS):

```sql
-- Use service_role key in connection
-- RLS policies are bypassed for service_role
```

### Application Code

In Python, use Supabase client with tenant context:

```python
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Set tenant context (if using RLS)
# Or use service_role key (bypasses RLS)

# Query drafts
drafts = supabase.table("lynx_drafts").select("*").eq("tenant_id", tenant_id).execute()
```

---

## Performance Considerations

- **Indexes:** All tenant-scoped queries are indexed
- **Partitioning:** Consider partitioning `lynx_audit_events` by date for large volumes
- **Archival:** Archive old audit events (>90 days) to separate table

---

## Security

- **RLS:** All tables enforce tenant isolation via RLS
- **Service Role:** Use service role key for application access (bypasses RLS)
- **API Keys:** Never expose service role key in client-side code

---

## References

- **Draft Protocol:** `lynx/mcp/cluster/drafts/base.py`
- **Execution Protocol:** `lynx/mcp/cell/execution/base.py`
- **Supabase RLS Docs:** https://supabase.com/docs/guides/auth/row-level-security

