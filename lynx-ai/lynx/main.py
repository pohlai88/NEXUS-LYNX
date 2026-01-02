"""
Lynx AI main entry point.

This is the main application entry point for Lynx AI.
"""

import asyncio
import sys
from lynx.core.runtime.app import app, load_config
from lynx.core.runtime.agent import create_lynx_agent
from lynx.core.session import SessionManager, ExecutionContext
from lynx.core.registry import MCPToolRegistry
from lynx.core.permissions import PermissionChecker
from lynx.core.audit import AuditLogger
from lynx.integration.kernel import KernelAPI


async def main():
    """Main application entry point."""
    print("🚀 Starting Lynx AI...")
    print("=" * 60)
    
    # Load configuration
    try:
        config = load_config()
        print("✅ Configuration loaded")
    except Exception as e:
        print(f"❌ Failed to load configuration: {e}")
        print("\n💡 Please:")
        print("   1. Copy config/config.yaml.example to config/config.yaml")
        print("   2. Set required environment variables")
        sys.exit(1)
    
    # Initialize components
    session_manager = SessionManager()
    tool_registry = MCPToolRegistry()
    print("✅ Core components initialized")
    
    # Initialize audit logger
    try:
        audit_logger = AuditLogger(
            supabase_url=config["supabase"]["url"],
            supabase_key=config["supabase"]["key"],
        )
        print("✅ Audit logger initialized")
    except Exception as e:
        print(f"⚠️  Audit logger initialization failed: {e}")
        print("   Continuing without audit logging (not recommended for production)")
        audit_logger = None
    
    # Initialize MCP server and register tools
    try:
        from lynx.mcp.server import initialize_mcp_server
        initialize_mcp_server(tool_registry)
        print("✅ MCP server initialized")
    except Exception as e:
        print(f"⚠️  MCP server initialization failed: {e}")
        print("   Some tools may not be available")
    
    print("\n" + "=" * 60)
    print("📋 Lynx AI Status:")
    print(f"   ✅ Tools registered: {len(tool_registry.list_all())}")
    print(f"   ✅ Domain MCPs: {len(tool_registry.list_by_layer('domain'))}")
    print(f"   ✅ Cluster MCPs: {len(tool_registry.list_by_layer('cluster'))}")
    print(f"   ✅ Cell MCPs: {len(tool_registry.list_by_layer('cell'))}")
    print(f"   ✅ Active sessions: {len(session_manager.sessions)}")
    print("\n💡 Next steps:")
    print("   1. Complete Phase 1: Foundation + Governance")
    print("   2. Implement remaining Domain MCPs")
    print("   3. Implement Cluster MCPs")
    print("   4. Implement Cell MCPs")
    print("\n🔗 See docs/IMPLEMENTATION/IMPLEMENTATION-LYNX-001.md for details")
    print("=" * 60)


if __name__ == "__main__":
    # Check runner mode
    from lynx.config import Config, LynxRunner
    
    if Config.LYNX_RUNNER == LynxRunner.DAEMON:
        # Redirect to daemon mode
        from lynx.runtime.daemon import main as daemon_main
        asyncio.run(daemon_main())
    else:
        # Oneshot mode (default) - initialize and exit
        asyncio.run(main())

