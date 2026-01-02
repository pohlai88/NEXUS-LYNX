"""
Kernel Domain MCP: Read Registry

Tool ID: kernel.domain.registry.read
Layer: domain
Risk: low
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from lynx.core.registry import MCPTool
from lynx.core.session import ExecutionContext
from lynx.integration.kernel import KernelAPI


class KernelRegistryInput(BaseModel):
    """Input schema for kernel registry read."""
    include_policies: bool = Field(
        default=True,
        description="Include policy references in response",
    )
    include_versions: bool = Field(
        default=True,
        description="Include version hashes for drift detection",
    )


class ToolDefinition(BaseModel):
    """Tool definition schema."""
    id: str
    name: str
    layer: str
    risk: str
    domain: str


class PolicyReference(BaseModel):
    """Policy reference schema."""
    tool_id: str
    risk_level: str
    required_role: List[str]
    required_scope: List[str]


class KernelRegistryOutput(BaseModel):
    """Output schema for kernel registry read."""
    tools: List[ToolDefinition] = Field(description="List of available tool definitions")
    policies: List[PolicyReference] = Field(description="Policy references (if requested)")
    version_hash: Optional[str] = Field(description="Version hash for drift detection (if requested)")
    tenant_id: str = Field(description="Tenant ID for this registry")


async def kernel_registry_read_handler(
    input: KernelRegistryInput,
    context: ExecutionContext,
) -> KernelRegistryOutput:
    """
    Read Kernel registry - list of tool definitions available to this tenant/role.
    
    This is a Domain MCP tool - read-only, low risk.
    
    Args:
        input: KernelRegistryInput
        context: Execution context
    
    Returns:
        KernelRegistryOutput with tool definitions and policies
    """
    # Initialize Kernel API for this tenant (if available)
    kernel_api = None
    try:
        kernel_api = KernelAPI(tenant_id=context.tenant_id)
    except (ValueError, Exception):
        # Kernel API not available (e.g., in tests) - use mock data
        pass
    
    try:
        # Read registry metadata from Kernel (tenant-scoped)
        # TODO: Implement actual Kernel API call
        # For now, return mock data based on registered tools
        
        # Get available tools (this would come from Kernel in production)
        tools = [
            ToolDefinition(
                id="finance.domain.health.read",
                name="Read Financial Health",
                layer="domain",
                risk="low",
                domain="finance",
            ),
            ToolDefinition(
                id="kernel.domain.registry.read",
                name="Read Kernel Registry",
                layer="domain",
                risk="low",
                domain="kernel",
            ),
        ]
        
        policies = []
        if input.include_policies:
            policies = [
                PolicyReference(
                    tool_id="finance.domain.health.read",
                    risk_level="low",
                    required_role=[],
                    required_scope=[],
                ),
                PolicyReference(
                    tool_id="kernel.domain.registry.read",
                    risk_level="low",
                    required_role=[],
                    required_scope=[],
                ),
            ]
        
        version_hash = None
        if input.include_versions:
            # In production, this would be a hash of all tool definitions
            version_hash = "registry-v1.0.0-hash"
        
        return KernelRegistryOutput(
            tools=tools,
            policies=policies,
            version_hash=version_hash,
            tenant_id=context.tenant_id,
        )
    finally:
        if kernel_api:
            await kernel_api.close()


# Register the tool
def register_kernel_registry_read_tool(registry) -> None:
    """Register the kernel.domain.registry.read tool."""
    tool = MCPTool(
        id="kernel.domain.registry.read",
        name="Read Kernel Registry",
        description="Returns list of tool definitions available to this tenant/role, policy references, and version hash for drift detection.",
        layer="domain",
        risk="low",
        domain="kernel",
        input_schema=KernelRegistryInput,
        output_schema=KernelRegistryOutput,
        required_role=[],  # No specific role required for read-only
        required_scope=[],  # No specific scope required for read-only
        handler=kernel_registry_read_handler,
    )
    registry.register(tool)

