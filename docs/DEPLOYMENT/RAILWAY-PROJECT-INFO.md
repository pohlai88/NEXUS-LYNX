# Railway Project Information

**Date:** 2026-01-27  
**Status:** ✅ Project Created & Linked

---

## Project Details

- **Project Name:** `lynx-staging`
- **Project URL:** https://railway.com/project/e06ec2c5-d679-4995-b2b2-48fa302b9221
- **Workspace:** pohlai88's Projects
- **Account:** jackwee@ai-bos.io
- **Status:** ✅ Linked
- **Service:** Will be auto-created on first deploy

---

## Next Steps

### 1. Set Environment Variables

You can set environment variables via Railway UI or CLI:

**Via Railway UI:**
1. Go to: https://railway.com/project/e06ec2c5-d679-4995-b2b2-48fa302b9221
2. Click on your service → Variables tab
3. Add all required variables (see RAILWAY-ENV-VARS.md)

**Via CLI:**
```powershell
# Set required variables
railway variables set LYNX_MODE=staging
railway variables set LYNX_RUNNER=daemon
railway variables set SUPABASE_URL=https://your-project.supabase.co
railway variables set SUPABASE_KEY=your-key --secret
railway variables set KERNEL_API_URL=https://your-kernel-api.com
railway variables set KERNEL_API_KEY=your-key --secret
railway variables set OPENAI_API_KEY=your-key --secret

# Set optional variables
railway variables set DAEMON_HEARTBEAT_INTERVAL=60
railway variables set DAEMON_STATUS_CHECK_INTERVAL=300
```

### 2. Verify Configuration

Check that `railway.json` is correct:
- Build command: `cd lynx-ai && uv sync`
- Start command: `cd lynx-ai && LYNX_RUNNER=daemon uv run python -m lynx.runtime.daemon`

### 3. Deploy

Once environment variables are set:
```powershell
railway up
```

Or Railway will auto-deploy when you push to the connected branch.

---

## Current Configuration

**Build Command:** `cd lynx-ai && uv sync`  
**Start Command:** `cd lynx-ai && LYNX_RUNNER=daemon uv run python -m lynx.runtime.daemon`

**Configuration File:** `railway.json` (at project root)

---

## Environment Variables Status

Check current variables:
```powershell
railway variables
```

**Required Variables:**
- [ ] `LYNX_MODE=staging`
- [ ] `LYNX_RUNNER=daemon`
- [ ] `SUPABASE_URL=...`
- [ ] `SUPABASE_KEY=...` (secret)
- [ ] `KERNEL_API_URL=...`
- [ ] `KERNEL_API_KEY=...` (secret)
- [ ] `OPENAI_API_KEY=...` (secret)

**Optional Variables:**
- [ ] `DAEMON_HEARTBEAT_INTERVAL=60`
- [ ] `DAEMON_STATUS_CHECK_INTERVAL=300`

---

## Deployment

**Auto-deploy:** Railway will deploy when you push to the connected branch (usually `main`)

**Manual deploy:**
```powershell
railway up
```

**View logs:**
```powershell
railway logs
```

**Check status:**
```powershell
railway status
```

---

**Status:** ✅ Project created and linked  
**Next:** Set environment variables and deploy

