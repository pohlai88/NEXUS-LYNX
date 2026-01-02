# Railway Setup Guide — Lynx AI

**Version:** 1.0.0  
**Date:** 2026-01-27  
**Target:** Railway deployment for Lynx Python runtime

---

## Overview

This guide covers deploying Lynx AI to Railway as a long-lived Python service.

**Architecture:**
- **Vercel**: Frontend (Next.js portal)
- **Supabase**: Database + RLS
- **Railway**: Lynx runtime (Python MCP server)

---

## Quick Start

### 1. Create Railway Project

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo" (or "Empty Project" for manual deploy)
4. Choose your repository

### 2. Configure Service

Railway will auto-detect Python. Configure:

**Root Directory:** `lynx-ai/` (or leave blank if `railway.json` is in root)

**Build Command:** (auto-detected or from `railway.json`)
```bash
uv sync
```

**Start Command:** (from `railway.json` or `Procfile`)
```bash
LYNX_RUNNER=daemon uv run python -m lynx.runtime.daemon
```

**Note:** The `LYNX_RUNNER=daemon` environment variable enables long-running mode. Without it, Lynx initializes and exits (oneshot mode).

### 3. Set Environment Variables

In Railway dashboard → Variables tab, add:

```
LYNX_MODE=staging
LYNX_RUNNER=daemon
KERNEL_API_URL=https://your-kernel-api.example.com
KERNEL_API_KEY=your-kernel-api-key
SUPABASE_URL=https://<project-ref>.supabase.co
SUPABASE_KEY=your-service-role-key
OPENAI_API_KEY=your-openai-api-key
```

**Mark as Secret:** `SUPABASE_KEY`, `OPENAI_API_KEY`, `KERNEL_API_KEY`

**Note:** `LYNX_RUNNER=daemon` enables long-running mode. You can also set it in the start command (already done in `railway.json`).

### 4. Deploy

Railway will:
1. Build: Install dependencies with `uv sync`
2. Deploy: Start `python -m lynx.main`
3. Monitor: Keep service alive, restart on failure

---

## Configuration Files

### `railway.json` (Project Root)

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "cd lynx-ai && uv sync"
  },
  "deploy": {
    "startCommand": "cd lynx-ai && LYNX_RUNNER=daemon uv run python -m lynx.runtime.daemon",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### `lynx-ai/Procfile` (Alternative)

```
web: LYNX_RUNNER=daemon uv run python -m lynx.runtime.daemon
```

---

## How Lynx Runs

### Daemon Mode (Railway/Staging)

Lynx runs as a **long-lived daemon process**:
- Initializes all MCP tools (Domain, Cluster, Cell)
- Stays running with heartbeat logging (every 60s)
- Runs periodic status checks (every 5 minutes)
- Handles graceful shutdown (SIGTERM/SIGINT)
- Waits for MCP client connections (from LLM clients)

**Logs to Watch:**
```
🚀 Starting Lynx AI Daemon...
✅ Configuration loaded
✅ Core components initialized
✅ Audit logger initialized
✅ MCP server initialized
📋 Lynx AI Status:
   ✅ Tools registered: 18
   ✅ Domain MCPs: 12
   ✅ Cluster MCPs: 3
   ✅ Cell MCPs: 3
   ✅ Runner mode: daemon
💚 Daemon running. Waiting for MCP client connections...
   Heartbeat interval: 60s
   Status check interval: 300s

💓 [2026-01-27 10:00:00] Heartbeat #1 | Tools: 18 | Sessions: 0
💓 [2026-01-27 10:01:00] Heartbeat #2 | Tools: 18 | Sessions: 0
📊 [2026-01-27 10:05:00] Status Check #1:
   Status: OPERATIONAL
   Storage: SUPABASE
   Drafts (24h): 0
   Executions (24h): 0
   Pending Settlements: 0
```

### Oneshot Mode (Local Testing)

For local testing, use oneshot mode (default):
```bash
python -m lynx.main  # Initializes and exits
```

This is useful for:
- Smoke tests
- Configuration validation
- Quick status checks

### Future: HTTP API (Optional)

If you add HTTP endpoints (FastAPI/Flask), update `railway.json`:

```json
{
  "deploy": {
    "startCommand": "cd lynx-ai && uv run uvicorn lynx.api:app --host 0.0.0.0 --port $PORT"
  }
}
```

Railway will expose the service at `https://your-app.railway.app`.

---

## Monitoring

### Check Logs

```bash
# In Railway dashboard
# Or via CLI
railway logs
```

### Check Status

```bash
# SSH into Railway service
railway run python -m lynx.cli.status
```

### Health Checks

Railway automatically monitors:
- Process health (restarts on crash)
- Resource usage (CPU, memory)
- Deployment status

---

## Scaling

### Single Service (Current)

One Railway service running Lynx MCP server.

### Multiple Services (Future)

**Service 1: MCP Server**
- Runs `python -m lynx.main`
- Handles MCP tool execution

**Service 2: Worker (Optional)**
- Background jobs (settlement processing, cleanup)
- Separate `Procfile`: `worker: uv run python -m lynx.worker`

**Service 3: HTTP API (Optional)**
- FastAPI endpoints for frontend
- Separate `Procfile`: `api: uv run uvicorn lynx.api:app --host 0.0.0.0 --port $PORT`

---

## Troubleshooting

### Issue: "uv: command not found"

**Solution:** Railway auto-detects Python, but may need explicit installation:

```json
{
  "build": {
    "buildCommand": "pip install uv && cd lynx-ai && uv sync"
  }
}
```

### Issue: "Module not found"

**Solution:** Ensure `railway.json` build command runs from `lynx-ai/` directory:

```json
{
  "build": {
    "buildCommand": "cd lynx-ai && uv sync"
  }
}
```

### Issue: Service exits immediately

**Check:**
1. Environment variables set correctly
2. Supabase connection works
3. Kernel API reachable
4. Check Railway logs for errors

### Issue: "RLS policy violation"

**Solution:** Ensure `SUPABASE_KEY` is the **service_role** key (not anon key). RLS is enforced via `app.tenant_id` in code.

---

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `LYNX_MODE` | Yes | `dev`, `staging`, or `prod` |
| `SUPABASE_URL` | Yes | Supabase project URL |
| `SUPABASE_KEY` | Yes | Supabase service_role key |
| `KERNEL_API_URL` | Yes | Kernel SSOT API URL |
| `KERNEL_API_KEY` | Yes | Kernel API key |
| `OPENAI_API_KEY` | Yes | OpenAI API key (or Anthropic) |

---

## Next Steps

1. ✅ Deploy to Railway
2. ✅ Verify service is running
3. ✅ Run RLS verification tests
4. ✅ Test MCP client connection
5. ✅ Set up monitoring/alerting
6. ✅ Plan production deployment

---

**Status:** ✅ Ready for Railway deployment

