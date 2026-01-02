# Railway Branch → Environment Mapping Guide

**Version:** 1.0.0  
**Date:** 2026-01-27  
**Purpose:** Guide for setting up branch-based deployments in Railway

---

## Overview

Railway supports branch-based deployments, allowing you to:
- Auto-deploy staging from `main` branch
- Deploy production from `prod` branch (manual or auto)
- Test features in preview deployments

---

## Recommended Strategies

### Strategy 1: Separate Services (Recommended for Staging/Prod Split)

**Setup:**
- **Staging Service:** `lynx-staging`
  - Branch: `main`
  - Auto-deploy: ✅ Yes
  - Environment: `LYNX_MODE=staging`
  
- **Production Service:** `lynx-prod`
  - Branch: `prod` or `production`
  - Auto-deploy: ❌ No (manual deploy for safety)
  - Environment: `LYNX_MODE=prod`

**Pros:**
- Clear separation of staging and production
- Independent scaling and configuration
- Easy to test production config in staging first

**Cons:**
- Requires managing two services
- Slightly more complex setup

**Best For:** Teams that want strict staging/prod separation

---

### Strategy 2: Single Service with Branch-based Config

**Setup:**
- **Single Service:** `lynx`
  - Branch: `main` (staging) or `prod` (production)
  - Auto-deploy: ✅ Yes for staging, ❌ No for production
  - Environment: `LYNX_MODE` changes based on branch

**Configuration:**
```bash
# In Railway, set branch-specific environment variables
# For main branch:
LYNX_MODE=staging

# For prod branch:
LYNX_MODE=prod
```

**Pros:**
- Simpler setup (one service)
- Lower cost (one service instead of two)
- Easy to switch between environments

**Cons:**
- Risk of deploying wrong branch to wrong environment
- Less isolation between staging and production

**Best For:** Small teams or projects with tight budgets

---

### Strategy 3: Preview Deployments (Advanced)

**Setup:**
- **Staging Service:** `lynx-staging`
  - Branch: `main`
  - Auto-deploy: ✅ Yes
  
- **Production Service:** `lynx-prod`
  - Branch: `prod`
  - Auto-deploy: ❌ No (manual)
  
- **Preview Deployments:** Auto-created for PRs
  - Branch: `feature/*` or any PR branch
  - Auto-deploy: ✅ Yes (on PR open)
  - Environment: `LYNX_MODE=dev` or `staging`

**Pros:**
- Test features in isolated environments
- No risk to staging/production
- Great for collaboration

**Cons:**
- More complex setup
- Higher cost (multiple deployments)

**Best For:** Teams with active feature development

---

## Railway Branch Configuration

### Setting Up Branch Deployments

1. **In Railway Dashboard:**
   - Go to Service → Settings → Source
   - Select branch for deployment
   - Enable/disable auto-deploy

2. **For Separate Services:**
   - Create two services
   - Connect each to different branch
   - Set environment variables per service

3. **For Single Service:**
   - Use Railway's branch-specific environment variables
   - Or use Railway CLI to set per-branch config

### Branch-Specific Environment Variables

Railway allows setting environment variables per branch:

```bash
# In Railway UI → Variables → Add Variable
# Set "Apply to branches" to specific branch

# For main branch:
LYNX_MODE=staging

# For prod branch:
LYNX_MODE=prod
```

---

## Recommended Setup for Lynx AI

### Phase 1: Staging Only (Current)

**Service:** `lynx-staging`
- **Branch:** `main`
- **Auto-deploy:** ✅ Yes
- **Environment:** `LYNX_MODE=staging`

**Why:** Start simple, validate staging works, then add production later.

### Phase 2: Add Production (After Staging Validated)

**Staging Service:** `lynx-staging`
- **Branch:** `main`
- **Auto-deploy:** ✅ Yes
- **Environment:** `LYNX_MODE=staging`

**Production Service:** `lynx-prod`
- **Branch:** `prod`
- **Auto-deploy:** ❌ No (manual deploy)
- **Environment:** `LYNX_MODE=prod`

**Why:** Separate services provide better isolation and safety.

---

## Migration Path

### Step 1: Deploy Staging (Now)

1. Create Railway project
2. Connect to `main` branch
3. Set `LYNX_MODE=staging`
4. Deploy and validate

### Step 2: Add Production (Later)

1. Create new Railway service (or duplicate staging service)
2. Connect to `prod` branch
3. Set `LYNX_MODE=prod`
4. Configure manual deploy only
5. Test production deployment

### Step 3: Add Preview Deployments (Optional)

1. Enable Railway preview deployments
2. Configure for `feature/*` branches
3. Set `LYNX_MODE=dev` for previews

---

## Environment Variable Differences

### Staging vs Production

| Variable | Staging | Production |
|----------|---------|------------|
| `LYNX_MODE` | `staging` | `prod` |
| `LYNX_RUNNER` | `daemon` | `daemon` |
| `SUPABASE_URL` | Staging Supabase | Production Supabase |
| `SUPABASE_KEY` | Staging service_role | Production service_role |
| `KERNEL_API_URL` | Staging Kernel | Production Kernel |
| `KERNEL_API_KEY` | Staging key | Production key |
| `OPENAI_API_KEY` | Same (or staging key) | Production key |
| `DAEMON_HEARTBEAT_INTERVAL` | `60` | `60` |
| `DAEMON_STATUS_CHECK_INTERVAL` | `300` | `300` |
| `LOG_LEVEL` | `info` or `debug` | `info` |
| `LYNX_MAINTENANCE_MODE` | `false` | `false` |

**Key Differences:**
- Different Supabase projects (staging vs prod)
- Different Kernel API endpoints (if applicable)
- Potentially different API keys
- Same daemon configuration

---

## Safety Checklist

Before enabling production:

- [ ] Staging validated and working
- [ ] RLS tests passing in staging
- [ ] End-to-end smoke tests passing
- [ ] Graceful shutdown verified
- [ ] Monitoring set up
- [ ] Rollback procedure documented
- [ ] Production environment variables reviewed
- [ ] Production Supabase schema applied
- [ ] Production Kernel API accessible
- [ ] Manual deploy only (no auto-deploy for prod)

---

## Railway CLI Commands (Optional)

If using Railway CLI:

```bash
# Link to project
railway link

# Set environment variable for specific branch
railway variables set LYNX_MODE=staging --branch main
railway variables set LYNX_MODE=prod --branch prod

# Deploy specific branch
railway up --branch main
railway up --branch prod

# View logs
railway logs --branch main
railway logs --branch prod
```

---

## Troubleshooting

### Issue: Wrong branch deploying

**Solution:** Check Railway service settings → Source → Branch

### Issue: Environment variables not applying

**Solution:** Verify branch-specific variables are set correctly in Railway UI

### Issue: Auto-deploy not working

**Solution:** Check Railway service settings → Source → Auto-deploy enabled

---

**Status:** ✅ Ready for branch mapping configuration

