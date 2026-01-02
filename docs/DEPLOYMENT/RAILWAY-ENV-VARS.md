# Railway Environment Variables Reference

**Version:** 1.0.0  
**Date:** 2026-01-27  
**Purpose:** Complete reference for Railway environment variables

---

## Required Environment Variables

### Core Configuration

| Variable | Value | Description | Secret? |
|----------|-------|-------------|---------|
| `LYNX_MODE` | `staging` | Execution environment | No |
| `LYNX_RUNNER` | `daemon` | Runner mode (oneshot/daemon) | No |

### Supabase Configuration

| Variable | Value | Description | Secret? |
|----------|-------|-------------|---------|
| `SUPABASE_URL` | `https://<project-ref>.supabase.co` | Supabase project URL | No |
| `SUPABASE_KEY` | `<service-role-key>` | **Service role key** (not anon key) | ✅ Yes |

**⚠️ CRITICAL:** Use **service_role** key, not anon key. This bypasses RLS for server-side operations. RLS is still enforced via `app.tenant_id` in code.

### Kernel API Configuration

| Variable | Value | Description | Secret? |
|----------|-------|-------------|---------|
| `KERNEL_API_URL` | `https://your-kernel-api.example.com` | Kernel SSOT API URL | No |
| `KERNEL_API_KEY` | `<kernel-api-key>` | Kernel API authentication key | ✅ Yes |

### LLM Provider Configuration

| Variable | Value | Description | Secret? |
|----------|-------|-------------|---------|
| `OPENAI_API_KEY` | `<openai-api-key>` | OpenAI API key (or Anthropic) | ✅ Yes |

---

## Optional Environment Variables

### Daemon Configuration

| Variable | Default | Description | Secret? |
|----------|---------|-------------|---------|
| `DAEMON_HEARTBEAT_INTERVAL` | `60` | Heartbeat log interval (seconds) | No |
| `DAEMON_STATUS_CHECK_INTERVAL` | `300` | Status check interval (seconds) | No |

### Logging Configuration

| Variable | Default | Description | Secret? |
|----------|---------|-------------|---------|
| `LOG_LEVEL` | `info` | Log level (debug, info, warning, error) | No |

### Maintenance Mode

| Variable | Default | Description | Secret? |
|----------|---------|-------------|---------|
| `LYNX_MAINTENANCE_MODE` | `false` | Enable maintenance mode | No |

---

## Railway Setup Example

### Minimum Configuration (Required)

```bash
LYNX_MODE=staging
LYNX_RUNNER=daemon
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...  # service_role key
KERNEL_API_URL=https://kernel.nexuscanon.com/api
KERNEL_API_KEY=your-kernel-key
OPENAI_API_KEY=sk-...
```

### Recommended Configuration (With Optional)

```bash
LYNX_MODE=staging
LYNX_RUNNER=daemon
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
KERNEL_API_URL=https://kernel.nexuscanon.com/api
KERNEL_API_KEY=your-kernel-key
OPENAI_API_KEY=sk-...
DAEMON_HEARTBEAT_INTERVAL=60
DAEMON_STATUS_CHECK_INTERVAL=300
LOG_LEVEL=info
```

---

## Sanity Check Checklist

Before deploying, verify:

- [ ] `LYNX_MODE` is set to `staging` (or `prod` for production)
- [ ] `LYNX_RUNNER` is set to `daemon` (required for Railway)
- [ ] `SUPABASE_URL` is correct (format: `https://<project-ref>.supabase.co`)
- [ ] `SUPABASE_KEY` is the **service_role** key (not anon key)
- [ ] `KERNEL_API_URL` is correct and reachable
- [ ] `KERNEL_API_KEY` is valid
- [ ] `OPENAI_API_KEY` is valid (or Anthropic key if using Anthropic)
- [ ] All secret variables are marked as "Secret" in Railway
- [ ] Optional variables have sensible defaults or are explicitly set

---

## Expected Startup Logs

With correct environment variables, you should see:

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

💓 [2026-01-27 10:00:00] Heartbeat #1 | Tools: 18 | Sessions: 0
```

---

## Common Issues

### Issue: "SUPABASE_KEY environment variable is required"

**Cause:** `SUPABASE_KEY` not set or empty.

**Solution:** Add `SUPABASE_KEY` to Railway variables (use service_role key).

### Issue: "KERNEL_API_URL environment variable is required"

**Cause:** `KERNEL_API_URL` not set.

**Solution:** Add `KERNEL_API_URL` to Railway variables.

### Issue: Storage Backend shows "MEMORY" instead of "SUPABASE"

**Cause:** `SUPABASE_URL` or `SUPABASE_KEY` not set, or connection failed.

**Solution:** 
1. Verify `SUPABASE_URL` and `SUPABASE_KEY` are set
2. Check Supabase connection (test in Supabase dashboard)
3. Verify service_role key is correct

### Issue: "Failed to load configuration"

**Cause:** Config file not found or invalid.

**Solution:** 
1. Verify `config/config.yaml` exists (or set `LYNX_CONFIG_PATH`)
2. Check config file syntax
3. Verify environment variable substitution works

---

## Production Considerations

For production deployment:

1. **Change `LYNX_MODE` to `prod`**
   - Enables stricter validation
   - Requires explicit approval for high-risk actions

2. **Review secret rotation**
   - Rotate API keys regularly
   - Use Railway's secret management

3. **Enable monitoring**
   - Set up alerts for service health
   - Monitor heartbeat logs
   - Track status check metrics

4. **Backup configuration**
   - Export environment variables
   - Document any custom settings

---

**Status:** ✅ Ready for Railway deployment

