# Railway Configuration Template

**Purpose:** Fill in this template with your Railway environment variables and branch mapping, then share for sanity-checking.

**Instructions:**
1. Fill in all `***` placeholders with your actual values (or mark as "not set" if not applicable)
2. Mark secrets with `[SECRET]` tag
3. Complete the branch mapping section
4. Share the completed template for review

---

## Railway Environment Variables

### Core Configuration

```bash
LYNX_MODE=***
# Options: dev, staging, prod
# Your value: [FILL IN]

LYNX_RUNNER=***
# Options: oneshot, daemon
# Your value: [FILL IN - should be "daemon" for Railway]
```

### Supabase Configuration

```bash
SUPABASE_URL=***
# Format: https://<project-ref>.supabase.co
# Your value: [FILL IN]
# Example: https://abcdefghijklmnop.supabase.co

SUPABASE_KEY=***
# ⚠️ MUST be service_role key (not anon key)
# Your value: [FILL IN - REDACT FOR SECURITY]
# Mark as Secret in Railway: [YES/NO]
```

### Kernel API Configuration

```bash
KERNEL_API_URL=***
# Your Kernel SSOT API URL
# Your value: [FILL IN]
# Example: https://kernel.nexuscanon.com/api

KERNEL_API_KEY=***
# Your Kernel API authentication key
# Your value: [FILL IN - REDACT FOR SECURITY]
# Mark as Secret in Railway: [YES/NO]
```

### LLM Provider Configuration

```bash
OPENAI_API_KEY=***
# OpenAI API key (or Anthropic if using Anthropic)
# Your value: [FILL IN - REDACT FOR SECURITY]
# Mark as Secret in Railway: [YES/NO]
# Provider: [OpenAI/Anthropic/Other]
```

### Optional: Daemon Configuration

```bash
DAEMON_HEARTBEAT_INTERVAL=***
# Default: 60 (seconds)
# Your value: [FILL IN or leave default]

DAEMON_STATUS_CHECK_INTERVAL=***
# Default: 300 (seconds = 5 minutes)
# Your value: [FILL IN or leave default]
```

### Optional: Logging Configuration

```bash
LOG_LEVEL=***
# Default: info
# Options: debug, info, warning, error
# Your value: [FILL IN or leave default]
```

### Optional: Maintenance Mode

```bash
LYNX_MAINTENANCE_MODE=***
# Default: false
# Your value: [FILL IN or leave default]
```

---

## Railway Service Configuration

### Build Command

```bash
cd lynx-ai && uv sync
```

**Status:** [ ] Confirmed in Railway UI  
**Notes:** [Any issues or customizations?]

### Start Command

```bash
cd lynx-ai && LYNX_RUNNER=daemon uv run python -m lynx.runtime.daemon
```

**Status:** [ ] Confirmed in Railway UI  
**Notes:** [Any issues or customizations?]

### Root Directory

**Railway Setting:** [FILL IN - usually "project root" or blank]  
**Notes:** [Any custom root directory?]

---

## Branch → Environment Mapping

### Current Setup

**Staging Environment:**
- **Branch:** `***`
  - Options: `main`, `develop`, `staging`, `staging/*`
  - Your branch: [FILL IN]
- **Railway Service:** `***`
  - Service name: [FILL IN]
- **Auto-deploy:** [YES/NO]
- **Environment Variables:** [Same as above / Different?]

**Production Environment:**
- **Branch:** `***`
  - Options: `prod`, `production`, `release/*`, `main` (if main is prod)
  - Your branch: [FILL IN or "Not set up yet"]
- **Railway Service:** `***`
  - Service name: [FILL IN or "Not set up yet"]
- **Auto-deploy:** [YES/NO or "Not set up yet"]
- **Environment Variables:** [Different from staging? List differences]

### Recommended Mapping (if not set up)

**Option 1: Separate Services**
```
Branch: main → Railway Service: lynx-staging → LYNX_MODE=staging
Branch: prod → Railway Service: lynx-prod → LYNX_MODE=prod
```

**Option 2: Single Service with Branch-based Config**
```
Branch: main → Railway Service: lynx → LYNX_MODE=staging
Branch: prod → Railway Service: lynx → LYNX_MODE=prod (manual deploy)
```

**Your Preference:** [FILL IN]

---

## Railway Project Details

### Project Information

- **Project Name:** `***`
  - Your value: [FILL IN]
- **GitHub Repository:** `***`
  - Your value: [FILL IN]
  - Format: `owner/repo-name`
- **Railway Project ID:** `***` (optional, for reference)
  - Your value: [FILL IN or leave blank]

### Service Information

- **Service Name:** `***`
  - Your value: [FILL IN]
- **Service ID:** `***` (optional, for reference)
  - Your value: [FILL IN or leave blank]

---

## Validation Checklist

Before sharing, verify:

- [ ] All required variables filled in (or marked as "not set")
- [ ] Secrets redacted (use `***` or `[REDACTED]`)
- [ ] `SUPABASE_KEY` confirmed as service_role key (not anon)
- [ ] `LYNX_RUNNER=daemon` for Railway deployment
- [ ] All secrets marked as "Secret" in Railway UI
- [ ] Build/start commands confirmed in Railway UI
- [ ] Branch mapping documented

---

## Additional Notes

**Any custom configurations?**
[FILL IN - e.g., custom build steps, additional services, etc.]

**Any known issues or concerns?**
[FILL IN - e.g., connection issues, missing dependencies, etc.]

**Questions for review?**
[FILL IN - any specific things you want me to check]

---

## Example Completed Template

Here's what a completed template might look like (with redacted secrets):

```bash
LYNX_MODE=staging
LYNX_RUNNER=daemon
SUPABASE_URL=https://abcdefghijklmnop.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9... [SECRET]
KERNEL_API_URL=https://kernel.nexuscanon.com/api
KERNEL_API_KEY=sk-kernel-xxx [SECRET]
OPENAI_API_KEY=sk-openai-xxx [SECRET]
DAEMON_HEARTBEAT_INTERVAL=60
DAEMON_STATUS_CHECK_INTERVAL=300
```

**Branch Mapping:**
- Staging: `main` → `lynx-staging` service → Auto-deploy: YES
- Production: `prod` → `lynx-prod` service → Auto-deploy: NO (manual)

---

**Status:** [ ] Ready for review  
**Date:** [FILL IN]

---

## After Review

Once reviewed, this template will be updated with:
- ✅ Sanity-check results
- ✅ Recommendations
- ✅ Any missing variables
- ✅ Branch mapping suggestions
- ✅ Security notes

