"""
Security Domain MCP: Read Permission Explanation

Tool ID: security.domain.permission.read
Layer: domain
Risk: low
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from lynx.core.registry import MCPTool
from lynx.core.session import ExecutionContext
from lynx.integration.kernel import KernelAPI


class SecurityPermissionInput(BaseModel):
    """Input schema for security permission read."""
    tool_id: str = Field(description="Tool ID to check permissions for")
    action: Optional[str] = Field(
        default=None,
        description="Specific action to check (defaults to tool_id)",
    )


class SecurityPermissionOutput(BaseModel):
    """Output schema for security permission read."""
    tool_id: str = Field(description="Tool ID checked")
    allowed: bool = Field(description="Whether action is allowed")
    reason: Optional[str] = Field(description="Explanation of why denied (if not allowed)")
    required_role: List[str] = Field(description="Required roles for this tool")
    required_scope: List[str] = Field(description="Required scopes for this tool")
    current_role: str = Field(description="Current user role")
    current_scope: List[str] = Field(description="Current user scope")
    policy_source: str = Field(description="Source of policy (Kernel or registry)")


async def security_permission_read_handler(
    input: SecurityPermissionInput,
    context: ExecutionContext,
) -> SecurityPermissionOutput:
    """
    Read permission explanation - why something is denied or allowed.
    
    This is a Domain MCP tool - read-only, low risk.
    
    Args:
        input: SecurityPermissionInput
        context: Execution context
    
    Returns:
        SecurityPermissionOutput with permission explanation
    """
    # Initialize Kernel API for this tenant (if available)
    kernel_api = None
    try:
        kernel_api = KernelAPI(tenant_id=context.tenant_id)
    except (ValueError, Exception):
        # Kernel API not available (e.g., in tests) - use mock data
        pass
    
    try:
        # Check permission via Kernel
        action = input.action or input.tool_id
        if kernel_api:
            permission_result = await kernel_api.check_permission(
                user_id=context.user_id,
                action=action,
                resource_type=input.tool_id.split(".")[0],  # Extract domain from tool_id
            )
            allowed = permission_result.get("allowed", False)
            reason = permission_result.get("reason")
        else:
            # Mock permission check for testing
            allowed = True  # Default to allowed in tests
            reason = None
        
        # Get tool requirements (would come from registry in production)
        required_role = []  # Would come from tool registry
        required_scope = []  # Would come from tool registry
        
        # Determine policy source
        if kernel_api:
            policy_source = "Kernel" if permission_result.get("source") == "kernel" else "registry"
        else:
            policy_source = "registry"  # Default in tests
        
        # Build explanation
        if not allowed and not reason:
            if context.user_role not in required_role:
                reason = f"User role '{context.user_role}' not in required roles: {required_role}"
            elif not any(scope in context.user_scope for scope in required_scope):
                reason = f"User scope {context.user_scope} does not include required scopes: {required_scope}"
            else:
                reason = "Permission denied by Kernel policy"
        
        return SecurityPermissionOutput(
            tool_id=input.tool_id,
            allowed=allowed,
            reason=reason,
            required_role=required_role,
            required_scope=required_scope,
            current_role=context.user_role,
            current_scope=context.user_scope,
            policy_source=policy_source,
        )
    finally:
        if kernel_api:
            await kernel_api.close()


# Register the tool
def register_security_permission_read_tool(registry) -> None:
    """Register the security.domain.permission.read tool."""
    tool = MCPTool(
        id="security.domain.permission.read",
        name="Read Permission Explanation",
        description="Returns 'why denied' explanation, required scopes vs current scopes, and policy source (Kernel or registry).",
        layer="domain",
        risk="low",
        domain="security",
        input_schema=SecurityPermissionInput,
        output_schema=SecurityPermissionOutput,
        required_role=[],  # No specific role required for read-only
        required_scope=[],  # No specific scope required for read-only
        handler=security_permission_read_handler,
    )
    registry.register(tool)

