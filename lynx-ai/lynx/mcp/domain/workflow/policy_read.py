"""
Workflow Domain MCP: Read Policy

Tool ID: workflow.domain.policy.read
Layer: domain
Risk: low
"""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from lynx.core.registry import MCPTool
from lynx.core.session import ExecutionContext
from lynx.integration.kernel import KernelAPI


class WorkflowPolicyInput(BaseModel):
    """Input schema for workflow policy read."""
    workflow_type: Optional[str] = Field(
        default=None,
        description="Filter by workflow type",
    )
    include_thresholds: bool = Field(
        default=True,
        description="Include approval thresholds",
    )


class ApprovalRule(BaseModel):
    """Approval rule schema."""
    rule_id: str
    workflow_type: str
    required_role: List[str]
    required_scope: List[str]
    threshold_amount: Optional[float] = None
    approval_count: int


class WorkflowPolicyOutput(BaseModel):
    """Output schema for workflow policy read."""
    approval_rules: List[ApprovalRule] = Field(description="List of approval rules")
    role_gates: Dict[str, List[str]] = Field(description="Role-based gates")
    tenant_id: str = Field(description="Tenant ID")


async def workflow_policy_read_handler(
    input: WorkflowPolicyInput,
    context: ExecutionContext,
) -> WorkflowPolicyOutput:
    """
    Read workflow policy - approval rules, thresholds, role gates (read-only).
    
    This is a Domain MCP tool - read-only, low risk.
    
    Args:
        input: WorkflowPolicyInput
        context: Execution context
    
    Returns:
        WorkflowPolicyOutput with workflow policies
    """
    # Initialize Kernel API for this tenant (if available)
    kernel_api = None
    try:
        kernel_api = KernelAPI(tenant_id=context.tenant_id)
    except (ValueError, Exception):
        pass
    
    try:
        # Read workflow policies from Kernel (tenant-scoped)
        # TODO: Implement actual Kernel API call
        # For now, return mock data
        
        approval_rules = [
            ApprovalRule(
                rule_id="rule-001",
                workflow_type="payment",
                required_role=["admin", "finance_manager"],
                required_scope=["payment_approve"],
                threshold_amount=1000.0 if input.include_thresholds else None,
                approval_count=1,
            ),
            ApprovalRule(
                rule_id="rule-002",
                workflow_type="document",
                required_role=["admin"],
                required_scope=["document_publish"],
                threshold_amount=None,
                approval_count=1,
            ),
        ]
        
        # Apply filters
        if input.workflow_type:
            approval_rules = [r for r in approval_rules if r.workflow_type == input.workflow_type]
        
        # Build role gates
        role_gates = {
            "admin": ["payment_approve", "document_publish", "workflow_create"],
            "finance_manager": ["payment_approve"],
            "user": [],
        }
        
        return WorkflowPolicyOutput(
            approval_rules=approval_rules,
            role_gates=role_gates,
            tenant_id=context.tenant_id,
        )
    finally:
        if kernel_api:
            await kernel_api.close()


# Register the tool
def register_workflow_policy_read_tool(registry) -> None:
    """Register the workflow.domain.policy.read tool."""
    tool = MCPTool(
        id="workflow.domain.policy.read",
        name="Read Workflow Policy",
        description="Returns approval rules, thresholds, and role gates (read-only) required before Cluster can draft workflows safely.",
        layer="domain",
        risk="low",
        domain="workflow",
        input_schema=WorkflowPolicyInput,
        output_schema=WorkflowPolicyOutput,
        required_role=[],
        required_scope=[],
        handler=workflow_policy_read_handler,
    )
    registry.register(tool)

