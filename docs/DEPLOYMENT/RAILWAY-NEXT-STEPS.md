# Railway Next Steps - Ready for Configuration

**Date:** 2026-01-27  
**Status:** ✅ Project Created | ⏳ Ready for Environment Variables

---

## ✅ Completed

- [x] Railway CLI installed (v4.11.1)
- [x] GitHub CLI installed (v2.83.2)
- [x] Railway CLI logged in (jackwee@ai-bos.io)
- [x] Railway project created (`lynx-staging`)
- [x] Project linked to repository
- [x] `railway.json` configured correctly

---

## ⏳ Next Steps

### Step 1: Set Environment Variables

**Option A: Via Railway Dashboard (Recommended)**

1. Open Railway project: https://railway.com/project/e06ec2c5-d679-4995-b2b2-48fa302b9221
2. Click on your service (or create one if it doesn't exist)
3. Go to **Variables** tab
4. Add the following variables:

**Required Variables:**
```
LYNX_MODE=staging
LYNX_RUNNER=daemon
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-service-role-key
KERNEL_API_URL=https://your-kernel-api.com
KERNEL_API_KEY=your-kernel-key
OPENAI_API_KEY=your-openai-key
```

**Optional Variables:**
```
DAEMON_HEARTBEAT_INTERVAL=60
DAEMON_STATUS_CHECK_INTERVAL=300
LOG_LEVEL=info
```

**⚠️ Important:** Mark these as **Secret** in Railway:
- `SUPABASE_KEY`
- `KERNEL_API_KEY`
- `OPENAI_API_KEY`

**Option B: Via Railway CLI**

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
railway variables set LOG_LEVEL=info
```

### Step 2: Verify Configuration

Check that variables are set:
```powershell
railway variables
```

### Step 3: Connect GitHub Repository (if not already connected)

1. Go to Railway project dashboard
2. Click **Settings** → **Source**
3. Connect your GitHub repository: `pohlai88/NEXUS-LYNX`
4. Select branch: `main` (for staging)
5. Enable **Auto-deploy** (optional)

### Step 4: Deploy

**Option A: Auto-deploy (if GitHub connected)**
- Push to `main` branch
- Railway will automatically deploy

**Option B: Manual deploy**
```powershell
railway up
```

### Step 5: Verify Deployment

**Check logs:**
```powershell
railway logs
```

**Expected logs:**
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

💚 Daemon running. Waiting for MCP client connections...
💓 [timestamp] Heartbeat #1 | Tools: 18 | Sessions: 0
```

---

## Current Configuration

**Project:** `lynx-staging`  
**Project URL:** https://railway.com/project/e06ec2c5-d679-4995-b2b2-48fa302b9221  
**Account:** jackwee@ai-bos.io  
**Repository:** `pohlai88/NEXUS-LYNX`

**Build Command:** `cd lynx-ai && uv sync`  
**Start Command:** `cd lynx-ai && LYNX_RUNNER=daemon uv run python -m lynx.runtime.daemon`

---

## Environment Variables Checklist

Before deploying, ensure you have:

- [ ] `LYNX_MODE=staging`
- [ ] `LYNX_RUNNER=daemon`
- [ ] `SUPABASE_URL` (your Supabase project URL)
- [ ] `SUPABASE_KEY` (service_role key, marked as Secret)
- [ ] `KERNEL_API_URL` (your Kernel API URL)
- [ ] `KERNEL_API_KEY` (marked as Secret)
- [ ] `OPENAI_API_KEY` (marked as Secret)
- [ ] Optional: `DAEMON_HEARTBEAT_INTERVAL=60`
- [ ] Optional: `DAEMON_STATUS_CHECK_INTERVAL=300`

---

## Quick Commands Reference

```powershell
# Check project status
railway status

# List variables
railway variables

# Set variable
railway variables set KEY=value

# Set secret variable
railway variables set KEY=value --secret

# Deploy
railway up

# View logs
railway logs

# Open in browser
railway open
```

---

## Troubleshooting

### Issue: Service not found

**Solution:** Railway will auto-create a service on first deploy. Or create one via Railway dashboard.

### Issue: Variables not applying

**Solution:** 
1. Verify variables are set: `railway variables`
2. Check they're set for the correct service/environment
3. Redeploy: `railway up`

### Issue: Build fails

**Solution:**
1. Check build command in `railway.json`
2. Verify `uv` is available in Railway environment
3. Check Railway logs for specific errors

---

**Status:** ✅ Ready for environment variable configuration  
**Next Action:** Set environment variables (via UI or CLI), then deploy

