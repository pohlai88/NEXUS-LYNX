# Railway Technical Specification - Complete Reference

**Version:** 1.0.0  
**Date:** 2026-01-27  
**Purpose:** Complete technical specification for Railway deployment - everything needed to build and deploy the dashboard

---

## Table of Contents

1. [Railway Configuration Files](#railway-configuration-files)
2. [Environment Variables (Complete)](#environment-variables-complete)
3. [Build Process](#build-process)
4. [Deployment Process](#deployment-process)
5. [Dashboard Configuration](#dashboard-configuration)
6. [Port Handling](#port-handling)
7. [Railway CLI Commands](#railway-cli-commands)
8. [Service Architecture](#service-architecture)
9. [Branch Mapping Strategy](#branch-mapping-strategy)
10. [Monitoring & Logging](#monitoring--logging)
11. [Troubleshooting Guide](#troubleshooting-guide)
12. [Project Structure](#project-structure)

---

## Railway Configuration Files

### 1. `railway.json` (Project Root)

**Location:** `D:\NexusCanon-Lynx\railway.json`

**Complete Configuration:**
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS",
    "buildCommand": "curl -LsSf https://astral.sh/uv/install.sh | sh && export PATH=\"$HOME/.local/bin:$PATH\" && cd lynx-ai && uv sync"
  },
  "deploy": {
    "startCommand": "cd lynx-ai && export PATH=\"$HOME/.local/bin:$PATH\" && LYNX_RUNNER=daemon uv run python -m lynx.runtime.daemon",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

**Key Details:**
- **Builder:** NIXPACKS (auto-detects Python)
- **Build Command:** Installs `uv`, sets PATH, changes to `lynx-ai/`, runs `uv sync`
- **Start Command:** Sets PATH, changes to `lynx-ai/`, sets `LYNX_RUNNER=daemon`, runs daemon
- **Restart Policy:** Restarts on failure, max 10 retries

**Why `$HOME/.local/bin`?**
- `uv` installer installs to `/root/.local/bin` (not `$HOME/.cargo/bin`)
- PATH must include `$HOME/.local/bin` for `uv` to be found

### 2. `lynx-ai/Procfile` (Alternative Start Command)

**Location:** `D:\NexusCanon-Lynx\lynx-ai\Procfile`

**Content:**
```
web: LYNX_RUNNER=daemon uv run python -m lynx.runtime.daemon
```

**Note:** Railway uses `railway.json` start command, but `Procfile` is a fallback.

### 3. `lynx-ai/pyproject.toml` (Dependencies)

**Location:** `D:\NexusCanon-Lynx\lynx-ai\pyproject.toml`

**Key Dependencies:**
```toml
requires-python = ">=3.10"
dependencies = [
    "mcp-agent[openai]>=0.2.5",
    "pydantic>=2.0.0",
    "httpx>=0.25.0",
    "supabase>=2.0.0",
    "pyyaml>=6.0",
    "fastapi>=0.104.0",        # Dashboard dependency
    "uvicorn[standard]>=0.24.0",  # Dashboard dependency
]
```

**Dashboard Dependencies:**
- `fastapi>=0.104.0` - Web framework for dashboard
- `uvicorn[standard]>=0.24.0` - ASGI server for FastAPI

---

## Environment Variables (Complete)

### Required Environment Variables

#### Core Configuration

| Variable | Value | Description | Secret? | Default |
|----------|-------|-------------|---------|---------|
| `LYNX_MODE` | `staging` \| `prod` \| `dev` | Execution environment | No | None (required) |
| `LYNX_RUNNER` | `daemon` \| `oneshot` | Runner mode | No | `oneshot` |

**Critical:** `LYNX_RUNNER=daemon` is **REQUIRED** for Railway. Without it, the service will initialize and exit immediately.

#### Supabase Configuration

| Variable | Value | Description | Secret? | Default |
|----------|-------|-------------|---------|---------|
| `SUPABASE_URL` | `https://<project-ref>.supabase.co` | Supabase project URL | No | None (required) |
| `SUPABASE_KEY` | `<service-role-key>` | **Service role key** (NOT anon key) | ✅ Yes | None (required) |

**⚠️ CRITICAL:** 
- Use **service_role** key, NOT anon key
- Service role key bypasses RLS for server-side operations
- RLS is still enforced via `app.tenant_id` in code
- Format: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

#### Kernel API Configuration

| Variable | Value | Description | Secret? | Default |
|----------|-------|-------------|---------|---------|
| `KERNEL_API_URL` | `https://your-kernel-api.example.com` | Kernel SSOT API URL | No | None (required*) |
| `KERNEL_API_KEY` | `<kernel-api-key>` | Kernel API authentication key | ✅ Yes | None (required*) |

**Note:** If using `KERNEL_MODE=lite`, these are NOT required.

#### LLM Provider Configuration

| Variable | Value | Description | Secret? | Default |
|----------|-------|-------------|---------|---------|
| `OPENAI_API_KEY` | `sk-...` | OpenAI API key (or Anthropic) | ✅ Yes | None (required) |

### Optional Environment Variables

#### Daemon Configuration

| Variable | Default | Description | Secret? |
|----------|---------|-------------|---------|
| `DAEMON_HEARTBEAT_INTERVAL` | `60` | Heartbeat log interval (seconds) | No |
| `DAEMON_STATUS_CHECK_INTERVAL` | `300` | Status check interval (seconds = 5 minutes) | No |

#### Logging Configuration

| Variable | Default | Description | Secret? |
|----------|---------|-------------|---------|
| `LOG_LEVEL` | `info` | Log level (`debug`, `info`, `warning`, `error`) | No |

#### Maintenance Mode

| Variable | Default | Description | Secret? |
|----------|---------|-------------|---------|
| `LYNX_MAINTENANCE_MODE` | `false` | Enable maintenance mode | No |

#### Kernel Mode (Alternative to Kernel API)

| Variable | Value | Description | Secret? | Default |
|----------|-------|-------------|---------|---------|
| `KERNEL_MODE` | `lite` | Use Kernel Lite mode (no API required) | No | None |

**Note:** If `KERNEL_MODE=lite`, do NOT set `KERNEL_API_URL` or `KERNEL_API_KEY`.

#### Dashboard Configuration

| Variable | Default | Description | Secret? |
|----------|---------|-------------|---------|
| `DASHBOARD_ENABLED` | `true` | Enable/disable dashboard | No |
| `PORT` | `8000` | Port for dashboard server | No |

**⚠️ IMPORTANT:** Railway **automatically sets `PORT`** - do NOT manually set it unless you have a specific reason.

### Complete Environment Variable Example

**Minimum Configuration (Required):**
```bash
LYNX_MODE=staging
LYNX_RUNNER=daemon
SUPABASE_URL=https://vrawceruzokxitybkufk.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # service_role key
KERNEL_MODE=lite  # OR KERNEL_API_URL + KERNEL_API_KEY
OPENAI_API_KEY=sk-...
```

**Recommended Configuration (With Optional):**
```bash
LYNX_MODE=staging
LYNX_RUNNER=daemon
SUPABASE_URL=https://vrawceruzokxitybkufk.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
KERNEL_MODE=lite
OPENAI_API_KEY=sk-...
DAEMON_HEARTBEAT_INTERVAL=60
DAEMON_STATUS_CHECK_INTERVAL=300
LOG_LEVEL=info
DASHBOARD_ENABLED=true
# PORT is set automatically by Railway
```

---

## Build Process

### Build Steps (Automatic)

1. **Railway detects Python project** (via `pyproject.toml`)
2. **Installs `uv`** via curl script
3. **Sets PATH** to include `$HOME/.local/bin`
4. **Changes to `lynx-ai/` directory**
5. **Runs `uv sync`** to install dependencies
6. **Builds Docker image** using Nixpacks

### Build Command Breakdown

```bash
# Step 1: Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Step 2: Set PATH (so uv is found)
export PATH="$HOME/.local/bin:$PATH"

# Step 3: Change to project directory
cd lynx-ai

# Step 4: Install Python dependencies
uv sync
```

### Build Time

- **Typical:** 2-5 minutes
- **Depends on:**
  - Number of dependencies
  - Cache availability
  - Build complexity

### Build Logs to Watch For

**Success Indicators:**
```
✅ Installing uv...
✅ uv installed successfully
✅ Installing dependencies...
✅ All dependencies installed
✅ Build complete
```

**Failure Indicators:**
```
❌ uv: command not found
❌ Module not found: <module>
❌ Build failed
```

---

## Deployment Process

### Deployment Steps (Automatic)

1. **Build completes** (Docker image ready)
2. **Railway starts container**
3. **Runs start command:**
   ```bash
   cd lynx-ai && export PATH="$HOME/.local/bin:$PATH" && LYNX_RUNNER=daemon uv run python -m lynx.runtime.daemon
   ```
4. **Daemon initializes:**
   - Loads configuration
   - Initializes MCP server
   - Registers tools
   - Starts dashboard server (if enabled)
5. **Service becomes available** on Railway public domain

### Start Command Breakdown

```bash
# Step 1: Change to project directory
cd lynx-ai

# Step 2: Set PATH (so uv is found)
export PATH="$HOME/.local/bin:$PATH"

# Step 3: Set daemon mode
LYNX_RUNNER=daemon

# Step 4: Run daemon
uv run python -m lynx.runtime.daemon
```

### Deployment Time

- **Deploy:** 30-60 seconds
- **Startup:** 10-30 seconds
- **Total:** ~1-2 minutes after build

### Expected Startup Logs

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

🌐 Dashboard server started on port 8000
   Access at: http://localhost:8000/
   Health check: http://localhost:8000/health
   API status: http://localhost:8000/api/status

💓 [2026-01-27 10:00:00] Heartbeat #1 | Tools: 18 | Sessions: 0
```

---

## Dashboard Configuration

### Dashboard Architecture

**Runs alongside daemon in same process:**
- Daemon handles MCP server operations
- Dashboard provides HTTP monitoring interface
- Both run in the same container
- Dashboard uses Railway's `PORT` environment variable

### Dashboard Startup

**Location:** `lynx-ai/lynx/runtime/daemon.py`

**Code:**
```python
# Start dashboard server (if enabled)
dashboard_enabled = os.getenv("DASHBOARD_ENABLED", "true").lower() == "true"
if dashboard_enabled:
    try:
        dashboard_port = int(os.getenv("PORT", "8000"))
        start_dashboard_server(dashboard_port)
    except Exception as e:
        print(f"⚠️  Dashboard server failed to start: {e}")
        print("   Continuing without dashboard (daemon will still work)")
```

**Dashboard Server:** `lynx-ai/lynx/runtime/dashboard_server.py`

**FastAPI App:** `lynx-ai/lynx/api/dashboard.py`

### Dashboard Endpoints

| Endpoint | Method | Description | Response |
|----------|--------|-------------|----------|
| `/` | GET | Dashboard home page | HTML |
| `/health` | GET | Health check (JSON) | `{"status": "operational", ...}` |
| `/api/status` | GET | Complete system status (JSON) | Full status object |
| `/api/metrics` | GET | Metrics for Prometheus | Metrics format |
| `/dashboard` | GET | Dashboard page (alias for `/`) | HTML |
| `/dashboard/_kpis` | GET | KPI fragment (for auto-refresh) | HTML fragment |
| `/dashboard/_services` | GET | Services fragment | HTML fragment |
| `/dashboard/_recent` | GET | Recent executions fragment | HTML fragment |
| `/dashboard/_cockpit` | GET | Developer cockpit fragment | HTML fragment |
| `/static/aibos-design-system.css` | GET | AIBOS CSS file | CSS |

### Dashboard Features

1. **Auto-refresh:** Every 30 seconds (via JavaScript)
2. **Fragment updates:** Only updates changed sections
3. **Dark theme:** AIBOS design system
4. **Responsive:** Works on mobile and desktop

### Dashboard Access

**After Deployment:**
1. Get Railway public domain:
   ```powershell
   railway domain
   ```
2. Access dashboard:
   ```
   https://<your-railway-domain>.railway.app/
   ```

**Local Development:**
```powershell
cd lynx-ai
PORT=8000 uv run python -m lynx.runtime.daemon
# Access at: http://localhost:8000/
```

---

## Port Handling

### Railway Automatic Port Assignment

**Railway automatically:**
1. Sets `PORT` environment variable
2. Exposes service on public domain
3. Routes HTTP traffic to the service

**You do NOT need to:**
- Manually set `PORT` (Railway sets it)
- Configure port mapping
- Set up reverse proxy

### Port Usage

**Dashboard Server:**
- Listens on `0.0.0.0:$PORT`
- Railway routes external traffic to this port
- Default fallback: `8000` (if `PORT` not set)

**Code:**
```python
port = int(os.getenv("PORT", "8000"))
config = uvicorn.Config(
    app,
    host="0.0.0.0",  # Listen on all interfaces
    port=port,        # Use Railway's PORT
    ...
)
```

### Port Configuration

**Environment Variable:**
```bash
PORT=8000  # Railway sets this automatically
```

**Manual Override (if needed):**
```bash
PORT=3000  # Only if you need a specific port
```

**Note:** Railway sets `PORT` automatically - manual override is rarely needed.

---

## Railway CLI Commands

### Installation

**Windows (PowerShell):**
```powershell
irm https://railway.app/install.ps1 | iex
```

**Mac/Linux:**
```bash
curl -fsSL https://railway.app/install.sh | sh
```

### Authentication

```powershell
railway login
```

### Project Management

```powershell
# Link to project
railway link

# Unlink project
railway unlink

# List all projects
railway list

# Open dashboard
railway open

# Show project status
railway status
```

### Service Management

```powershell
# Link to service
railway service

# SSH into service
railway ssh

# Run command in service environment
railway run <command>
```

### Environment Variables

```powershell
# List all variables
railway variables

# Set variable
railway variables --set "KEY=value"

# Set multiple variables
railway variables --set "KEY1=value1" --set "KEY2=value2"

# JSON output
railway variables --json
```

**Note:** Railway CLI doesn't have `--secret` flag. Mark secrets in Railway dashboard.

### Deployment

```powershell
# Deploy current directory
railway up

# Redeploy latest
railway redeploy

# Redeploy specific service
railway redeploy --service lynx-ai
```

### Logs

```powershell
# Stream live logs
railway logs

# Get last N lines (non-streaming)
railway logs --lines 100

# View build logs
railway logs --build --lines 100

# View deployment logs
railway logs --deployment --lines 100

# Filter logs (errors only)
railway logs --lines 50 --filter "@level:error"

# JSON format
railway logs --lines 100 --json
```

**Note:** Use `--lines` (not `--tail`) for consistency.

### Deployment Management

```powershell
# List deployments
railway deployment list

# View specific deployment
railway deployment view <deployment-id>

# View deployment logs
railway logs --deployment <deployment-id>
```

### Domain Management

```powershell
# Get public domain
railway domain

# Generate domain
railway domain generate
```

---

## Service Architecture

### Single Service Architecture (Current)

**Service:** `lynx-ai`
- **Type:** Long-lived daemon
- **Mode:** Daemon (`LYNX_RUNNER=daemon`)
- **Components:**
  - MCP Server (handles tool execution)
  - Dashboard Server (HTTP monitoring interface)
  - Both run in same process

### Process Structure

```
Railway Container
├── Main Process: python -m lynx.runtime.daemon
│   ├── MCP Server (stdin/stdout)
│   ├── Dashboard Server (background thread, port $PORT)
│   └── Daemon Loop (heartbeat, status checks)
└── Environment Variables (Railway sets)
```

### Future: Multi-Service Architecture (Optional)

**Service 1: MCP Server**
- Runs `python -m lynx.runtime.daemon`
- Handles MCP tool execution
- No HTTP endpoints

**Service 2: Dashboard API (Optional)**
- FastAPI endpoints
- Separate service
- Connects to MCP server

**Service 3: Worker (Optional)**
- Background jobs
- Settlement processing
- Cleanup tasks

---

## Branch Mapping Strategy

### Recommended: Separate Services

**Staging Service:** `lynx-staging`
- **Branch:** `main`
- **Auto-deploy:** ✅ Yes
- **Environment:** `LYNX_MODE=staging`

**Production Service:** `lynx-prod`
- **Branch:** `prod` or `production`
- **Auto-deploy:** ❌ No (manual deploy)
- **Environment:** `LYNX_MODE=prod`

### Branch-Specific Environment Variables

Railway allows setting environment variables per branch:

**For `main` branch:**
```bash
LYNX_MODE=staging
```

**For `prod` branch:**
```bash
LYNX_MODE=prod
```

### Setup Steps

1. **Create two services** in Railway
2. **Connect each to different branch**
3. **Set environment variables per service**
4. **Configure auto-deploy** (staging: yes, prod: no)

---

## Monitoring & Logging

### Log Types

1. **Build Logs:** Installation, dependency resolution
2. **Deployment Logs:** Service startup, initialization
3. **Runtime Logs:** Heartbeat, status checks, errors

### Log Levels

- **DEBUG:** Detailed debugging information
- **INFO:** General information (heartbeat, status)
- **WARNING:** Warnings (non-critical issues)
- **ERROR:** Errors (critical issues)

### Monitoring Endpoints

**Dashboard:**
- `/health` - Quick health check
- `/api/status` - Complete status
- `/api/metrics` - Prometheus metrics

### Expected Log Patterns

**Heartbeat (every 60s):**
```
💓 [2026-01-27 10:00:00] Heartbeat #1 | Tools: 18 | Sessions: 0
```

**Status Check (every 5 minutes):**
```
📊 [2026-01-27 10:05:00] Status Check #1:
   Status: OPERATIONAL
   Storage: SUPABASE
   Drafts (24h): 0
   Executions (24h): 0
   Pending Settlements: 0
```

---

## Troubleshooting Guide

### Issue: Service Exits Immediately

**Symptoms:**
- Service starts then exits
- No heartbeat logs
- Deployment shows "crashed"

**Causes:**
1. `LYNX_RUNNER=daemon` not set
2. Missing environment variables
3. Configuration errors
4. Database connection failed

**Solutions:**
1. Verify `LYNX_RUNNER=daemon` is set
2. Check all required env vars are set
3. Review logs for specific errors
4. Test Supabase connection

### Issue: Build Fails

**Symptoms:**
- Build logs show errors
- `uv: command not found`
- `Module not found`

**Solutions:**
1. Check `railway.json` build command
2. Verify PATH includes `$HOME/.local/bin`
3. Check `pyproject.toml` dependencies
4. Review build logs for specific errors

### Issue: Dashboard Not Accessible

**Symptoms:**
- Dashboard URL returns 404 or connection refused
- No dashboard startup message in logs

**Solutions:**
1. Verify `DASHBOARD_ENABLED=true` (or not set, defaults to true)
2. Check `PORT` is set (Railway sets automatically)
3. Check service is running
4. Review logs for dashboard startup errors

### Issue: Database Connection Failed

**Symptoms:**
- Storage backend shows "MEMORY" instead of "SUPABASE"
- Connection errors in logs

**Solutions:**
1. Verify `SUPABASE_URL` is correct
2. Verify `SUPABASE_KEY` is service_role key (not anon)
3. Test connection in Supabase dashboard
4. Check network connectivity

---

## Project Structure

### Key Files

```
D:\NexusCanon-Lynx\
├── railway.json                    # Railway configuration
├── lynx-ai/
│   ├── Procfile                    # Alternative start command
│   ├── pyproject.toml              # Python dependencies
│   ├── lynx/
│   │   ├── runtime/
│   │   │   ├── daemon.py           # Main daemon entry point
│   │   │   └── dashboard_server.py # Dashboard server
│   │   └── api/
│   │       └── dashboard.py        # FastAPI dashboard app
│   └── ...
└── docs/
    └── DEPLOYMENT/
        └── RAILWAY-TECHNICAL-SPEC.md  # This file
```

### Configuration Files

1. **`railway.json`** - Railway build and deploy config
2. **`lynx-ai/pyproject.toml`** - Python dependencies
3. **`lynx-ai/Procfile`** - Alternative start command (fallback)

---

## Quick Reference

### Minimum Setup Checklist

- [ ] Railway project created
- [ ] Service linked
- [ ] `LYNX_MODE=staging` set
- [ ] `LYNX_RUNNER=daemon` set
- [ ] `SUPABASE_URL` set
- [ ] `SUPABASE_KEY` set (service_role key)
- [ ] `KERNEL_MODE=lite` OR `KERNEL_API_URL` + `KERNEL_API_KEY` set
- [ ] `OPENAI_API_KEY` set
- [ ] All secrets marked as "Secret" in Railway
- [ ] `railway.json` configured correctly
- [ ] Deployed and running

### Success Criteria

- [ ] Service stays alive (no immediate exits)
- [ ] Startup banner appears in logs
- [ ] Heartbeat logs appear every 60 seconds
- [ ] Status check logs appear every 5 minutes
- [ ] Dashboard accessible on Railway domain
- [ ] `/health` endpoint returns 200
- [ ] `/api/status` endpoint returns complete status
- [ ] No error spam in logs

---

## Additional Resources

### Railway Documentation
- Railway Docs: https://docs.railway.app
- Railway CLI: https://docs.railway.app/develop/cli

### Related Documents
- `DASHBOARD-SETUP.md` - Dashboard configuration
- `STAGING-CHECKLIST.md` - Complete deployment checklist

---

**Status:** ✅ Complete Technical Specification  
**Last Updated:** 2026-01-27  
**Version:** 1.0.0

