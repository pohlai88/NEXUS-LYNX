# Railway Environment Variables - Extracted from .env

**Date:** 2026-01-27  
**Source:** `.env` file  
**Status:** Ready for Railway Configuration

---

## Extracted Variables

### ✅ Available (from .env)

| Variable | Value | Notes |
|----------|-------|-------|
| `SUPABASE_URL` | `https://vrawceruzokxitybkufk.supabase.co` | ✅ Ready |
| `SUPABASE_KEY` | `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` | ✅ Service role key (from SUPABASE_SERVICE_ROLE_KEY) |
| `RAILWAY_PROJECT_URL` | `https://railway.com/project/e06ec2c5-d679-4995-b2b2-48fa302b9221` | ✅ Matches our project |

### ❌ Missing (Required for Lynx)

| Variable | Status | Action Required |
|----------|--------|-----------------|
| `LYNX_MODE` | ❌ Missing | Set to `staging` |
| `LYNX_RUNNER` | ❌ Missing | Set to `daemon` |
| `KERNEL_API_URL` | ❌ Missing | **Need to provide** |
| `KERNEL_API_KEY` | ❌ Missing | **Need to provide** |
| `OPENAI_API_KEY` | ❌ Missing | **Need to provide** |

### ⚠️ Optional (Can use defaults)

| Variable | Default | Notes |
|----------|---------|-------|
| `DAEMON_HEARTBEAT_INTERVAL` | `60` | Optional |
| `DAEMON_STATUS_CHECK_INTERVAL` | `300` | Optional |
| `LOG_LEVEL` | `info` | Optional |

---

## Railway Configuration Commands

### Step 1: Set Available Variables

```powershell
# Set Supabase variables
railway variables set SUPABASE_URL=https://vrawceruzokxitybkufk.supabase.co
railway variables set SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZyYXdjZXJ1em9reGl0eWJrdWZrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NTgxMzEzMywiZXhwIjoyMDgxMzg5MTMzfQ.4WZnLnfHfbAceq3HARshjxtmH12BYlMEyJJTGQvkt3A --secret

# Set Lynx configuration
railway variables set LYNX_MODE=staging
railway variables set LYNX_RUNNER=daemon
```

### Step 2: Set Missing Variables (Need Your Input)

```powershell
# These need to be provided:
railway variables set KERNEL_API_URL=*** --secret
railway variables set KERNEL_API_KEY=*** --secret
railway variables set OPENAI_API_KEY=*** --secret
```

### Step 3: Set Optional Variables (Optional)

```powershell
railway variables set DAEMON_HEARTBEAT_INTERVAL=60
railway variables set DAEMON_STATUS_CHECK_INTERVAL=300
railway variables set LOG_LEVEL=info
```

---

## Complete Railway Variables List

### Required Variables

```bash
LYNX_MODE=staging
LYNX_RUNNER=daemon
SUPABASE_URL=https://vrawceruzokxitybkufk.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZyYXdjZXJ1em9reGl0eWJrdWZrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NTgxMzEzMywiZXhwIjoyMDgxMzg5MTMzfQ.4WZnLnfHfbAceq3HARshjxtmH12BYlMEyJJTGQvkt3A
KERNEL_API_URL=*** [NEED TO PROVIDE]
KERNEL_API_KEY=*** [NEED TO PROVIDE]
OPENAI_API_KEY=*** [NEED TO PROVIDE]
```

### Optional Variables

```bash
DAEMON_HEARTBEAT_INTERVAL=60
DAEMON_STATUS_CHECK_INTERVAL=300
LOG_LEVEL=info
```

---

## Next Steps

1. ✅ **Set Supabase variables** (ready to set)
2. ✅ **Set Lynx configuration** (ready to set)
3. ⏳ **Provide Kernel API credentials** (need your input)
4. ⏳ **Provide OpenAI API key** (need your input)
5. ⏳ **Deploy to Railway**

---

## Questions

**For Kernel API:**
- What is your Kernel API URL?
- What is your Kernel API key?

**For OpenAI:**
- Do you have an OpenAI API key?
- Or are you using Anthropic instead?

---

**Status:** ⏳ Ready to set available variables, waiting for Kernel/OpenAI credentials

