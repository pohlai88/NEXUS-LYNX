# CLI Setup Guide — Railway & GitHub

**Version:** 1.0.0  
**Date:** 2026-01-27  
**Status:** Setup Instructions

---

## Current Status

✅ **Railway CLI:** Installed (v4.11.1)  
✅ **GitHub CLI:** Installed (v2.83.2)  
✅ **GitHub CLI:** Authenticated as `pohlai88`  
❌ **Railway CLI:** Not logged in (requires interactive login)

---

## Step 1: Login to Railway CLI

Railway login requires interactive mode (opens browser). Run this command manually:

```powershell
railway login
```

**What happens:**
1. Command opens your default browser
2. You'll be prompted to authorize Railway CLI
3. After authorization, you'll be logged in

**Verify login:**
```powershell
railway whoami
```

**Expected output:**
```
Logged in as: your-email@example.com
```

---

## Step 2: Verify GitHub CLI

GitHub CLI is already authenticated. Verify:

```powershell
gh auth status
```

**Expected output:**
```
github.com
  ✓ Logged in to github.com account pohlai88 (GITHUB_TOKEN)
  - Active account: true
```

---

## Step 3: Link Railway to Your Project

Once logged in to Railway, link your project:

### Option A: Link Existing Railway Project

```powershell
# Navigate to project root
cd D:\NexusCanon-Lynx

# Link to existing Railway project
railway link
```

**What happens:**
1. Railway CLI will list your projects
2. Select the project you want to link
3. Creates `.railway` directory with project config

### Option B: Create New Railway Project

```powershell
# Navigate to project root
cd D:\NexusCanon-Lynx

# Create new Railway project
railway init
```

**What happens:**
1. Prompts for project name
2. Creates new Railway project
3. Links current directory to project

---

## Step 4: Verify Repository Connection

### Check GitHub Repository

```powershell
# Check current repository
gh repo view

# Or check git remote
git remote -v
```

**Expected output:**
```
owner/repo-name
```

### Check Railway Project

```powershell
# Check linked Railway project
railway status

# Or check Railway config
cat .railway/project.json
```

---

## Step 5: Set Environment Variables via CLI (Optional)

Once linked, you can set environment variables via CLI:

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

**Note:** Variables marked with `--secret` are hidden in logs.

---

## Step 6: Deploy via CLI (Optional)

You can deploy directly from CLI:

```powershell
# Deploy current branch
railway up

# Deploy specific branch
railway up --branch main

# View deployment logs
railway logs

# View service status
railway status
```

---

## Quick Reference Commands

### Railway CLI

```powershell
# Authentication
railway login              # Login (interactive)
railway logout             # Logout
railway whoami             # Check current user

# Project Management
railway init               # Create new project
railway link               # Link to existing project
railway unlink             # Unlink from project

# Environment Variables
railway variables          # List all variables
railway variables set KEY=value        # Set variable
railway variables set KEY=value --secret  # Set secret variable
railway variables delete KEY           # Delete variable

# Deployment
railway up                 # Deploy current branch
railway up --branch main   # Deploy specific branch
railway logs               # View logs
railway status             # Check service status
railway open               # Open project in browser
```

### GitHub CLI

```powershell
# Authentication
gh auth status             # Check auth status
gh auth login              # Login (if needed)
gh auth logout             # Logout

# Repository
gh repo view               # View current repo
gh repo clone owner/repo   # Clone repository
gh repo create             # Create new repository

# Pull Requests
gh pr list                 # List pull requests
gh pr create               # Create pull request
gh pr view                 # View current PR

# Issues
gh issue list              # List issues
gh issue create            # Create issue
gh issue view              # View issue
```

---

## Troubleshooting

### Issue: Railway login fails

**Solution:**
1. Check internet connection
2. Try `railway login --browserless` (if available)
3. Or login via Railway dashboard and use token:
   ```powershell
   railway login --token YOUR_TOKEN
   ```

### Issue: Railway link fails

**Solution:**
1. Ensure you're logged in: `railway whoami`
2. Check you're in the correct directory
3. Try `railway init` to create new project instead

### Issue: GitHub CLI not authenticated

**Solution:**
```powershell
gh auth login
```

Follow the prompts to authenticate.

---

## Next Steps

After CLI setup:

1. ✅ Login to Railway CLI
2. ✅ Link Railway project
3. ✅ Set environment variables (via UI or CLI)
4. ✅ Deploy to Railway
5. ✅ Verify deployment logs

---

**Status:** ⏳ Waiting for Railway CLI login

**Action Required:** Run `railway login` manually in your terminal (requires browser)

