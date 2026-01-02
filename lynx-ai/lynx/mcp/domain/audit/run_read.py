"""
Audit Domain MCP: Read Run History

Tool ID: audit.domain.run.read
Layer: domain
Risk: low
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from lynx.core.registry import MCPTool
from lynx.core.session import ExecutionContext
from lynx.integration.kernel import KernelAPI


class AuditRunInput(BaseModel):
    """Input schema for audit run read."""
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of runs to return",
    )
    tool_id: Optional[str] = Field(
        default=None,
        description="Filter by tool ID",
    )
    status: Optional[str] = Field(
        default=None,
        description="Filter by status (completed, failed, blocked)",
    )
    since: Optional[str] = Field(
        default=None,
        description="Filter runs since this timestamp (ISO format)",
    )


class RunSummary(BaseModel):
    """Run summary schema."""
    run_id: str
    actor_id: str
    timestamp: str
    outcome: str
    tool_id: Optional[str] = None
    status: str


class AuditRunOutput(BaseModel):
    """Output schema for audit run read."""
    runs: List[RunSummary] = Field(description="List of Lynx runs")
    total_count: int = Field(description="Total number of runs (may be more than returned)")
    tenant_id: str = Field(description="Tenant ID for these runs")


async def audit_run_read_handler(
    input: AuditRunInput,
    context: ExecutionContext,
) -> AuditRunOutput:
    """
    Read audit run history - last N Lynx runs.
    
    This is a Domain MCP tool - read-only, low risk.
    
    Args:
        input: AuditRunInput
        context: Execution context
    
    Returns:
        AuditRunOutput with run history
    """
    # Initialize Kernel API for this tenant (if available)
    kernel_api = None
    try:
        kernel_api = KernelAPI(tenant_id=context.tenant_id)
    except (ValueError, Exception):
        # Kernel API not available (e.g., in tests) - use mock data
        pass
    
    try:
        # Read audit runs from Kernel/Supabase (tenant-scoped)
        # TODO: Implement actual Kernel API call or Supabase query
        # For now, return mock data
        
        # In production, this would query the audit_logs table filtered by tenant_id
        runs = [
            RunSummary(
                run_id="run-001",
                actor_id=context.user_id,
                timestamp=datetime.now().isoformat(),
                outcome="completed",
                tool_id="finance.domain.health.read",
                status="completed",
            ),
            RunSummary(
                run_id="run-002",
                actor_id=context.user_id,
                timestamp=datetime.now().isoformat(),
                outcome="denied",
                tool_id="test.restricted.tool",
                status="blocked",
            ),
        ]
        
        # Apply filters
        if input.tool_id:
            runs = [r for r in runs if r.tool_id == input.tool_id]
        
        if input.status:
            runs = [r for r in runs if r.status == input.status]
        
        # Limit results
        runs = runs[:input.limit]
        
        return AuditRunOutput(
            runs=runs,
            total_count=len(runs),  # In production, this would be total count from query
            tenant_id=context.tenant_id,
        )
    finally:
        if kernel_api:
            await kernel_api.close()


# Register the tool
def register_audit_run_read_tool(registry) -> None:
    """Register the audit.domain.run.read tool."""
    tool = MCPTool(
        id="audit.domain.run.read",
        name="Read Audit Run History",
        description="Returns last N Lynx runs with optional filtering by tool_id, status, or since timestamp.",
        layer="domain",
        risk="low",
        domain="audit",
        input_schema=AuditRunInput,
        output_schema=AuditRunOutput,
        required_role=[],  # No specific role required for read-only
        required_scope=[],  # No specific scope required for read-only
        handler=audit_run_read_handler,
    )
    registry.register(tool)

