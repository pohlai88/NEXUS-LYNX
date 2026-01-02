-- ============================================================================
-- Lynx AI Supabase Migration Script
-- Version: 0.1.0
-- Date: 2026-01-27
-- ============================================================================
-- 
-- This script creates all required tables, indexes, and RLS policies for
-- Lynx AI multi-tenant staging/production deployment.
--
-- Prerequisites:
--   1. Supabase project created
--   2. uuid-ossp extension enabled (usually enabled by default)
--
-- Usage:
--   Copy and paste this entire script into Supabase SQL Editor and execute.
--
-- ============================================================================

-- Enable UUID extension (if not already enabled)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- TABLE: lynx_drafts
-- ============================================================================
-- Stores all draft objects (docs, workflow, payment).
-- ============================================================================

CREATE TABLE IF NOT EXISTS lynx_drafts (
    draft_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    tenant_id TEXT NOT NULL,
    draft_type TEXT NOT NULL CHECK (draft_type IN ('docs', 'workflow', 'vpm_payment')),
    payload JSONB NOT NULL,
    status TEXT NOT NULL DEFAULT 'draft' CHECK (status IN ('draft', 'submitted', 'approved', 'rejected', 'cancelled', 'published', 'executed')),
    risk_level TEXT NOT NULL CHECK (risk_level IN ('low', 'medium', 'high')),
    created_by TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    source_context JSONB NOT NULL DEFAULT '{}'::JSONB,
    recommended_approvers TEXT[] DEFAULT ARRAY[]::TEXT[],
    request_id TEXT
);

-- Indexes for lynx_drafts
CREATE INDEX IF NOT EXISTS idx_lynx_drafts_tenant_id ON lynx_drafts(tenant_id);
CREATE INDEX IF NOT EXISTS idx_lynx_drafts_status ON lynx_drafts(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_lynx_drafts_request_id ON lynx_drafts(tenant_id, request_id) WHERE request_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_lynx_drafts_created_at ON lynx_drafts(tenant_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_lynx_drafts_draft_type ON lynx_drafts(tenant_id, draft_type);

-- Unique index for idempotency (request_id per tenant)
CREATE UNIQUE INDEX IF NOT EXISTS idx_lynx_drafts_request_id_unique 
    ON lynx_drafts(tenant_id, request_id) 
    WHERE request_id IS NOT NULL;

-- RLS Policy for lynx_drafts
ALTER TABLE lynx_drafts ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Tenant isolation for drafts" ON lynx_drafts;
CREATE POLICY "Tenant isolation for drafts"
    ON lynx_drafts
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id', true));

-- ============================================================================
-- TABLE: lynx_executions
-- ============================================================================
-- Stores all Cell MCP execution records.
-- ============================================================================

CREATE TABLE IF NOT EXISTS lynx_executions (
    execution_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    draft_id UUID NOT NULL REFERENCES lynx_drafts(draft_id) ON DELETE CASCADE,
    tool_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'started' CHECK (status IN ('started', 'succeeded', 'failed', 'denied')),
    result_payload JSONB DEFAULT '{}'::JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    error_message TEXT,
    rollback_instructions JSONB,
    request_id TEXT,
    source_context JSONB DEFAULT '{}'::JSONB
);

-- Indexes for lynx_executions
CREATE INDEX IF NOT EXISTS idx_lynx_executions_tenant_id ON lynx_executions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_lynx_executions_draft_id ON lynx_executions(tenant_id, draft_id);
CREATE INDEX IF NOT EXISTS idx_lynx_executions_tool_id ON lynx_executions(tenant_id, tool_id);
CREATE INDEX IF NOT EXISTS idx_lynx_executions_status ON lynx_executions(tenant_id, status);
CREATE INDEX IF NOT EXISTS idx_lynx_executions_request_id ON lynx_executions(tenant_id, request_id) WHERE request_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_lynx_executions_created_at ON lynx_executions(tenant_id, created_at DESC);

-- Unique constraint for exactly-once semantics
-- A given (tenant_id, draft_id, tool_id) can only have ONE successful execution
CREATE UNIQUE INDEX IF NOT EXISTS idx_lynx_executions_draft_tool_unique 
    ON lynx_executions(tenant_id, draft_id, tool_id) 
    WHERE status = 'succeeded';

-- Unique index for idempotency (request_id per tenant)
CREATE UNIQUE INDEX IF NOT EXISTS idx_lynx_executions_request_id_unique 
    ON lynx_executions(tenant_id, request_id) 
    WHERE request_id IS NOT NULL;

-- RLS Policy for lynx_executions
ALTER TABLE lynx_executions ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Tenant isolation for executions" ON lynx_executions;
CREATE POLICY "Tenant isolation for executions"
    ON lynx_executions
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id', true));

-- ============================================================================
-- TABLE: settlement_intents
-- ============================================================================
-- Stores settlement intent objects for payment executions.
-- ============================================================================

CREATE TABLE IF NOT EXISTS settlement_intents (
    payment_id TEXT NOT NULL PRIMARY KEY,
    settlement_status TEXT NOT NULL DEFAULT 'queued' CHECK (settlement_status IN ('queued', 'processing', 'completed', 'failed')),
    provider TEXT NOT NULL DEFAULT 'none' CHECK (provider IN ('none', 'manual', 'bank_x')),
    tenant_id TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    metadata JSONB DEFAULT '{}'::JSONB
);

-- Indexes for settlement_intents
CREATE INDEX IF NOT EXISTS idx_settlement_intents_tenant_id ON settlement_intents(tenant_id);
CREATE INDEX IF NOT EXISTS idx_settlement_intents_status ON settlement_intents(tenant_id, settlement_status);
CREATE INDEX IF NOT EXISTS idx_settlement_intents_created_at ON settlement_intents(tenant_id, created_at DESC);

-- RLS Policy for settlement_intents
ALTER TABLE settlement_intents ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Tenant isolation for settlement intents" ON settlement_intents;
CREATE POLICY "Tenant isolation for settlement intents"
    ON settlement_intents
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id', true));

-- ============================================================================
-- TABLE: lynx_audit_events
-- ============================================================================
-- Stores audit events (Lynx runs, tool calls, refusals).
-- ============================================================================

CREATE TABLE IF NOT EXISTS lynx_audit_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id TEXT NOT NULL,
    tenant_id TEXT NOT NULL,
    tool_id TEXT,
    event_type TEXT NOT NULL CHECK (event_type IN ('run_start', 'run_success', 'run_failure', 'tool_call', 'refusal')),
    status TEXT CHECK (status IN ('started', 'succeeded', 'failed', 'denied')),
    input_data JSONB,
    output_data JSONB,
    error_message TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Indexes for lynx_audit_events
CREATE INDEX IF NOT EXISTS idx_lynx_audit_events_tenant_id ON lynx_audit_events(tenant_id);
CREATE INDEX IF NOT EXISTS idx_lynx_audit_events_run_id ON lynx_audit_events(tenant_id, run_id);
CREATE INDEX IF NOT EXISTS idx_lynx_audit_events_tool_id ON lynx_audit_events(tenant_id, tool_id) WHERE tool_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_lynx_audit_events_created_at ON lynx_audit_events(tenant_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_lynx_audit_events_event_type ON lynx_audit_events(tenant_id, event_type);

-- RLS Policy for lynx_audit_events
ALTER TABLE lynx_audit_events ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS "Tenant isolation for audit events" ON lynx_audit_events;
CREATE POLICY "Tenant isolation for audit events"
    ON lynx_audit_events
    FOR ALL
    USING (tenant_id = current_setting('app.tenant_id', true));

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================
-- Run these after migration to verify tables exist and RLS is enabled.
-- Copy and paste these queries into Supabase SQL Editor to verify.
-- ============================================================================

-- Verify all tables exist and RLS is enabled
SELECT 
    tablename, 
    rowsecurity,
    CASE 
        WHEN rowsecurity THEN '✅ RLS Enabled'
        ELSE '❌ RLS Disabled'
    END as rls_status
FROM pg_tables 
WHERE schemaname = 'public' 
AND (tablename LIKE 'lynx%' OR tablename = 'settlement_intents')
ORDER BY tablename;

-- Expected: All 4 tables with rowsecurity = true

-- Verify RLS policies exist
SELECT 
    schemaname, 
    tablename, 
    policyname,
    CASE 
        WHEN policyname IS NOT NULL THEN '✅ Policy Exists'
        ELSE '❌ Policy Missing'
    END as policy_status
FROM pg_policies 
WHERE tablename LIKE 'lynx%' OR tablename = 'settlement_intents'
ORDER BY tablename, policyname;

-- Expected: 4 policies (one per table)

-- Verify indexes exist
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
AND (tablename LIKE 'lynx%' OR tablename = 'settlement_intents')
ORDER BY tablename, indexname;

-- Verify unique constraints exist
SELECT
    tc.table_name,
    tc.constraint_name,
    tc.constraint_type
FROM information_schema.table_constraints tc
WHERE tc.table_schema = 'public'
AND (tc.table_name LIKE 'lynx%' OR tc.table_name = 'settlement_intents')
AND tc.constraint_type = 'UNIQUE'
ORDER BY tc.table_name, tc.constraint_name;

-- Expected: Unique constraints on request_id and draft_id+tool_id combinations

-- ============================================================================
-- MIGRATION COMPLETE
-- ============================================================================
-- If all verification queries return expected results, migration is successful.
-- Next steps:
--   1. Run RLS verification tests: pytest tests/integration/test_rls_verification.py
--   2. Verify staging checklist: docs/DEPLOYMENT/STAGING-CHECKLIST.md
--   3. Test status CLI: python -m lynx.cli.status
-- ============================================================================

