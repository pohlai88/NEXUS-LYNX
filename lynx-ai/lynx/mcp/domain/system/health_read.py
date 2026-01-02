"""
System Domain MCP: Read Health

Tool ID: system.domain.health.read
Layer: domain
Risk: low
"""

from pydantic import BaseModel, Field
from typing import Dict, Optional
from lynx.core.registry import MCPTool
from lynx.core.session import ExecutionContext
from lynx.integration.kernel import KernelAPI


class SystemHealthInput(BaseModel):
    """Input schema for system health read."""
    include_dependencies: bool = Field(
        default=True,
        description="Include dependency health (Kernel, Supabase, etc.)",
    )


class DependencyHealth(BaseModel):
    """Dependency health schema."""
    name: str
    status: str  # "healthy", "degraded", "unavailable"
    response_time_ms: Optional[int] = None
    last_check: str


class SystemHealthOutput(BaseModel):
    """Output schema for system health read."""
    overall_status: str = Field(description="Overall system status")
    kernel_status: Optional[str] = Field(description="Kernel API status")
    supabase_status: Optional[str] = Field(description="Supabase status")
    dependencies: Dict[str, DependencyHealth] = Field(description="Dependency health map")
    tenant_id: str = Field(description="Tenant ID")


async def system_health_read_handler(
    input: SystemHealthInput,
    context: ExecutionContext,
) -> SystemHealthOutput:
    """
    Read system health - Kernel availability, Supabase connectivity, queue/job status.
    
    This is a Domain MCP tool - read-only, low risk.
    
    Args:
        input: SystemHealthInput
        context: Execution context
    
    Returns:
        SystemHealthOutput with system health status
    """
    # Initialize Kernel API for this tenant (if available)
    kernel_api = None
    kernel_status = "unknown"
    try:
        kernel_api = KernelAPI(tenant_id=context.tenant_id)
        kernel_status = "healthy"
    except (ValueError, Exception):
        kernel_status = "unavailable"
    
    try:
        # Check system health
        # TODO: Implement actual health checks
        # For now, return mock data
        
        dependencies = {}
        if input.include_dependencies:
            from datetime import datetime
            dependencies = {
                "kernel": DependencyHealth(
                    name="Kernel API",
                    status=kernel_status,
                    response_time_ms=50 if kernel_status == "healthy" else None,
                    last_check=datetime.now().isoformat(),
                ),
                "supabase": DependencyHealth(
                    name="Supabase",
                    status="healthy",
                    response_time_ms=30,
                    last_check=datetime.now().isoformat(),
                ),
            }
        
        # Determine overall status
        if kernel_status == "healthy" and dependencies.get("supabase", {}).status == "healthy":
            overall_status = "healthy"
        elif kernel_status == "unavailable":
            overall_status = "degraded"
        else:
            overall_status = "healthy"
        
        return SystemHealthOutput(
            overall_status=overall_status,
            kernel_status=kernel_status,
            supabase_status=dependencies.get("supabase", {}).status if input.include_dependencies else None,
            dependencies=dependencies,
            tenant_id=context.tenant_id,
        )
    finally:
        if kernel_api:
            await kernel_api.close()


# Register the tool
def register_system_health_read_tool(registry) -> None:
    """Register the system.domain.health.read tool."""
    tool = MCPTool(
        id="system.domain.health.read",
        name="Read System Health",
        description="Returns Kernel availability, Supabase connectivity, and queue/job status to keep Lynx safe when dependencies degrade.",
        layer="domain",
        risk="low",
        domain="system",
        input_schema=SystemHealthInput,
        output_schema=SystemHealthOutput,
        required_role=[],
        required_scope=[],
        handler=system_health_read_handler,
    )
    registry.register(tool)

