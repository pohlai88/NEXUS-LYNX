"""
Lynx AI Dashboard — Neo-Analog Ops Console (v3.0 - Layout Fixes)
Fixes the "squished" KPI cards and improves grid responsiveness.
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse, Response
from fastapi.staticfiles import StaticFiles

from lynx.cli.status import get_lynx_status
from lynx.__version__ import LYNX_PROTOCOL_VERSION, MCP_TOOLSET_VERSION
from lynx.api.dashboard_models import DashboardViewModel, DeveloperCockpitViewModel, ServiceStatus

app = FastAPI(
    title="Lynx AI Dashboard",
    description="Enterprise-grade monitoring for Lynx AI",
    version=LYNX_PROTOCOL_VERSION,
)

# ---- 1. Static Files & CSS Setup ----
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- 2. Neo-Analog Design Tokens (FIXED GRID) ----
NEO_INLINE_CSS = """
<style>
    :root {
        /* Base Palette (Zinc-950/900) */
        --color-void: #09090b;
        --color-paper: #121214;
        --color-paper-2: #18181b;
        --color-paper-hover: #27272a;
        
        /* Text (Zinc-50/400) */
        --color-lux: #f4f4f5;
        --color-lux-dim: #a1a1aa;
        --color-clay: #71717a;
        --color-gold: #eab308;

        /* Strokes */
        --color-stroke: #27272a;
        --color-stroke-strong: #3f3f46;

        /* Semantic Status */
        --color-success: #10b981;
        --color-warning: #f59e0b;
        --color-error: #f43f5e;
        --color-info: #3b82f6;

        /* Typography */
        --font-sans: "Inter", system-ui, sans-serif;
        --font-serif: "Playfair Display", Georgia, serif;
        --font-mono: "JetBrains Mono", monospace;

        /* Spacing & Radius */
        --radius-card: 12px;
        --radius-panel: 16px;
        --radius-pill: 9999px;
    }

    /* Reset */
    body {
        background-color: var(--color-void);
        color: var(--color-lux);
        font-family: var(--font-sans);
        margin: 0;
        -webkit-font-smoothing: antialiased;
        line-height: 1.5;
    }

    /* --- LAYOUT UTILS (FIXED) --- */
    .na-shell { 
        max-width: 1400px; 
        margin: 0 auto; 
        padding: 0 32px 64px 32px; 
    }
    
    /* GRID FIX: distinct separation of concerns. 
       'auto-fit' prevents the "squished columns" effect seen in your screenshot.
    */
    .na-grid-kpis { 
        display: grid; 
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); 
        gap: 24px; 
    }

    .na-grid-split { 
        display: grid; 
        grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); 
        gap: 24px; 
    }
    
    /* Cards */
    .na-card {
        background: var(--color-paper);
        border: 1px solid var(--color-stroke);
        border-radius: var(--radius-card);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
        overflow: hidden; /* Contains children */
    }
    .na-card-p6 { padding: 24px; }
    
    /* Typography */
    .na-h3 { font-size: 20px; font-weight: 600; color: var(--color-lux); margin: 0; letter-spacing: -0.01em; }
    
    .na-data-large {
        font-family: var(--font-serif);
        font-size: 42px; /* Slightly larger for impact */
        font-weight: 500;
        color: var(--color-lux);
        letter-spacing: -0.02em;
        line-height: 1.0;
        margin: 12px 0;
    }
    .na-data {
        font-family: var(--font-mono);
        font-size: 13px;
        color: var(--color-lux-dim);
    }
    .na-metadata {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
        color: var(--color-clay);
    }
    .na-desc {
        font-size: 13px;
        color: var(--color-clay);
        line-height: 1.4;
    }

    /* Badges */
    .na-badge {
        display: inline-flex;
        align-items: center;
        padding: 4px 10px;
        border-radius: var(--radius-pill);
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border: 1px solid transparent;
        white-space: nowrap;
    }
    .badge-ok { background: rgba(16, 185, 129, 0.1); color: var(--color-success); border-color: rgba(16, 185, 129, 0.2); }
    .badge-pending { background: rgba(245, 158, 11, 0.1); color: var(--color-warning); border-color: rgba(245, 158, 11, 0.2); }
    .badge-error { background: rgba(244, 63, 94, 0.1); color: var(--color-error); border-color: rgba(244, 63, 94, 0.2); }
    .badge-void { background: var(--color-paper-2); color: var(--color-clay); border-color: var(--color-stroke); }

    /* Command Bar */
    .na-command-bar {
        position: sticky;
        top: 0;
        z-index: 50;
        background: rgba(9, 9, 11, 0.85);
        backdrop-filter: blur(16px);
        border-bottom: 1px solid var(--color-stroke);
        margin-bottom: 40px;
    }
    .na-bar-inner {
        max-width: 1400px;
        margin: 0 auto;
        padding: 16px 32px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Utilities */
    .flex-between { display: flex; justify-content: space-between; align-items: center; }
    .flex-gap { display: flex; gap: 16px; align-items: center; }
    .mb-6 { margin-bottom: 24px; }
    .mt-4 { margin-top: 16px; }
    
    .spin { animation: spin 1s linear infinite; }
    @keyframes spin { 100% { transform: rotate(360deg); } }
    
    /* Link styling reset */
    a { text-decoration: none; color: inherit; }
</style>
"""

# ---- 3. Helpers ----

def _safe(s: Any) -> str:
    if s is None: return ""
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def render_status_badge(status: ServiceStatus, label: str) -> str:
    style_map = {
        ServiceStatus.OK: "badge-ok",
        ServiceStatus.PENDING: "badge-pending",
        ServiceStatus.BAD: "badge-error",
        ServiceStatus.ERROR: "badge-error",
        ServiceStatus.INFO: "badge-void",
    }
    css_class = style_map.get(status, "badge-void")
    return f'<span class="na-badge {css_class}">{_safe(label)}</span>'

def render_shell(vm: DashboardViewModel, cockpit: DeveloperCockpitViewModel) -> str:
    status_enum = vm.get_status_enum()
    
    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Lynx AI | Ops Console</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500&family=Playfair+Display:wght@500;600&display=swap" rel="stylesheet">
    {NEO_INLINE_CSS}
    <script>
        async function refreshFragment(id) {{
            const el = document.getElementById(`fragment-${{id}}`);
            if (!el) return;
            el.style.opacity = '0.5';
            try {{
                const res = await fetch(`/dashboard/_${{id}}`);
                const html = await res.text();
                el.innerHTML = html;
            }} catch (e) {{ console.error(e); }}
            el.style.opacity = '1';
        }}
        
        async function refreshAll() {{ 
            const icon = document.getElementById('refresh-icon');
            if(icon) icon.classList.add('spin');
            
            await Promise.all(['kpis', 'services', 'recent', 'cockpit'].map(refreshFragment));
            
            const timeEl = document.getElementById('last-updated');
            if(timeEl) timeEl.innerText = new Date().toLocaleTimeString();
            
            if(icon) icon.classList.remove('spin');
        }}
        
        setInterval(refreshAll, 30000);
    </script>
</head>
<body>
    <header class="na-command-bar">
        <div class="na-bar-inner">
            <div class="flex-gap">
                <div style="width: 12px; height: 12px; background: var(--color-gold); border-radius: 50%; box-shadow: 0 0 12px rgba(234, 179, 8, 0.5);"></div>
                <div>
                    <h1 class="na-h3" style="font-family: var(--font-serif);">Lynx Ops Console</h1>
                </div>
            </div>
            
            <div class="flex-gap">
                <div style="text-align: right; display: none; @media(min-width: 600px){{display:block;}}">
                    <div class="na-metadata" style="color: var(--color-lux);">PROTOCOL v{vm.lynx_protocol_version}</div>
                    <div class="na-metadata">UPDATED <span id="last-updated">{datetime.now().strftime('%H:%M:%S')}</span></div>
                </div>
                <button onclick="refreshAll()" class="na-card" style="padding: 8px 12px; cursor: pointer; color: var(--color-lux); background: transparent;">
                    <span id="refresh-icon" style="display: inline-block;">↻</span>
                </button>
                {render_status_badge(status_enum, "SYSTEM " + vm.status.upper())}
            </div>
        </div>
    </header>

    <main class="na-shell">
        <div id="fragment-cockpit" class="mb-6">
            {render_fragment_cockpit(cockpit)}
        </div>

        <div id="fragment-kpis" class="mb-6">
            {render_fragment_kpis(vm)}
        </div>

        <div class="na-grid-split">
            <div id="fragment-services">
                {render_fragment_services(vm)}
            </div>
            <div id="fragment-recent">
                {render_fragment_recent(vm)}
            </div>
        </div>
    </main>
</body>
</html>
"""

def render_fragment_kpis(vm: DashboardViewModel) -> str:
    """Renders KPIs with correct width constraints to prevent text squishing."""
    data = vm.to_dict()
    
    def kpi_card(label, value, sublabel, desc, status_enum=ServiceStatus.INFO):
        # Determine badge style
        badge = render_status_badge(status_enum, sublabel)
        
        return f"""
        <div class="na-card na-card-p6" style="display: flex; flex-direction: column; justify-content: flex-start; min-height: 200px;">
            <div class="flex-between">
                <div class="na-metadata">{label}</div>
                {badge}
            </div>
            
            <div class="na-data-large">{value}</div>
            
            <div class="na-desc" style="margin-top: auto;">
                {desc}
            </div>
        </div>
        """

    # Helper logic for status
    exec_count = data.get("execution_count_24h", 0)
    draft_count = data.get("draft_count_24h", 0)
    tools_count = data.get("total_mcp_tools_registered", 0)
    pending_count = data.get("pending_settlement_count", 0)

    return f"""
    <div class="na-grid-kpis">
        {kpi_card(
            "Executions (24h)", 
            exec_count, 
            "Active" if exec_count > 0 else "Quiet",
            "Signal of tool usage and end-to-end flow health.",
            ServiceStatus.OK if exec_count > 0 else ServiceStatus.INFO
        )}
        {kpi_card(
            "Drafts (24h)", 
            draft_count, 
            "Pending" if draft_count > 0 else "Clear",
            "Uncommitted work waiting for finalization or review.",
            ServiceStatus.PENDING if draft_count > 0 else ServiceStatus.INFO
        )}
        {kpi_card(
            "Tools Registered", 
            tools_count, 
            "Online" if tools_count > 0 else "Offline",
            "Total MCP tools currently available to the agent.",
            ServiceStatus.OK if tools_count > 0 else ServiceStatus.BAD
        )}
        {kpi_card(
            "Settlements", 
            pending_count, 
            "Backlog" if pending_count > 0 else "Settled",
            "Ops backlog items that may block reporting accuracy.",
            ServiceStatus.PENDING if pending_count > 0 else ServiceStatus.OK
        )}
    </div>
    """

def render_fragment_cockpit(cockpit: DeveloperCockpitViewModel) -> str:
    data = cockpit.to_dict()
    blockers = data.get("top_blockers", [])
    
    blocker_html = ""
    if blockers:
        blocker_html = f'''
        <div style="margin-top: 24px; padding-top: 16px; border-top: 1px solid var(--color-stroke);">
            <div class="na-metadata" style="color: var(--color-error); margin-bottom: 8px;">⚠️ BLOCKERS</div>
            {"".join([f'<div class="na-data" style="margin-bottom: 4px;">• {_safe(b)}</div>' for b in blockers])}
        </div>
        '''
    
    return f"""
    <div class="na-card na-card-p6">
        <div class="flex-between mb-6">
            <div>
                <h3 class="na-h3">Developer Cockpit</h3>
                <div class="na-desc mt-4">Where you stopped — and what to do next.</div>
            </div>
            <span class="na-badge badge-void">DEV MODE</span>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 32px;">
            <div>
                <div class="na-metadata mb-6">CURRENT STAGE</div>
                <div style="font-size: 24px; color: var(--color-gold); font-weight: 600; font-family: var(--font-sans);">
                    {_safe(data.get('current_stage', 'Unknown'))}
                </div>
                <div class="na-desc mt-4">Keep this as the "chapter title" of your dev diary.</div>
            </div>

            <div>
                <div class="na-metadata mb-6">NEXT RECOMMENDED ACTION</div>
                <div class="na-data" style="color: var(--color-lux); font-size: 14px; line-height: 1.6;">
                    {_safe(data.get('next_recommended_action') or 'System Idle')}
                </div>
            </div>
        </div>

        {blocker_html}
    </div>
    """

def render_fragment_services(vm: DashboardViewModel) -> str:
    data = vm.to_dict()
    
    def row(name, is_ok, details):
        status = ServiceStatus.OK if is_ok else ServiceStatus.BAD
        status_text = "Connected" if is_ok else "Disconnected"
        
        return f"""
        <div class="flex-between" style="padding: 16px 0; border-bottom: 1px solid var(--color-stroke-strong);">
            <div>
                <div style="font-weight: 600; font-size: 14px; color: var(--color-lux); margin-bottom: 4px;">{name}</div>
                <div class="na-data" style="opacity: 0.7;">{details}</div>
            </div>
            {render_status_badge(status, status_text)}
        </div>
        """

    return f"""
    <div class="na-card na-card-p6">
        <h3 class="na-h3 mb-6">System Health</h3>
        <div style="margin-top: 16px;">
            {row("Kernel API", data.get("kernel_api_reachable"), "Core SSOT/Registry Endpoint")}
            {row("Supabase", data.get("supabase_reachable"), f"Storage Backend: {_safe(data.get('storage_backend'))}")}
            {row("Dashboard", True, "Internal Monitoring (Port 8000)")}
        </div>
    </div>
    """

def render_fragment_recent(vm: DashboardViewModel) -> str:
    data = vm.to_dict()
    runs = data.get("last_5_runs_summary", [])
    
    content = ""
    if not runs:
        content = '<div class="na-desc" style="text-align: center; padding: 48px 0;">No recent activity recorded.<br>Run a tool to populate this list.</div>'
    else:
        for run in runs:
            s_str = run.get("status", "pending").lower()
            s_enum = ServiceStatus.OK if s_str in ["success", "ok", "completed"] else ServiceStatus.PENDING
            
            content += f"""
            <div class="flex-between" style="padding: 16px 0; border-bottom: 1px solid var(--color-stroke-strong);">
                <div>
                    <div style="font-weight: 500; font-size: 14px; color: var(--color-lux); margin-bottom: 4px;">{_safe(run.get('tool_id', 'Unknown Tool'))}</div>
                    <div class="na-data" style="font-size: 11px; opacity: 0.7;">{_safe(run.get('created_at', 'Just now'))}</div>
                </div>
                {render_status_badge(s_enum, s_str.upper())}
            </div>
            """

    return f"""
    <div class="na-card na-card-p6">
        <div class="flex-between mb-6">
            <h3 class="na-h3">Activity Log</h3>
            <span class="na-metadata">LAST 5 RUNS</span>
        </div>
        <div style="margin-top: 16px;">
            {content}
        </div>
    </div>
    """

# ---- 4. Endpoints ----

@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_home():
    try:
        raw_status = await get_lynx_status()
        vm = DashboardViewModel(raw_status)
    except Exception as e:
        vm = DashboardViewModel({"status": "error", "error": str(e)})
    
    cockpit = DeveloperCockpitViewModel() 
    return render_shell(vm, cockpit)

@app.get("/dashboard/_kpis", response_class=HTMLResponse)
async def fragment_kpis():
    try:
        raw = await get_lynx_status()
        return render_fragment_kpis(DashboardViewModel(raw))
    except Exception as e:
        return f'<div class="na-data" style="color:var(--color-error)">Error: {str(e)}</div>'

@app.get("/dashboard/_services", response_class=HTMLResponse)
async def fragment_services():
    try:
        raw = await get_lynx_status()
        return render_fragment_services(DashboardViewModel(raw))
    except:
        return '<div class="na-data">Service check failed</div>'

@app.get("/dashboard/_recent", response_class=HTMLResponse)
async def fragment_recent():
    try:
        raw = await get_lynx_status()
        return render_fragment_recent(DashboardViewModel(raw))
    except:
        return '<div class="na-data">Activity log unavailable</div>'

@app.get("/dashboard/_cockpit", response_class=HTMLResponse)
async def fragment_cockpit():
    return render_fragment_cockpit(DeveloperCockpitViewModel())

@app.get("/health")
async def health_check():
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.get("/api/status")
async def api_status():
    raw = await get_lynx_status()
    return DashboardViewModel(raw).to_dict()

@app.get("/static/aibos-design-system.css")
async def serve_css():
    css_path = Path(__file__).parent / "static" / "aibos-design-system.css"
    if css_path.exists():
        return FileResponse(css_path, media_type="text/css")
    return Response("/* Not Found */", media_type="text/css", status_code=404)

# ---- 5. Include API Routes ----
from lynx.api.chat_routes import router as chat_router
from lynx.api.draft_routes import router as draft_router
from lynx.api.audit_routes import router as audit_router

app.include_router(chat_router)
app.include_router(draft_router)
app.include_router(audit_router)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)