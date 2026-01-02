# Lynx AI Setup Guide

This guide will help you set up the Lynx AI development environment.

---

## Prerequisites

- **Python 3.10+** - Check with `python --version`
- **uv** (recommended) or **pip** - Package manager
- **OpenAI API Key** - Get from [platform.openai.com/api-keys](https://platform.openai.com/api-keys)
- **Kernel API Access** - Your Kernel SSOT API URL and key
- **Supabase Access** - For audit log storage

---

## Step 1: Install uv (Recommended)

```bash
# Install uv using pipx
pipx install uv

# Or using pip
pip install uv
```

---

## Step 2: Set Up Project

```bash
# Navigate to lynx-ai directory
cd lynx-ai

# Initialize uv environment
uv init

# Install dependencies
uv add "mcp-agent[openai]"
uv add pydantic
uv add httpx
uv add supabase
uv add pyyaml
```

---

## Step 3: Configure Environment

### 3.1 Create Configuration Files

```bash
# Copy example configuration
cp config/config.yaml.example config/config.yaml
cp config/secrets.yaml.example config/secrets.yaml
```

### 3.2 Set Environment Variables

**Windows (PowerShell):**
```powershell
$env:OPENAI_API_KEY="sk-..."
$env:KERNEL_API_URL="https://your-kernel-api.com/api"
$env:KERNEL_API_KEY="your-kernel-key"
$env:SUPABASE_URL="https://xxx.supabase.co"
$env:SUPABASE_KEY="your-supabase-key"
```

**Linux/Mac:**
```bash
export OPENAI_API_KEY="sk-..."
export KERNEL_API_URL="https://your-kernel-api.com/api"
export KERNEL_API_KEY="your-kernel-key"
export SUPABASE_URL="https://xxx.supabase.co"
export SUPABASE_KEY="your-supabase-key"
```

### 3.3 Update Configuration Files

Edit `config/config.yaml` and replace `${ENV_VAR}` placeholders with actual values or ensure environment variables are set.

---

## Step 4: Set Up Database (Supabase)

### 4.1 Create Tables

Run these SQL commands in your Supabase SQL editor:

```sql
-- Lynx Runs Table
CREATE TABLE IF NOT EXISTS lynx_runs (
    run_id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    user_query TEXT NOT NULL,
    lynx_response TEXT NOT NULL,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    status VARCHAR(20) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_lynx_runs_tenant ON lynx_runs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_lynx_runs_user ON lynx_runs(user_id);
CREATE INDEX IF NOT EXISTS idx_lynx_runs_timestamp ON lynx_runs(timestamp);

-- Audit Logs Table
CREATE TABLE IF NOT EXISTS audit_logs (
    audit_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    run_id UUID REFERENCES lynx_runs(run_id),
    tool_id VARCHAR(100) NOT NULL,
    user_id UUID NOT NULL,
    tenant_id UUID NOT NULL,
    input JSONB NOT NULL,
    output JSONB,
    risk_level VARCHAR(10) NOT NULL,
    approved BOOLEAN NOT NULL,
    approved_by UUID,
    refused BOOLEAN DEFAULT FALSE,
    refusal_reason TEXT,
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_audit_logs_tenant ON audit_logs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user ON audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_tool ON audit_logs(tool_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs(timestamp);
```

---

## Step 5: Verify Installation

```bash
# Run Lynx AI
uv run python -m lynx.main
```

**Expected Output:**
```
🚀 Starting Lynx AI...
============================================================
✅ Configuration loaded
✅ Core components initialized
✅ Audit logger initialized
✅ MCP server initialized

============================================================
📋 Lynx AI Status:
   ✅ Tools registered: 1
   ✅ Domain MCPs: 1
   ✅ Cluster MCPs: 0
   ✅ Cell MCPs: 0
   ✅ Active sessions: 0
```

---

## Step 6: Development Workflow

### Run Development Server

```bash
# Start Lynx AI
uv run python -m lynx.main

# Or with auto-reload (if using watch mode)
uv run --watch python -m lynx.main
```

### Run Tests

```bash
# Install dev dependencies
uv add --dev pytest pytest-asyncio

# Run tests
uv run pytest
```

---

## Troubleshooting

### Issue: Configuration file not found

**Solution:** Make sure you've copied `config/config.yaml.example` to `config/config.yaml`

### Issue: Environment variables not set

**Solution:** Set all required environment variables (see Step 3.2)

### Issue: Supabase connection failed

**Solution:** 
- Verify Supabase URL and key
- Check network connectivity
- Ensure tables are created (see Step 4.1)

### Issue: Kernel API connection failed

**Solution:**
- Verify Kernel API URL and key
- Check that Kernel API is accessible
- Ensure tenant ID is correct

---

## Next Steps

1. **Study awesome-llm-apps examples** (see `docs/ANALYSIS/ANALYSIS-LYNX-002.md`)
2. **Implement remaining Domain MCPs** (Phase 2)
3. **Implement Cluster MCPs** (Phase 3)
4. **Implement Cell MCPs** (Phase 4)

See `docs/IMPLEMENTATION/IMPLEMENTATION-LYNX-001.md` for detailed implementation plan.

---

**Status:** Foundation setup complete ✅

