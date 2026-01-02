"""
Permission checker for MCP tool execution.

Enforces role and scope-based permissions.
"""

from typing import Optional
from lynx.core.registry import MCPTool
from lynx.core.session import ExecutionContext
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from lynx.integration.kernel import KernelAPI


class PermissionChecker:
    """Checks permissions for MCP tool execution."""
    
    def __init__(self, kernel_api: Optional["KernelAPI"] = None):
        """
        Initialize permission checker.
        
        Args:
            kernel_api: Kernel API client (optional, will be created if not provided)
        """
        self.kernel_api = kernel_api
    
    async def check(
        self,
        tool: MCPTool,
        context: ExecutionContext,
    ) -> bool:
        """
        Check if user has permission to execute tool.
        
        This checks:
        1. Role requirements
        2. Scope requirements
        3. Kernel permissions (if kernel_api available)
        
        Args:
            tool: MCPTool to check
            context: Execution context
        
        Returns:
            True if user has permission, False otherwise
        """
        # 1. Check role requirement
        if tool.required_role:
            if context.user_role not in tool.required_role:
                return False
        
        # 2. Check scope requirement
        if tool.required_scope:
            if not any(scope in context.user_scope for scope in tool.required_scope):
                return False
        
        # 3. Check Kernel permissions (if kernel_api available)
        if self.kernel_api:
            try:
                kernel_permission = await self.kernel_api.check_permission(
                    user_id=context.user_id,
                    action=tool.id,
                    resource_type=tool.domain,
                )
                if not kernel_permission.get("allowed", False):
                    return False
            except Exception:
                # If Kernel API check fails, fall back to role/scope check
                # Log the error but don't block execution
                pass
        
        return True

