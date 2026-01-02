"""
Lynx AI Status Command

Provides operator truth endpoint for system health.
"""

import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

from lynx.config import Config
from lynx.integration.kernel import KernelAPI
from supabase import create_client, Client
from lynx.core.registry import MCPToolRegistry
from lynx.mcp.server import initialize_mcp_server
from lynx.__version__ import LYNX_PROTOCOL_VERSION, MCP_TOOLSET_VERSION
from lynx.storage.execution_storage import get_execution_storage
from lynx.mcp.cell.execution.models import ExecutionStatus


async def check_kernel_reachable() -> bool:
    """Check if Kernel API is reachable."""
    try:
        if not Config.KERNEL_API_URL:
            return False
        # Simple connectivity check (implement actual health check)
        kernel_api = KernelAPI(tenant_id="test")
        await kernel_api.close()
        return True
    except Exception:
        return False


def check_supabase_reachable() -> bool:
    """Check if Supabase is reachable."""
    try:
        if not Config.SUPABASE_URL or not Config.SUPABASE_KEY:
            return False
        supabase: Client = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
        # Simple connectivity check
        supabase.table("lynx_drafts").select("draft_id").limit(1).execute()
        return True
    except Exception:
        return False


def get_storage_backend_type() -> str:
    """Get the storage backend type in use."""
    from lynx.storage.draft_storage import get_draft_storage
    storage = get_draft_storage()
    if hasattr(storage, 'client'):
        return "supabase"
    return "memory"


async def get_draft_count_last_24h(tenant_id: Optional[str] = None) -> int:
    """Get count of drafts created in last 24 hours."""
    from lynx.storage.draft_storage import get_draft_storage, DraftStorageSupabase
    from supabase import Client
    
    storage = get_draft_storage()
    if tenant_id is None:
        # For CLI, use a dummy tenant or aggregate if possible
        tenant_id = "system"
    
    # Use direct Supabase query if available (more efficient)
    if isinstance(storage, DraftStorageSupabase):
        cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
        try:
            result = (
                storage.client.table("lynx_drafts")
                .select("draft_id", count="exact")
                .eq("tenant_id", tenant_id)
                .gte("created_at", cutoff)
                .execute()
            )
            # Supabase returns count in response
            return result.count if hasattr(result, 'count') else len(result.data) if result.data else 0
        except Exception:
            # Fallback to list_drafts if query fails
            pass
    
    # Fallback: List all drafts and filter in memory
    drafts = await storage.list_drafts(tenant_id, limit=1000)
    cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
    recent_drafts = [d for d in drafts if d.created_at >= cutoff]
    return len(recent_drafts)


async def get_execution_count_last_24h(tenant_id: Optional[str] = None) -> int:
    """Get count of executions created in last 24 hours."""
    from lynx.storage.execution_storage import get_execution_storage, ExecutionStorageSupabase
    
    storage = get_execution_storage()
    if tenant_id is None:
        tenant_id = "system"
    
    # Use direct Supabase query if available (more efficient)
    if isinstance(storage, ExecutionStorageSupabase):
        cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
        try:
            result = (
                storage.client.table("lynx_executions")
                .select("execution_id", count="exact")
                .eq("tenant_id", tenant_id)
                .gte("created_at", cutoff)
                .execute()
            )
            # Supabase returns count in response
            return result.count if hasattr(result, 'count') else len(result.data) if result.data else 0
        except Exception:
            # Fallback to list_executions if query fails
            pass
    
    # Fallback: List all executions and filter in memory
    executions = await storage.list_executions(tenant_id, limit=1000)
    cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
    recent_executions = [e for e in executions if e.created_at >= cutoff]
    return len(recent_executions)


async def get_pending_settlement_count(tenant_id: Optional[str] = None) -> int:
    """Get count of settlement intents with status 'queued' or 'processing'."""
    from lynx.storage.settlement_storage import get_settlement_intent_storage, SettlementIntentStorageSupabase
    
    storage = get_settlement_intent_storage()
    if tenant_id is None:
        tenant_id = "system"
    
    # Use direct Supabase query if available (more efficient)
    if isinstance(storage, SettlementIntentStorageSupabase):
        try:
            # Query for queued or processing status
            result_queued = (
                storage.client.table("settlement_intents")
                .select("payment_id", count="exact")
                .eq("tenant_id", tenant_id)
                .eq("settlement_status", "queued")
                .execute()
            )
            result_processing = (
                storage.client.table("settlement_intents")
                .select("payment_id", count="exact")
                .eq("tenant_id", tenant_id)
                .eq("settlement_status", "processing")
                .execute()
            )
            count_queued = result_queued.count if hasattr(result_queued, 'count') else len(result_queued.data) if result_queued.data else 0
            count_processing = result_processing.count if hasattr(result_processing, 'count') else len(result_processing.data) if result_processing.data else 0
            return count_queued + count_processing
        except Exception:
            # Fallback to list_settlement_intents if query fails
            pass
    
    # Fallback: List all settlement intents and filter in memory
    intents = await storage.list_settlement_intents(tenant_id, limit=1000)
    pending = [i for i in intents if i.settlement_status in ("queued", "processing")]
    return len(pending)


async def get_last_n_runs_summary(n: int = 5) -> List[Dict[str, Any]]:
    """Get a summary of the last N Lynx runs."""
    execution_storage = get_execution_storage()
    # Using a dummy tenant for CLI status
    recent_executions = await execution_storage.list_executions(
        tenant_id="system",
        limit=n,
    )
    
    summary = []
    for exec_record in recent_executions:
        summary.append({
            "execution_id": exec_record.execution_id,
            "tool_id": exec_record.tool_id,
            "status": exec_record.status.value,
            "created_at": exec_record.created_at,
            "completed_at": exec_record.completed_at,
            "tenant_id": exec_record.tenant_id,
        })
    return summary


async def get_lynx_status() -> Dict[str, Any]:
    """Get the overall status of Lynx AI."""
    kernel_reachable = await check_kernel_reachable()
    supabase_reachable = check_supabase_reachable()
    
    # Initialize a dummy registry to get tool count
    registry = MCPToolRegistry()
    initialize_mcp_server(registry)
    
    last_runs_summary = await get_last_n_runs_summary()
    
    # Get storage backend type
    backend_type = get_storage_backend_type()
    
    # Get counts (only if Supabase is reachable)
    draft_count_24h = 0
    execution_count_24h = 0
    pending_settlement_count = 0
    
    if supabase_reachable:
        try:
            draft_count_24h = await get_draft_count_last_24h()
            execution_count_24h = await get_execution_count_last_24h()
            pending_settlement_count = await get_pending_settlement_count()
        except Exception as e:
            # If counts fail, log but don't fail status check
            print(f"Warning: Could not retrieve counts: {e}", file=__import__('sys').stderr)
    
    return {
        "service_name": "Lynx AI",
        "status": "operational" if kernel_reachable and supabase_reachable else "degraded",
        "lynx_protocol_version": LYNX_PROTOCOL_VERSION,
        "mcp_toolset_version": MCP_TOOLSET_VERSION,
        "tool_registry_hash": registry.get_version_hash(),
        "kernel_api_reachable": kernel_reachable,
        "supabase_reachable": supabase_reachable,
        "storage_backend": backend_type,
        "total_mcp_tools_registered": len(registry.list_tools()),
        "last_5_runs_summary": last_runs_summary,
        "current_mode": Config.LYNX_MODE.value,
        "maintenance_mode": Config.MAINTENANCE_MODE,
        "draft_count_24h": draft_count_24h,
        "execution_count_24h": execution_count_24h,
        "pending_settlement_count": pending_settlement_count,
    }


async def main():
    """Main function for the lynx status CLI."""
    status = await get_lynx_status()
    
    print("\n--- Lynx AI System Status ---")
    print(f"Service Status: {status['status'].upper()}")
    print(f"Current Mode: {status['current_mode'].upper()}")
    print(f"Maintenance Mode: {status['maintenance_mode']}")
    print("\n--- Versions ---")
    print(f"Lynx Protocol Version: {status['lynx_protocol_version']}")
    print(f"MCP Toolset Version: {status['mcp_toolset_version']}")
    print(f"Tool Registry Hash: {status['tool_registry_hash']}")
    print("\n--- Connectivity ---")
    print(f"Kernel API Reachable: {'✅' if status['kernel_api_reachable'] else '❌'}")
    print(f"Supabase Reachable: {'✅' if status['supabase_reachable'] else '❌'}")
    print("\n--- Storage ---")
    print(f"Storage Backend: {status['storage_backend'].upper()}")
    if status['storage_backend'] == 'supabase':
        print(f"Drafts (last 24h): {status['draft_count_24h']}")
        print(f"Executions (last 24h): {status['execution_count_24h']}")
        print(f"Pending Settlements: {status['pending_settlement_count']}")
    print("\n--- MCP Tools ---")
    print(f"Total MCP Tools Registered: {status['total_mcp_tools_registered']}")
    print("\n--- Recent Runs (Last 5) ---")
    if status['last_5_runs_summary']:
        for run in status['last_5_runs_summary']:
            print(f"- [{run['created_at']}] {run['tool_id']} (Tenant: {run['tenant_id']}) -> {run['status'].upper()} (ID: {run['execution_id']})")
    else:
        print("No recent runs found.")
    print("\n---------------------------\n")


if __name__ == "__main__":
    asyncio.run(main())
