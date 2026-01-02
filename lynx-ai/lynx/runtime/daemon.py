"""
Lynx AI Daemon Runtime

Long-running process for Railway/staging deployment.
Handles graceful shutdown, heartbeat logging, and periodic status checks.
"""

import asyncio
import signal
import sys
from datetime import datetime
from typing import Optional

from lynx.config import Config
from lynx.core.runtime.app import load_config
from lynx.core.session import SessionManager
from lynx.core.registry import MCPToolRegistry
from lynx.core.audit import AuditLogger
from lynx.mcp.server import initialize_mcp_server


class LynxDaemon:
    """Long-running Lynx daemon for staging/production."""
    
    def __init__(self):
        """Initialize daemon."""
        self.running = False
        self.shutdown_event = asyncio.Event()
        self.session_manager: Optional[SessionManager] = None
        self.tool_registry: Optional[MCPToolRegistry] = None
        self.audit_logger: Optional[AuditLogger] = None
        self.config: Optional[dict] = None
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        signal.signal(signal.SIGINT, self._handle_shutdown)
    
    def _handle_shutdown(self, signum, frame):
        """Handle shutdown signals (SIGTERM/SIGINT)."""
        print(f"\n🛑 Received signal {signum}, initiating graceful shutdown...")
        self.running = False
        self.shutdown_event.set()
    
    async def initialize(self) -> bool:
        """Initialize Lynx components."""
        print("🚀 Starting Lynx AI Daemon...")
        print("=" * 60)
        
        # Load configuration
        try:
            self.config = load_config()
            print("✅ Configuration loaded")
        except Exception as e:
            print(f"❌ Failed to load configuration: {e}")
            print("\n💡 Please:")
            print("   1. Copy config/config.yaml.example to config/config.yaml")
            print("   2. Set required environment variables")
            return False
        
        # Initialize components
        try:
            self.session_manager = SessionManager()
            self.tool_registry = MCPToolRegistry()
            print("✅ Core components initialized")
        except Exception as e:
            print(f"❌ Failed to initialize core components: {e}")
            return False
        
        # Initialize audit logger
        try:
            self.audit_logger = AuditLogger(
                supabase_url=self.config["supabase"]["url"],
                supabase_key=self.config["supabase"]["key"],
            )
            print("✅ Audit logger initialized")
        except Exception as e:
            print(f"⚠️  Audit logger initialization failed: {e}")
            print("   Continuing without audit logging (not recommended for production)")
            self.audit_logger = None
        
        # Initialize MCP server and register tools
        try:
            initialize_mcp_server(self.tool_registry)
            print("✅ MCP server initialized")
        except Exception as e:
            print(f"⚠️  MCP server initialization failed: {e}")
            print("   Some tools may not be available")
            return False
        
        # Get storage backend type
        from lynx.storage.draft_storage import get_draft_storage
        storage = get_draft_storage()
        storage_backend = "supabase" if hasattr(storage, 'client') else "memory"
        
        # Get version info
        from lynx.__version__ import LYNX_PROTOCOL_VERSION, MCP_TOOLSET_VERSION
        
        # Print startup banner
        print("\n" + "=" * 60)
        print("📋 Lynx AI Startup Banner")
        print("=" * 60)
        print(f"   Environment:        {Config.LYNX_MODE.value.upper()}")
        print(f"   Runner Mode:         {Config.LYNX_RUNNER.value.upper()}")
        print(f"   Storage Backend:     {storage_backend.upper()}")
        print(f"   Protocol Version:   {LYNX_PROTOCOL_VERSION}")
        print(f"   Toolset Version:    {MCP_TOOLSET_VERSION}")
        print("=" * 60)
        print("\n📋 Lynx AI Status:")
        print(f"   ✅ Tools registered: {len(self.tool_registry.list_all())}")
        print(f"   ✅ Domain MCPs: {len(self.tool_registry.list_by_layer('domain'))}")
        print(f"   ✅ Cluster MCPs: {len(self.tool_registry.list_by_layer('cluster'))}")
        print(f"   ✅ Cell MCPs: {len(self.tool_registry.list_by_layer('cell'))}")
        print(f"   ✅ Active sessions: {len(self.session_manager.sessions)}")
        print("=" * 60)
        print("\n💚 Daemon running. Waiting for MCP client connections...")
        print(f"   Heartbeat interval: {Config.DAEMON_HEARTBEAT_INTERVAL}s")
        print(f"   Status check interval: {Config.DAEMON_STATUS_CHECK_INTERVAL}s")
        print("   Press Ctrl+C or send SIGTERM to shutdown gracefully\n")
        
        return True
    
    async def run_heartbeat(self):
        """Run heartbeat loop (logs every N seconds)."""
        heartbeat_count = 0
        
        while self.running:
            try:
                await asyncio.sleep(Config.DAEMON_HEARTBEAT_INTERVAL)
                
                if not self.running:
                    break
                
                heartbeat_count += 1
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Simple heartbeat log
                print(f"💓 [{timestamp}] Heartbeat #{heartbeat_count} | "
                      f"Tools: {len(self.tool_registry.list_all())} | "
                      f"Sessions: {len(self.session_manager.sessions)}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"⚠️  Heartbeat error: {e}")
    
    async def run_status_check(self):
        """Run periodic status checks (every N seconds)."""
        from lynx.cli.status import get_lynx_status  # type: ignore
        
        status_check_count = 0
        
        while self.running:
            try:
                await asyncio.sleep(Config.DAEMON_STATUS_CHECK_INTERVAL)
                
                if not self.running:
                    break
                
                status_check_count += 1
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Run status check
                try:
                    status = await get_lynx_status()
                    print(f"📊 [{timestamp}] Status Check #{status_check_count}:")
                    print(f"   Status: {status['status'].upper()}")
                    print(f"   Storage: {status['storage_backend'].upper()}")
                    print(f"   Drafts (24h): {status['draft_count_24h']}")
                    print(f"   Executions (24h): {status['execution_count_24h']}")
                    print(f"   Pending Settlements: {status['pending_settlement_count']}")
                except Exception as e:
                    print(f"⚠️  Status check error: {e}")
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"⚠️  Status check loop error: {e}")
    
    async def run(self):
        """Run daemon main loop."""
        # Initialize
        if not await self.initialize():
            print("❌ Initialization failed, exiting")
            sys.exit(1)
        
        self.running = True
        
        # Start background tasks
        heartbeat_task = asyncio.create_task(self.run_heartbeat())
        status_task = asyncio.create_task(self.run_status_check())
        
        try:
            # Wait for shutdown signal
            await self.shutdown_event.wait()
            
            print("\n🛑 Shutdown signal received, cleaning up...")
            
            # Cancel background tasks
            heartbeat_task.cancel()
            status_task.cancel()
            
            # Wait for tasks to finish (with timeout)
            try:
                await asyncio.wait_for(
                    asyncio.gather(heartbeat_task, status_task, return_exceptions=True),
                    timeout=5.0
                )
            except asyncio.TimeoutError:
                print("⚠️  Some tasks did not finish in time")
            
            print("✅ Graceful shutdown complete")
            
        except KeyboardInterrupt:
            print("\n🛑 Keyboard interrupt received")
            self.running = False
            heartbeat_task.cancel()
            status_task.cancel()
        except Exception as e:
            print(f"❌ Daemon error: {e}")
            raise
        finally:
            self.running = False


async def main():
    """Main entry point for daemon mode."""
    daemon = LynxDaemon()
    await daemon.run()


if __name__ == "__main__":
    asyncio.run(main())

