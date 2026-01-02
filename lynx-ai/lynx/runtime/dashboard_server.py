"""
Dashboard Server - Runs alongside daemon

Starts FastAPI dashboard server in background while daemon runs.
"""

import os
from typing import Optional
import uvicorn
from threading import Thread

from lynx.api.dashboard import app


def start_dashboard_server(port: Optional[int] = None):
    """Start dashboard server in a separate thread."""
    if port is None:
        port = int(os.getenv("PORT", "8000"))
    
    def run_server():
        """Run uvicorn server."""
        config = uvicorn.Config(
            app,
            host="0.0.0.0",
            port=port,
            log_level="info",
            access_log=False,  # Reduce log noise
            loop="asyncio",
        )
        server = uvicorn.Server(config)
        server.run()
    
    # Start dashboard in background thread
    dashboard_thread = Thread(target=run_server, daemon=True)
    dashboard_thread.start()
    print(f"🌐 Dashboard server started on port {port}")
    print(f"   Access at: http://localhost:{port}/")
    print(f"   Health check: http://localhost:{port}/health")
    print(f"   API status: http://localhost:{port}/api/status")
    return dashboard_thread

