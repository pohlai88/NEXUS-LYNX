"""
Audit logger for Lynx AI.

Logs all Lynx interactions and tool executions.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from supabase import create_client, Client
from lynx.core.registry import MCPTool
from lynx.core.session import ExecutionContext


class AuditLogger:
    """Logs all Lynx actions for audit compliance."""
    
    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
    ):
        """
        Initialize audit logger.
        
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase service key
        """
        self.supabase: Client = create_client(supabase_url, supabase_key)
    
    async def log_lynx_run(
        self,
        run_id: str,
        user_id: str,
        tenant_id: str,
        user_query: str,
        lynx_response: str,
        status: str = "completed",
    ) -> None:
        """
        Log a Lynx Run (user interaction).
        
        Args:
            run_id: Lynx Run ID
            user_id: User ID
            tenant_id: Tenant ID
            user_query: User's query
            lynx_response: Lynx's response
            status: Run status ("completed", "failed", "blocked")
        """
        try:
            self.supabase.table("lynx_runs").insert({
                "run_id": run_id,
                "user_id": user_id,
                "tenant_id": tenant_id,
                "user_query": user_query,
                "lynx_response": lynx_response,
                "timestamp": datetime.now().isoformat(),
                "status": status,
            }).execute()
        except Exception as e:
            # Log error but don't fail - audit logging should be resilient
            print(f"Failed to log Lynx Run: {e}")
    
    async def log_execution_start(
        self,
        context: ExecutionContext,
        tool: MCPTool,
        input_data: Dict[str, Any],
    ) -> None:
        """Log tool execution start."""
        await self._log_tool_call(
            context=context,
            tool=tool,
            input_data=input_data,
            output_data=None,
            approved=False,
            refused=False,
        )
    
    async def log_execution_success(
        self,
        context: ExecutionContext,
        tool: MCPTool,
        output_data: Dict[str, Any],
    ) -> None:
        """Log successful tool execution."""
        await self._log_tool_call(
            context=context,
            tool=tool,
            input_data=None,  # Already logged in start
            output_data=output_data,
            approved=context.explicit_approval or tool.risk != "high",
            refused=False,
        )
    
    async def log_execution_failure(
        self,
        context: ExecutionContext,
        tool: MCPTool,
        error: str,
    ) -> None:
        """Log failed tool execution."""
        await self._log_tool_call(
            context=context,
            tool=tool,
            input_data=None,
            output_data={"error": error},
            approved=False,
            refused=False,
        )
    
    async def log_execution_warning(
        self,
        context: ExecutionContext,
        tool: MCPTool,
        warning: str,
    ) -> None:
        """Log execution warning."""
        await self._log_tool_call(
            context=context,
            tool=tool,
            input_data=None,
            output_data={"warning": warning},
            approved=False,
            refused=False,
        )
    
    async def log_refusal(
        self,
        context: ExecutionContext,
        tool: MCPTool,
        reason: str,
    ) -> None:
        """
        Log a refused/blocked action.
        
        This enforces PRD Section 22: Failure & Refusal Behavior.
        """
        await self._log_tool_call(
            context=context,
            tool=tool,
            input_data=None,
            output_data=None,
            approved=False,
            refused=True,
            refusal_reason=reason,
        )
    
    async def _log_tool_call(
        self,
        context: ExecutionContext,
        tool: MCPTool,
        input_data: Optional[Dict[str, Any]],
        output_data: Optional[Dict[str, Any]],
        approved: bool,
        refused: bool,
        refusal_reason: Optional[str] = None,
    ) -> None:
        """Internal method to log tool calls."""
        try:
            self.supabase.table("audit_logs").insert({
                "run_id": context.lynx_run_id,
                "tool_id": tool.id,
                "user_id": context.user_id,
                "tenant_id": context.tenant_id,
                "input": input_data or {},
                "output": output_data or {},
                "risk_level": tool.risk,
                "approved": approved,
                "approved_by": context.user_id if approved else None,
                "refused": refused,
                "refusal_reason": refusal_reason,
                "timestamp": datetime.now().isoformat(),
            }).execute()
        except Exception as e:
            # Log error but don't fail - audit logging should be resilient
            print(f"Failed to log tool call: {e}")

