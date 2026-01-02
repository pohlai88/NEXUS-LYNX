"""
Tenant Domain MCP: Read Profile

Tool ID: tenant.domain.profile.read
Layer: domain
Risk: low
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from lynx.core.registry import MCPTool
from lynx.core.session import ExecutionContext
from lynx.integration.kernel import KernelAPI


class TenantProfileInput(BaseModel):
    """Input schema for tenant profile read."""
    include_modules: bool = Field(
        default=True,
        description="Include enabled modules/feature flags",
    )
    include_user_context: bool = Field(
        default=True,
        description="Include current user role/scope summary",
    )


class TenantProfileOutput(BaseModel):
    """Output schema for tenant profile read."""
    tenant_id: str = Field(description="Tenant ID")
    tenant_name: Optional[str] = Field(description="Tenant name")
    plan: Optional[str] = Field(description="Subscription plan")
    region: Optional[str] = Field(description="Region/locale")
    enabled_modules: List[str] = Field(description="Enabled modules/feature flags (if requested)")
    user_role: Optional[str] = Field(description="Current user role (if requested)")
    user_scope: List[str] = Field(description="Current user scope (if requested)")


async def tenant_profile_read_handler(
    input: TenantProfileInput,
    context: ExecutionContext,
) -> TenantProfileOutput:
    """
    Read tenant profile summary.
    
    This is a Domain MCP tool - read-only, low risk.
    
    Args:
        input: TenantProfileInput
        context: Execution context
    
    Returns:
        TenantProfileOutput with tenant profile and context
    """
    # Initialize Kernel API for this tenant (if available)
    kernel_api = None
    try:
        kernel_api = KernelAPI(tenant_id=context.tenant_id)
    except (ValueError, Exception):
        # Kernel API not available (e.g., in tests) - use mock data
        pass
    
    try:
        # Read tenant profile from Kernel (tenant-scoped)
        # TODO: Implement actual Kernel API call
        # For now, return mock data
        
        # Get tenant customizations from Kernel
        tenant_customizations = {}
        if kernel_api:
            tenant_customizations = await kernel_api.get_tenant_customizations()
        else:
            tenant_customizations = {"name": "Test Tenant", "plan": "standard", "region": "us-east"}
        
        enabled_modules = []
        if input.include_modules:
            # In production, this would come from Kernel
            enabled_modules = ["finance", "workflow", "vpm", "document"]
        
        return TenantProfileOutput(
            tenant_id=context.tenant_id,
            tenant_name=tenant_customizations.get("name", "Unknown Tenant"),
            plan=tenant_customizations.get("plan", "standard"),
            region=tenant_customizations.get("region", "us-east"),
            enabled_modules=enabled_modules if input.include_modules else [],
            user_role=context.user_role if input.include_user_context else None,
            user_scope=context.user_scope if input.include_user_context else [],
        )
    finally:
        if kernel_api:
            await kernel_api.close()


# Register the tool
def register_tenant_profile_read_tool(registry) -> None:
    """Register the tenant.domain.profile.read tool."""
    tool = MCPTool(
        id="tenant.domain.profile.read",
        name="Read Tenant Profile",
        description="Returns tenant profile summary including name, plan, region, enabled modules, and current user role/scope.",
        layer="domain",
        risk="low",
        domain="tenant",
        input_schema=TenantProfileInput,
        output_schema=TenantProfileOutput,
        required_role=[],  # No specific role required for read-only
        required_scope=[],  # No specific scope required for read-only
        handler=tenant_profile_read_handler,
    )
    registry.register(tool)

