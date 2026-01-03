# Lynx AI Dashboard Setup

**Date:** 2026-01-27  
**Status:** ✅ DASHBOARD IMPLEMENTED  
**Purpose:** Web dashboard for monitoring Lynx AI service

---

## ✅ Dashboard Features

### Web Interface
- **URL:** `http://<railway-domain>/` or `http://localhost:8000/`
- **Auto-refresh:** Every 30 seconds
- **Dark theme:** Optimized for monitoring

### Endpoints

1. **Dashboard Home** (`/`)
   - Visual status dashboard
   - System metrics
   - Recent activity
   - Real-time updates

2. **Health Check** (`/health`)
   - JSON health status
   - For Railway/monitoring tools
   - Returns: `{"status": "operational", "service": "lynx-ai", ...}`

3. **API Status** (`/api/status`)
   - Complete system status JSON
   - All metrics and connectivity info

4. **Metrics** (`/api/metrics`)
   - Metrics for Prometheus integration (future)
   - Activity counts, connectivity status

---

## 🚀 How It Works

### Architecture

The dashboard runs **alongside the daemon** in the same process:
- Daemon handles MCP server operations
- Dashboard provides HTTP monitoring interface
- Both run in the same container
- Dashboard uses Railway's `PORT` environment variable

### Startup Sequence

1. Daemon initializes (MCP server, tools, etc.)
2. Dashboard server starts in background thread
3. Both run concurrently
4. Dashboard accessible via Railway public domain

---

## 📋 Configuration

### Environment Variables

```bash
# Enable/disable dashboard (default: true)
DASHBOARD_ENABLED=true

# Port for dashboard (Railway sets PORT automatically)
PORT=8000
```

### Railway Setup

Railway automatically:
- Exposes the service on a public domain
- Sets `PORT` environment variable
- Routes HTTP traffic to the dashboard

**No additional configuration needed!**

---

## 🔍 Accessing the Dashboard

### After Deployment

1. **Get Railway Public Domain:**
   ```powershell
   railway domain
   ```

2. **Or check Railway Dashboard:**
   - Go to Railway project
   - Service → Settings → Domains
   - Copy the public domain URL

3. **Access Dashboard:**
   ```
   https://<your-railway-domain>.railway.app/
   ```

### Local Development

```bash
# Start daemon with dashboard
cd lynx-ai
LYNX_RUNNER=daemon PORT=8000 uv run python -m lynx.runtime.daemon

# Access at:
# http://localhost:8000/
```

---

## 📊 Dashboard Features

### System Status Card
- Current mode (staging/prod)
- Maintenance mode status
- Storage backend type

### Connectivity Card
- Kernel API reachability
- Supabase reachability

### Versions Card
- Protocol version
- Toolset version
- Tools registered count

### Activity Card (24h)
- Drafts created
- Executions completed
- Pending settlements

### Recent Runs
- Last 5 tool executions
- Status and timestamps
- Tool IDs and tenant info

---

## 🔧 Troubleshooting

### Dashboard Not Accessible

**Check:**
1. `DASHBOARD_ENABLED=true` is set (or not set, defaults to true)
2. `PORT` environment variable is set (Railway sets this automatically)
3. Service is running (check Railway logs)

**Solution:**
```powershell
# Check Railway logs
railway logs --lines 50

# Look for:
# "🌐 Dashboard server started on port 8000"
```

### Dashboard Shows Errors

**Check:**
1. Supabase connection (dashboard needs it for metrics)
2. Kernel API connection (for status checks)
3. Service initialization completed

**Solution:**
- Check `/health` endpoint first (simpler, doesn't query Supabase)
- Check `/api/status` for detailed errors
- Review Railway logs for initialization errors

---

## 📝 API Examples

### Health Check
```bash
curl https://<railway-domain>/health
```

**Response:**
```json
{
  "status": "operational",
  "service": "lynx-ai",
  "version": "0.1.0",
  "timestamp": "2026-01-27T10:00:00"
}
```

### Status API
```bash
curl https://<railway-domain>/api/status
```

**Response:**
```json
{
  "service_name": "Lynx AI",
  "status": "operational",
  "lynx_protocol_version": "0.1.0",
  "mcp_toolset_version": "0.1.0",
  "kernel_api_reachable": true,
  "supabase_reachable": true,
  "storage_backend": "supabase",
  "total_mcp_tools_registered": 18,
  "draft_count_24h": 0,
  "execution_count_24h": 0,
  "pending_settlement_count": 0,
  ...
}
```

---

## ✅ Deployment Checklist

- [x] FastAPI and uvicorn added to dependencies
- [x] Dashboard module created (`lynx/api/dashboard.py`)
- [x] Dashboard server integration (`lynx/runtime/dashboard_server.py`)
- [x] Daemon updated to start dashboard automatically
- [x] Railway configuration supports HTTP (uses PORT env var)
- [ ] Dashboard accessible after deployment
- [ ] Health endpoint working
- [ ] Status API returning data

---

## 🎯 Next Steps

1. **Deploy to Railway:**
   ```powershell
   railway up
   ```

2. **Get Public Domain:**
   ```powershell
   railway domain
   ```

3. **Access Dashboard:**
   - Visit the Railway public domain URL
   - Check `/health` endpoint
   - View full dashboard at `/`

---

**Status:** ✅ **DASHBOARD IMPLEMENTED**  
**Ready for:** Railway deployment  
**Last Updated:** 2026-01-27

