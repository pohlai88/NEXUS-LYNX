# Dashboard Pending Items

**Date:** 2026-01-27  
**Status:** ⚠️ PENDING IMPLEMENTATION  
**Component:** `lynx-ai/lynx/api/dashboard_models.py`

---

## 📋 Pending Items

### 1. DeveloperCockpitViewModel - Git/Config Integration

**Location:** `lynx-ai/lynx/api/dashboard_models.py:105`

**Current State:**
```python
def __init__(self):
    """Initialize developer cockpit data."""
    # TODO: Get from git/config/deployment status
    self.current_stage: str = "STAGING"  # STAGING / PROD
    self.last_successful_task: Optional[str] = None  # commit/tag/build ID
    self.next_recommended_action: Optional[str] = None
    self.top_blockers: List[str] = []
    self.deployment_url: Optional[str] = None
```

**Required Implementation:**

1. **Current Stage Detection**
   - Read from environment variable `LYNX_MODE` or `RAILWAY_ENVIRONMENT`
   - Default to "STAGING" if not set
   - Validate against known stages: `["STAGING", "PROD"]`

2. **Last Successful Task**
   - Extract from git: `git rev-parse --short HEAD` (commit hash)
   - Or from Railway: `RAILWAY_DEPLOYMENT_ID`
   - Or from build metadata: `RAILWAY_BUILD_ID`
   - Format: `{commit_hash}@{branch}` or `{deployment_id}`

3. **Next Recommended Action**
   - Logic to determine next action based on:
     - Current stage
     - Pending settlements
     - Error state
     - Test failures
   - Examples:
     - "Deploy to production" (if staging is healthy)
     - "Fix pending settlements" (if backlog exists)
     - "Review test failures" (if tests failing)

4. **Top Blockers**
   - Query from:
     - Error logs (last 24h)
     - Failed test runs
     - Pending settlements count
     - Kernel API connectivity issues
   - Format: `["Error: Kernel API unreachable", "5 pending settlements"]`

5. **Deployment URL**
   - Read from `RAILWAY_PUBLIC_DOMAIN` or `RAILWAY_STATIC_URL`
   - Or construct from Railway metadata
   - Format: `https://{domain}/`

---

## 🔧 Implementation Plan

### Phase 1: Environment Detection
- [ ] Read `LYNX_MODE` or `RAILWAY_ENVIRONMENT`
- [ ] Validate stage value
- [ ] Set `current_stage` dynamically

### Phase 2: Git Integration
- [ ] Add `gitpython` dependency (optional, or use subprocess)
- [ ] Get current commit hash
- [ ] Get current branch name
- [ ] Set `last_successful_task` as `{hash}@{branch}`

### Phase 3: Railway Metadata
- [ ] Read Railway environment variables
- [ ] Extract deployment/build IDs
- [ ] Set `deployment_url` from Railway domain

### Phase 4: Blocker Detection
- [ ] Query error logs (last 24h)
- [ ] Check pending settlements count
- [ ] Check Kernel API connectivity
- [ ] Format blockers list

### Phase 5: Next Action Logic
- [ ] Implement decision tree:
  - If staging healthy → "Deploy to production"
  - If errors exist → "Fix errors"
  - If settlements pending → "Process settlements"
  - If tests failing → "Fix tests"
  - Default → "System idle"

---

## 📝 Notes

- **Current Implementation:** Hardcoded values for development
- **Priority:** Medium (not blocking deployment)
- **Dependencies:** 
  - Git (for commit hash)
  - Railway metadata (for deployment info)
  - Error log access (for blockers)

---

## ✅ Acceptance Criteria

- [ ] `current_stage` reflects actual deployment environment
- [ ] `last_successful_task` shows real commit/deployment ID
- [ ] `next_recommended_action` provides actionable guidance
- [ ] `top_blockers` shows real issues (if any)
- [ ] `deployment_url` points to actual deployment
- [ ] All fields update dynamically (not hardcoded)

---

**Status:** ⚠️ **PENDING** - Ready for implementation

