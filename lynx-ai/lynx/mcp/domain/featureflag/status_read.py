"""
Feature Flag Domain MCP: Read Status

Tool ID: featureflag.domain.status.read
Layer: domain
Risk: low
"""

from pydantic import BaseModel, Field
from typing import List, Dict
from lynx.core.registry import MCPTool
from lynx.core.session import ExecutionContext
from lynx.integration.kernel import KernelAPI


class FeatureFlagStatusInput(BaseModel):
    """Input schema for feature flag status read."""
    include_modules: bool = Field(
        default=True,
        description="Include enabled modules",
    )
    include_tools: bool = Field(
        default=True,
        description="Include enabled tools/features",
    )


class FeatureFlagStatusOutput(BaseModel):
    """Output schema for feature flag status read."""
    enabled_modules: List[str] = Field(description="List of enabled modules")
    enabled_tools: List[str] = Field(description="List of enabled tools/features")
    feature_flags: Dict[str, bool] = Field(description="Feature flag status map")
    tenant_id: str = Field(description="Tenant ID for these flags")


async def featureflag_status_read_handler(
    input: FeatureFlagStatusInput,
    context: ExecutionContext,
) -> FeatureFlagStatusOutput:
    """
    Read feature flag status - which modules/tools/features are enabled per tenant.
    
    This is a Domain MCP tool - read-only, low risk.
    
    Args:
        input: FeatureFlagStatusInput
        context: Execution context
    
    Returns:
        FeatureFlagStatusOutput with feature flag status
    """
    # Initialize Kernel API for this tenant (if available)
    kernel_api = None
    try:
        kernel_api = KernelAPI(tenant_id=context.tenant_id)
    except (ValueError, Exception):
        pass
    
    try:
        # Read feature flags from Kernel (tenant-scoped)
        # TODO: Implement actual Kernel API call
        # For now, return mock data
        
        enabled_modules = []
        if input.include_modules:
            enabled_modules = ["finance", "workflow", "vpm", "document", "portal"]
        
        enabled_tools = []
        if input.include_tools:
            enabled_tools = [
                "finance.domain.health.read",
                "workflow.domain.status.read",
                "vpm.domain.vendor.read",
            ]
        
        feature_flags = {
            "lynx_enabled": True,
            "cluster_drafting_enabled": True,
            "cell_execution_enabled": False,  # Not enabled yet
            "advanced_audit_enabled": False,
        }
        
        return FeatureFlagStatusOutput(
            enabled_modules=enabled_modules,
            enabled_tools=enabled_tools,
            feature_flags=feature_flags,
            tenant_id=context.tenant_id,
        )
    finally:
        if kernel_api:
            await kernel_api.close()


# Register the tool
def register_featureflag_status_read_tool(registry) -> None:
    """Register the featureflag.domain.status.read tool."""
    tool = MCPTool(
        id="featureflag.domain.status.read",
        name="Read Feature Flag Status",
        description="Returns which modules/tools/features are enabled per tenant to prevent suggesting unavailable actions.",
        layer="domain",
        risk="low",
        domain="featureflag",
        input_schema=FeatureFlagStatusInput,
        output_schema=FeatureFlagStatusOutput,
        required_role=[],
        required_scope=[],
        handler=featureflag_status_read_handler,
    )
    registry.register(tool)

