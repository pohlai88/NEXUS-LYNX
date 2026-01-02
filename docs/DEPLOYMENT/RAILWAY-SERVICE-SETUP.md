# Railway Service Setup - Step by Step

**Date:** 2026-01-27  
**Status:** Creating Service

---

## Current Step: Add Service

Railway CLI is asking: **"What do you need?"**

### ✅ Select: **Empty Service** (Option 4)

This will create a new empty service that we'll configure for Lynx.

**After selecting "Empty Service":**
1. Railway will create a new service
2. You'll be able to set environment variables
3. You'll be able to deploy

---

## Next Steps After Service Creation

### Step 1: Set Environment Variables

Once the service is created, set variables using the correct Railway CLI syntax:

```powershell
# Set required variables (using --set flag)
railway variables --set "LYNX_MODE=staging"
railway variables --set "LYNX_RUNNER=daemon"
railway variables --set "SUPABASE_URL=https://vrawceruzokxitybkufk.supabase.co"
railway variables --set "SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZyYXdjZXJ1em9reGl0eWJrdWZrIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NTgxMzEzMywiZXhwIjoyMDgxMzg5MTMzfQ.4WZnLnfHfbAceq3HARshjxtmH12BYlMEyJJTGQvkt3A"

# Set optional variables
railway variables --set "DAEMON_HEARTBEAT_INTERVAL=60"
railway variables --set "DAEMON_STATUS_CHECK_INTERVAL=300"
```

**Note:** For secret variables, Railway will prompt you or you can mark them in the dashboard.

### Step 2: Set Missing Variables (Need Your Input)

You'll still need to provide:
- `KERNEL_API_URL`
- `KERNEL_API_KEY`
- `OPENAI_API_KEY`

### Step 3: Verify Configuration

```powershell
# Check all variables
railway variables

# Check service status
railway status
```

### Step 4: Deploy

```powershell
railway up
```

---

## Railway CLI Variable Syntax

**Correct syntax:**
```powershell
railway variables --set "KEY=value"
railway variables --set "KEY1=value1" --set "KEY2=value2"
```

**Incorrect syntax (what we tried before):**
```powershell
railway variables set KEY=value  # ❌ Wrong
```

---

## Environment Variables Ready to Set

From your `.env` file, we have:

✅ **Ready to set:**
- `LYNX_MODE=staging`
- `LYNX_RUNNER=daemon`
- `SUPABASE_URL=https://vrawceruzokxitybkufk.supabase.co`
- `SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (service role key)
- `DAEMON_HEARTBEAT_INTERVAL=60`
- `DAEMON_STATUS_CHECK_INTERVAL=300`

⏳ **Need to provide:**
- `KERNEL_API_URL=...`
- `KERNEL_API_KEY=...`
- `OPENAI_API_KEY=...`

---

**Action:** Select "Empty Service" in the Railway CLI prompt, then we'll set the variables.

