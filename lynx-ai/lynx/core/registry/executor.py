"""
MCP tool executor.

Handles tool execution with validation, permission checks, and audit logging.
"""

from typing import Any, Dict
from lynx.core.registry import MCPTool, MCPToolRegistry
from lynx.core.session import ExecutionContext
from lynx.core.permissions import PermissionChecker
from lynx.core.audit import AuditLogger


class ApprovalRequiredError(Exception):
    """Raised when explicit approval is required for high-risk actions."""
    pass


async def execute_tool(
    tool_id: str,
    input_data: Dict[str, Any],
    context: ExecutionContext,
    registry: MCPToolRegistry,
    permission_checker: PermissionChecker,
    audit_logger: AuditLogger,
) -> Dict[str, Any]:
    """
    Execute an MCP tool with full validation and audit.
    
    This enforces:
    - PRD Law 3: Tool-Only Action
    - PRD Law 4: Suggest First, Execute with Consent
    - PRD Law 5: Audit Is Reality
    - Risk classification (Section 20-21)
    
    Args:
        tool_id: Tool ID to execute
        input_data: Input data for the tool
        context: Execution context
        registry: MCP tool registry
        permission_checker: Permission checker
        audit_logger: Audit logger
    
    Returns:
        Tool execution result
    
    Raises:
        ValueError: If tool not found or input invalid
        PermissionError: If user lacks permissions
        ApprovalRequiredError: If explicit approval required
    """
    # 1. Get tool from registry
    tool = registry.get(tool_id)
    
    # 2. Validate input
    try:
        validated_input = tool.input_schema(**input_data)
    except Exception as e:
        await audit_logger.log_refusal(
            context=context,
            tool=tool,
            reason=f"Input validation failed: {str(e)}",
        )
        raise ValueError(f"Input validation failed: {str(e)}")
    
    # 3. Check permissions
    has_permission = await permission_checker.check(tool, context)
    if not has_permission:
        await audit_logger.log_refusal(
            context=context,
            tool=tool,
            reason="Insufficient permissions",
        )
        raise PermissionError(
            f"Insufficient permissions to execute {tool_id}. "
            f"Required role: {tool.required_role}, "
            f"Required scope: {tool.required_scope}"
        )
    
    # 4. Check risk level and approval
    # Policy: High-risk Cell tools require approved draft + explicit_approval (prod only)
    # Low-risk Cell tools: approved draft is enough
    # Cluster tools: no explicit_approval ever
    from lynx.config import Config
    
    if tool.risk == "high":
        # High-risk tools require explicit approval in production
        if Config.requires_explicit_approval_for_high_risk():
            if context.explicit_approval is not True:
                await audit_logger.log_refusal(
                    context=context,
                    tool=tool,
                    reason="Explicit approval required for high-risk action in production",
                )
                raise ApprovalRequiredError(
                    f"High-risk action {tool_id} requires explicit approval in production mode. "
                    "Please use draft mode first or request approval."
                )
    
    # 5. Log execution start
    await audit_logger.log_execution_start(
        context=context,
        tool=tool,
        input_data=validated_input.model_dump() if hasattr(validated_input, 'model_dump') else validated_input,
    )
    
    # 6. Execute tool
    try:
        if tool.handler is None:
            raise ValueError(f"Tool {tool_id} has no handler")
        
        result = await tool.handler(validated_input, context)
        
        # 7. Validate output
        try:
            if isinstance(result, dict):
                validated_output = tool.output_schema(**result)
            else:
                validated_output = tool.output_schema(**result.__dict__ if hasattr(result, '__dict__') else {})
        except Exception as e:
            # Log validation error but don't fail execution
            await audit_logger.log_execution_warning(
                context=context,
                tool=tool,
                warning=f"Output validation failed: {str(e)}",
            )
            validated_output = result
        
        # 8. Log execution success
        output_dict = validated_output.model_dump() if hasattr(validated_output, 'model_dump') else validated_output
        await audit_logger.log_execution_success(
            context=context,
            tool=tool,
            output_data=output_dict,
        )
        
        return output_dict
        
    except Exception as e:
        # 9. Log execution failure
        await audit_logger.log_execution_failure(
            context=context,
            tool=tool,
            error=str(e),
        )
        raise

