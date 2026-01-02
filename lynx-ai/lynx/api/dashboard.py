"""
Lynx AI Dashboard - HTTP API for Monitoring

Provides web dashboard and API endpoints for monitoring Lynx AI service.
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from lynx.cli.status import get_lynx_status, get_last_n_runs_summary
from lynx.config import Config
from lynx.__version__ import LYNX_PROTOCOL_VERSION, MCP_TOOLSET_VERSION

app = FastAPI(
    title="Lynx AI Dashboard",
    description="Monitoring dashboard and API for Lynx AI service",
    version=LYNX_PROTOCOL_VERSION,
)

# CORS middleware for dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_class=HTMLResponse)
async def dashboard_home():
    """Main dashboard page."""
    try:
        status = await get_lynx_status()
    except Exception as e:
        # Return error page if status check fails
        status = {
            "status": "error",
            "error_message": str(e),
            "current_mode": "unknown",
            "maintenance_mode": False,
            "storage_backend": "unknown",
            "kernel_api_reachable": False,
            "supabase_reachable": False,
            "draft_count_24h": 0,
            "execution_count_24h": 0,
            "pending_settlement_count": 0,
            "total_mcp_tools_registered": 0,
            "last_runs": [],
        }
    
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Lynx AI Dashboard</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: #0a0a0a;
                color: #e0e0e0;
                padding: 20px;
                line-height: 1.6;
            }}
            .container {{
                max-width: 1200px;
                margin: 0 auto;
            }}
            h1 {{
                color: #4CAF50;
                margin-bottom: 30px;
                font-size: 2.5em;
            }}
            .status-badge {{
                display: inline-block;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 0.9em;
                margin-left: 10px;
            }}
            .status-operational {{
                background: #4CAF50;
                color: white;
            }}
            .status-degraded {{
                background: #ff9800;
                color: white;
            }}
            .status-down {{
                background: #f44336;
                color: white;
            }}
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 30px;
            }}
            .card {{
                background: #1a1a1a;
                border: 1px solid #333;
                border-radius: 8px;
                padding: 20px;
            }}
            .card h2 {{
                color: #4CAF50;
                margin-bottom: 15px;
                font-size: 1.3em;
            }}
            .metric {{
                display: flex;
                justify-content: space-between;
                padding: 10px 0;
                border-bottom: 1px solid #333;
            }}
            .metric:last-child {{
                border-bottom: none;
            }}
            .metric-label {{
                color: #aaa;
            }}
            .metric-value {{
                color: #e0e0e0;
                font-weight: bold;
            }}
            .check {{
                color: #4CAF50;
                margin-right: 8px;
            }}
            .cross {{
                color: #f44336;
                margin-right: 8px;
            }}
            .footer {{
                text-align: center;
                margin-top: 40px;
                color: #666;
                font-size: 0.9em;
            }}
            .refresh-btn {{
                background: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 1em;
                margin-bottom: 20px;
            }}
            .refresh-btn:hover {{
                background: #45a049;
            }}
        </style>
        <script>
            function refreshDashboard() {{
                location.reload();
            }}
            // Auto-refresh every 30 seconds
            setInterval(refreshDashboard, 30000);
        </script>
    </head>
    <body>
        <div class="container">
            <h1>
                Lynx AI Dashboard
                <span class="status-badge status-{status.get('status', 'error')}">
                    {status.get('status', 'ERROR').upper()}
                </span>
            </h1>
            <button class="refresh-btn" onclick="refreshDashboard()">🔄 Refresh</button>
            {f'<div class="error-banner">⚠️ Error: {status.get("error_message", "Unknown error")}</div>' if status.get('status') == 'error' else ''}
            
            <div class="grid">
                <div class="card">
                    <h2>System Status</h2>
                    <div class="metric">
                        <span class="metric-label">Mode</span>
                        <span class="metric-value">{status.get('current_mode', 'unknown').upper()}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Maintenance Mode</span>
                        <span class="metric-value">{'Yes' if status.get('maintenance_mode', False) else 'No'}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Storage Backend</span>
                        <span class="metric-value">{status.get('storage_backend', 'unknown').upper()}</span>
                    </div>
                </div>
                
                <div class="card">
                    <h2>Connectivity</h2>
                    <div class="metric">
                        <span class="metric-label">Kernel API</span>
                        <span class="metric-value">
                            {'<span class="check">✅</span> Reachable' if status.get('kernel_api_reachable', False) else '<span class="cross">❌</span> Unreachable'}
                        </span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Supabase</span>
                        <span class="metric-value">
                            {'<span class="check">✅</span> Reachable' if status.get('supabase_reachable', False) else '<span class="cross">❌</span> Unreachable'}
                        </span>
                    </div>
                </div>
                
                <div class="card">
                    <h2>Versions</h2>
                    <div class="metric">
                        <span class="metric-label">Protocol Version</span>
                        <span class="metric-value">{status.get('lynx_protocol_version', 'unknown')}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Toolset Version</span>
                        <span class="metric-value">{status.get('mcp_toolset_version', 'unknown')}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Tools Registered</span>
                        <span class="metric-value">{status.get('total_mcp_tools_registered', 0)}</span>
                    </div>
                </div>
                
                <div class="card">
                    <h2>Activity (24h)</h2>
                    <div class="metric">
                        <span class="metric-label">Drafts</span>
                        <span class="metric-value">{status.get('draft_count_24h', 0)}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Executions</span>
                        <span class="metric-value">{status.get('execution_count_24h', 0)}</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Pending Settlements</span>
                        <span class="metric-value">{status.get('pending_settlement_count', 0)}</span>
                    </div>
                </div>
            </div>
            
            <div class="card">
                <h2>Recent Runs (Last 5)</h2>
                {"<ul style='list-style: none; padding: 0;'>" + "".join([
                    f"<li style='padding: 10px 0; border-bottom: 1px solid #333;'>"
                    f"<strong>{run.get('tool_id', 'unknown')}</strong> - {run.get('status', 'unknown').upper()} "
                    f"<span style='color: #666;'>({run.get('created_at', 'unknown')})</span>"
                    f"</li>"
                    for run in status.get('last_5_runs_summary', [])
                ]) + "</ul>" if status.get('last_5_runs_summary') else "<p style='color: #666;'>No recent runs</p>"}
            </div>
            
            <div class="footer">
                <p>Lynx AI Dashboard | Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>Auto-refreshes every 30 seconds</p>
            </div>
        </div>
    </body>
    </html>
    """
    return html


@app.get("/health")
async def health_check():
    """Health check endpoint for Railway/monitoring."""
    try:
        status = await get_lynx_status()
        return {
            "status": status.get('status', 'degraded'),
            "service": "lynx-ai",
            "version": LYNX_PROTOCOL_VERSION,
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        # Return degraded status if status check fails
        return {
            "status": "degraded",
            "service": "lynx-ai",
            "version": LYNX_PROTOCOL_VERSION,
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
        }


@app.get("/api/status")
async def api_status():
    """JSON API endpoint for status."""
    try:
        status = await get_lynx_status()
        return status
    except Exception as e:
        # Return error status if check fails
        return {
            "status": "error",
            "error": str(e),
            "service": "lynx-ai",
            "version": LYNX_PROTOCOL_VERSION,
            "timestamp": datetime.now().isoformat(),
        }


@app.get("/api/metrics")
async def api_metrics():
    """Metrics endpoint (for Prometheus integration in future)."""
    try:
        status = await get_lynx_status()
        return {
            "drafts_24h": status.get('draft_count_24h', 0),
            "executions_24h": status.get('execution_count_24h', 0),
            "pending_settlements": status.get('pending_settlement_count', 0),
            "tools_registered": status.get('total_mcp_tools_registered', 0),
            "kernel_reachable": 1 if status.get('kernel_api_reachable', False) else 0,
            "supabase_reachable": 1 if status.get('supabase_reachable', False) else 0,
        }
    except Exception as e:
        # Return zero metrics on error
        return {
            "drafts_24h": 0,
            "executions_24h": 0,
            "pending_settlements": 0,
            "tools_registered": 0,
            "kernel_reachable": 0,
            "supabase_reachable": 0,
            "error": str(e),
        }


if __name__ == "__main__":
    import os
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=port)

