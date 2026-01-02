# Lynx AI Runbook — Operations Guide

**Version:** 0.1.0  
**Last Updated:** 2026-01-27

---

## Quick Reference

### Status Check

```bash
# Check system health
lynx status

# Or via API
curl http://localhost:8000/healthz
```

### Key Metrics

- **Tool Registry Version:** `MCP_TOOLSET_VERSION=0.1.0`
- **Protocol Version:** `LYNX_PROTOCOL_VERSION=0.1.0`
- **Total Tools:** 18 (12 Domain, 3 Cluster, 3 Cell)

---

## How to Run

### Development Mode

```bash
# Set environment
export LYNX_MODE=dev
export KERNEL_API_URL=http://localhost:3000
export SUPABASE_URL=your-supabase-url
export SUPABASE_KEY=your-supabase-key

# Start Lynx
cd lynx-ai
python -m lynx.main
```

### Staging Mode

```bash
export LYNX_MODE=staging
# ... (same env vars as dev)
```

### Production Mode

```bash
export LYNX_MODE=prod
# ... (same env vars, but stricter validation)
```

**Production Safety:**
- High-risk Cell tools require: `approved draft` + `explicit_approval=True`
- All executions are logged to Supabase audit tables
- Draft and execution storage use Supabase (not in-memory)

---

## How to Diagnose

### 1. Check System Health

```bash
lynx status
```

**Expected Output:**
```
Lynx AI Status
==============
Tool Registry: 18 tools registered
Protocol Version: 0.1.0
Toolset Version: 0.1.0

Kernel API: ✅ Reachable
Supabase: ✅ Reachable

Last 5 Runs:
- Run 1: SUCCEEDED (2026-01-27 10:00:00)
- Run 2: SUCCEEDED (2026-01-27 09:55:00)
...
```

### 2. Check Draft Status

```sql
-- Query drafts for tenant
SELECT draft_id, draft_type, status, created_at, risk_level
FROM lynx_drafts
WHERE tenant_id = 'tenant-123'
ORDER BY created_at DESC
LIMIT 10;
```

### 3. Check Execution Status

```sql
-- Query executions for tenant
SELECT execution_id, draft_id, tool_id, status, created_at, completed_at
FROM lynx_executions
WHERE tenant_id = 'tenant-123'
ORDER BY created_at DESC
LIMIT 10;
```

### 4. Check Audit Logs

```sql
-- Query audit events
SELECT run_id, tool_id, status, created_at, error_message
FROM lynx_audit_events
WHERE tenant_id = 'tenant-123'
ORDER BY created_at DESC
LIMIT 20;
```

### 5. Common Error Patterns

**"Draft not found or does not belong to tenant"**
- **Cause:** Cross-tenant access attempt or draft deleted
- **Fix:** Verify `tenant_id` matches execution context

**"Draft is not approved (status: draft)"**
- **Cause:** Attempting to execute unapproved draft
- **Fix:** Submit draft for approval first, then approve externally

**"Draft has already been successfully executed"**
- **Cause:** Exactly-once semantics - draft already executed
- **Fix:** This is expected behavior. Create new draft if re-execution needed.

**"High-risk action requires explicit approval"**
- **Cause:** Production mode requires `explicit_approval=True` for high-risk tools
- **Fix:** Set `context.explicit_approval = True` or use approved draft workflow

---

## How to Rollback

### Rollback Draft Execution

**If execution failed:**
1. Check execution record for `rollback_instructions`
2. Execute rollback manually (if provided)
3. Update draft status if needed

**Example rollback:**
```python
# Get execution record
execution = await execution_storage.get_execution(execution_id, tenant_id)

# Check rollback instructions
if execution.rollback_instructions:
    # Execute rollback based on instructions
    # e.g., delete created payment record, revert workflow status
    pass
```

### Rollback Payment Execution

**If payment was executed incorrectly:**
1. Payment status is `pending_settlement` (not yet settled)
2. Settlement intent has `provider=none` (no bank integration)
3. Manually update payment status or create reversal record

**Note:** In production, implement proper reversal workflow.

---

## Understanding Status States

### Draft Status: "Already Executed"

**What it means:**
- Draft has been successfully executed by a Cell MCP
- Status is `PUBLISHED` (workflow) or `EXECUTED` (payment/docs)
- Exactly-once semantics prevents re-execution

**Why it happens:**
- Same draft executed twice (even with different `request_id`)
- Execution record exists with `status=SUCCEEDED`

**What to do:**
- This is expected behavior (prevents duplicate executions)
- If re-execution needed, create new draft from scratch

### Payment Status: "pending_settlement"

**What it means:**
- Payment draft was executed successfully
- Payment record created with `status=pending_settlement`
- Settlement intent created with `status=queued`, `provider=none`
- **No bank transfer has occurred** (internal-only execution)

**Why it exists:**
- Separates execution (governance) from settlement (bank integration)
- Allows audit and approval before actual money movement
- Settlement is a future seam (separate Cell tool or async worker)

**What to do:**
- Payment is queued for settlement
- Settlement can be processed manually or via future `vpm.cell.settlement.execute` tool
- Check `settlement_intent` object for settlement details

---

## Environment Variables

### Required

```bash
KERNEL_API_URL=http://localhost:3000  # Kernel SSOT API
SUPABASE_URL=https://xxx.supabase.co  # Supabase project URL
SUPABASE_KEY=your-supabase-key         # Supabase service key
```

### Optional

```bash
LYNX_MODE=dev|staging|prod            # Execution mode (default: dev)
LYNX_PROTOCOL_VERSION=0.1.0           # Protocol version
MCP_TOOLSET_VERSION=0.1.0             # Toolset version
```

---

## Monitoring

### Key Metrics to Watch

1. **Execution Success Rate**
   - Query: `SELECT status, COUNT(*) FROM lynx_executions GROUP BY status`
   - Alert if: Success rate < 95%

2. **Draft Approval Time**
   - Query: Time from `SUBMITTED` to `APPROVED`
   - Alert if: Average > 24 hours

3. **Failed Executions**
   - Query: `SELECT * FROM lynx_executions WHERE status = 'FAILED'`
   - Alert if: Failure rate > 5%

4. **Pending Settlements**
   - Query: `SELECT COUNT(*) FROM settlement_intents WHERE status = 'queued'`
   - Alert if: Queue size > 100

---

## Troubleshooting

### Kernel API Unreachable

**Symptoms:**
- `system.domain.health.read` returns `kernel_reachable: false`
- Domain MCPs fail with connection errors

**Fix:**
1. Check `KERNEL_API_URL` is correct
2. Verify Kernel service is running
3. Check network connectivity

### Supabase Connection Issues

**Symptoms:**
- Draft/execution storage fails
- Audit logging fails

**Fix:**
1. Check `SUPABASE_URL` and `SUPABASE_KEY`
2. Verify Supabase project is active
3. Check RLS policies allow service key access

### High-Risk Tool Blocked in Production

**Symptoms:**
- `vpm.cell.payment.execute` fails with "explicit approval required"

**Fix:**
1. Ensure draft is `APPROVED`
2. Set `context.explicit_approval = True` (or use approval workflow)
3. Verify `LYNX_MODE=prod` is set correctly

---

## Emergency Procedures

### Stop All Executions

```bash
# Set maintenance mode (if implemented)
export LYNX_MAINTENANCE_MODE=true

# Or stop service
systemctl stop lynx-ai
```

### Clear Stuck Executions

```sql
-- Mark stuck executions as failed
UPDATE lynx_executions
SET status = 'FAILED',
    error_message = 'Manual intervention: execution stuck',
    completed_at = NOW()
WHERE status = 'STARTED'
  AND created_at < NOW() - INTERVAL '1 hour';
```

### Force Draft Status Reset

```sql
-- Reset draft to DRAFT (use with caution)
UPDATE lynx_drafts
SET status = 'DRAFT'
WHERE draft_id = 'xxx'
  AND tenant_id = 'yyy';
```

**Warning:** Only use in emergency. Breaks audit trail.

---

## References

- **Tool Index:** `docs/MCP/INDEX.md`
- **PRD:** PRD-LYNX-003 (HYBRID BASIC)
- **Decision:** DECISION-LYNX-002 (Cell Execution Protocol)
- **Code:** `lynx-ai/lynx/`

