# Phase 5.3: Railway Staging Launch Checklist

**Version:** 1.0.0  
**Date:** 2026-01-27  
**Status:** Ready for Execution

---

## Overview

This checklist covers the complete staging deployment and validation sequence for Lynx AI on Railway.

**Architecture:**
- **Vercel**: Frontend (Next.js portal)
- **Supabase**: Database + RLS + Storage
- **Railway**: Lynx runtime (daemon mode)

---

## Prerequisites

- [ ] Supabase project created and schema applied
- [ ] Railway account created
- [ ] Git repository accessible to Railway
- [ ] All environment variables ready (see below)

---

## Step 1: Deploy to Railway

### 1.1 Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo" (or "Empty Project" for manual deploy)
4. Choose your repository

### 1.2 Configure Service

**Root Directory:** Project root (Railway will use `railway.json` which does `cd lynx-ai`)

**Build Command:** (auto-detected from `railway.json`)
```bash
cd lynx-ai && uv sync
```

**Start Command:** (from `railway.json`)
```bash
cd lynx-ai && LYNX_RUNNER=daemon uv run python -m lynx.runtime.daemon
```

### 1.3 Set Environment Variables

In Railway dashboard → Variables tab, add:

**Required:**
```
LYNX_MODE=staging
LYNX_RUNNER=daemon
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_KEY=<service-role-key>
KERNEL_API_URL=https://your-kernel-api.example.com
KERNEL_API_KEY=<kernel-api-key>
OPENAI_API_KEY=<openai-api-key>
```

**Optional (with defaults):**
```
DAEMON_HEARTBEAT_INTERVAL=60
DAEMON_STATUS_CHECK_INTERVAL=300
```

**Mark as Secret:** `SUPABASE_KEY`, `OPENAI_API_KEY`, `KERNEL_API_KEY`

### 1.4 Deploy

1. Railway will automatically build and deploy
2. Check deployment logs for errors
3. Verify service starts successfully

---

## Step 2: Verify Service Stays Alive

### 2.1 Check Initialization Logs

**Expected logs on startup:**
```
🚀 Starting Lynx AI Daemon...
✅ Configuration loaded
✅ Core components initialized
✅ Audit logger initialized
✅ MCP server initialized

============================================================
📋 Lynx AI Startup Banner
============================================================
   Environment:        STAGING
   Runner Mode:         DAEMON
   Storage Backend:     SUPABASE
   Protocol Version:    0.1.0
   Toolset Version:     0.1.0
============================================================

📋 Lynx AI Status:
   ✅ Tools registered: 18
   ✅ Domain MCPs: 12
   ✅ Cluster MCPs: 3
   ✅ Cell MCPs: 3
   ✅ Active sessions: 0
============================================================

💚 Daemon running. Waiting for MCP client connections...
   Heartbeat interval: 60s
   Status check interval: 300s
   Press Ctrl+C or send SIGTERM to shutdown gracefully
```

### 2.2 Verify Heartbeat

**Expected heartbeat logs (every 60s):**
```
💓 [2026-01-27 10:00:00] Heartbeat #1 | Tools: 18 | Sessions: 0
💓 [2026-01-27 10:01:00] Heartbeat #2 | Tools: 18 | Sessions: 0
💓 [2026-01-27 10:02:00] Heartbeat #3 | Tools: 18 | Sessions: 0
```

**If heartbeat doesn't appear:**
- Check log level settings
- Verify daemon loop is running
- Check for errors in logs

### 2.3 Verify Status Checks

**Expected status check logs (every 5 minutes):**
```
📊 [2026-01-27 10:05:00] Status Check #1:
   Status: OPERATIONAL
   Storage: SUPABASE
   Drafts (24h): 0
   Executions (24h): 0
   Pending Settlements: 0
```

---

## Step 3: Database Migration Verification

### 3.1 Run Verification Queries

Connect to Supabase SQL Editor and run queries from `docs/DEPLOYMENT/supabase-migration.sql`:

**Verify tables exist:**
```sql
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
```

**Expected:** All 4 tables with `rowsecurity = true`

**Verify RLS policies:**
```sql
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
```

**Expected:** 4 policies (one per table)

**Verify indexes:**
```sql
SELECT 
    schemaname,
    tablename,
    indexname
FROM pg_indexes
WHERE schemaname = 'public'
AND (tablename LIKE 'lynx%' OR tablename = 'settlement_intents')
ORDER BY tablename, indexname;
```

**Expected:** 20+ indexes

---

## Step 4: RLS Verification Tests

### 4.1 Run RLS Tests Against Staging

From your local machine (pointing at staging Supabase):

```bash
cd lynx-ai

# Set staging Supabase credentials
export SUPABASE_URL=https://<project-ref>.supabase.co
export SUPABASE_KEY=<service-role-key>

# Run RLS verification tests
uv run pytest -q tests/integration/test_rls_verification.py -x
```

**Expected:** All tests pass (5+ tests)

**Test Coverage:**
- ✅ Draft isolation (cross-tenant access blocked)
- ✅ Execution isolation (cross-tenant access blocked)
- ✅ Settlement intent isolation (cross-tenant access blocked)
- ✅ Idempotency respects tenant boundaries
- ✅ Update operations respect tenant boundaries

---

## Step 5: End-to-End Smoke Test

### 5.1 Create Document Draft → Submit

**Test flow:**
1. Create document draft via MCP tool
2. Submit draft for approval
3. Verify in Supabase:
   - `lynx_drafts` table has new record
   - `lynx_executions` table has execution record
   - `lynx_audit_events` has audit events

**SQL verification:**
```sql
-- Check draft
SELECT draft_id, draft_type, status, created_at, tenant_id
FROM lynx_drafts
WHERE draft_type = 'docs'
ORDER BY created_at DESC
LIMIT 1;

-- Check execution
SELECT execution_id, draft_id, tool_id, status, created_at
FROM lynx_executions
WHERE tool_id = 'docs.cell.draft.submit_for_approval'
ORDER BY created_at DESC
LIMIT 1;

-- Check audit events
SELECT event_id, run_id, tool_id, event_type, created_at
FROM lynx_audit_events
WHERE tool_id = 'docs.cell.draft.submit_for_approval'
ORDER BY created_at DESC
LIMIT 5;
```

### 5.2 Create Workflow Draft → Publish

**Test flow:**
1. Create workflow draft
2. Approve draft (if needed)
3. Publish workflow
4. Verify in Supabase:
   - Draft status = `published`
   - Execution record created
   - Audit events logged

### 5.3 Create Payment Draft → Execute

**Test flow:**
1. Create payment draft
2. Approve draft (if needed)
3. Execute payment
4. Verify in Supabase:
   - Draft status = `executed`
   - Execution record created
   - `settlement_intents` table has queued intent
   - Audit events logged

**SQL verification:**
```sql
-- Check settlement intent
SELECT payment_id, settlement_status, provider, tenant_id, created_at
FROM settlement_intents
ORDER BY created_at DESC
LIMIT 1;
```

---

## Step 6: Graceful Shutdown Verification

### 6.1 Trigger Railway Redeploy

1. In Railway dashboard, trigger a redeploy (or push a small change)
2. Watch logs for graceful shutdown

### 6.2 Verify Shutdown Logs

**Expected shutdown logs:**
```
🛑 Received signal 15, initiating graceful shutdown...
🛑 Shutdown signal received, cleaning up...
✅ Graceful shutdown complete
```

### 6.3 Verify No Orphaned Records

**Check for incomplete executions:**
```sql
-- Should be minimal (only edge cases)
SELECT execution_id, draft_id, tool_id, status, created_at
FROM lynx_executions
WHERE status = 'started'
AND completed_at IS NULL
ORDER BY created_at DESC;
```

**Expected:** 0 or very few (only if shutdown happened mid-execution)

---

## Step 7: Monitoring Setup

### 7.1 Railway Logs

- [ ] Logs accessible in Railway dashboard
- [ ] Heartbeat visible every 60s
- [ ] Status checks visible every 5 minutes
- [ ] No error spam

### 7.2 Supabase Monitoring

- [ ] Supabase dashboard accessible
- [ ] Database queries working
- [ ] RLS policies active
- [ ] No connection errors

### 7.3 Health Checks

**Run status CLI (via Railway SSH or local with staging env):**
```bash
railway run python -m lynx.cli.status
```

**Expected output:**
```
--- Lynx AI System Status ---
Service Status: OPERATIONAL
Current Mode: STAGING
Storage Backend: SUPABASE
Drafts (last 24h): X
Executions (last 24h): Y
Pending Settlements: Z
...
```

---

## Troubleshooting

### Issue: Service exits immediately

**Check:**
1. Environment variables set correctly
2. Supabase connection works
3. Kernel API reachable
4. Check Railway logs for errors

**Solution:** Verify all required env vars are set and marked as "Secret" if needed.

### Issue: No heartbeat logs

**Check:**
1. Daemon mode enabled (`LYNX_RUNNER=daemon`)
2. Log level not filtering out INFO logs
3. Service actually running (check Railway status)

**Solution:** Verify `LYNX_RUNNER=daemon` is set in Railway variables.

### Issue: RLS tests fail

**Check:**
1. Supabase schema applied correctly
2. RLS policies exist
3. Using service_role key (not anon key)
4. `app.tenant_id` set correctly in storage layer

**Solution:** Re-run migration script and verify RLS policies.

### Issue: Graceful shutdown not working

**Check:**
1. SIGTERM handler registered
2. Background tasks canceling properly
3. No blocking operations in shutdown

**Solution:** Check daemon logs for shutdown messages.

---

## Success Criteria

- [x] Service stays alive (heartbeat visible)
- [x] Database migration verified (all tables + RLS)
- [x] RLS tests pass (all 5+ tests)
- [x] End-to-end smoke test passes (all 3 flows)
- [x] Graceful shutdown works (clean logs)
- [x] Status CLI shows correct metrics
- [x] No orphaned execution records

---

## Next Steps After Staging Validation

Once staging is verified:

1. ✅ Document any issues found
2. ✅ Update runbook with staging-specific notes
3. ✅ Plan production deployment
4. ✅ Set up monitoring/alerting
5. ✅ Prepare rollback procedure

---

**Status:** ✅ Ready for Phase 5.3 execution

