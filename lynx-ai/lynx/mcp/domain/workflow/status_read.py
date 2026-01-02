"""
Workflow Domain MCP: Read Status

Tool ID: workflow.domain.status.read
Layer: domain
Risk: low
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from lynx.core.registry import MCPTool
from lynx.core.session import ExecutionContext
from lynx.integration.kernel import KernelAPI


class WorkflowStatusInput(BaseModel):
    """Input schema for workflow status read."""
    include_events: bool = Field(
        default=True,
        description="Include last N workflow events",
    )
    event_limit: int = Field(
        default=10,
        ge=1,
        le=50,
        description="Maximum number of events to return (if include_events is True)",
    )


class WorkflowEvent(BaseModel):
    """Workflow event schema."""
    event_id: str
    workflow_id: str
    event_type: str
    timestamp: str
    actor_id: str
    description: str


class WorkflowStatusOutput(BaseModel):
    """Output schema for workflow status read."""
    active_workflows_count: int = Field(description="Number of active workflows")
    pending_approvals_count: int = Field(description="Number of pending approvals")
    recent_events: List[WorkflowEvent] = Field(description="Last N workflow events (if requested)")
    tenant_id: str = Field(description="Tenant ID for these workflows")


async def workflow_status_read_handler(
    input: WorkflowStatusInput,
    context: ExecutionContext,
) -> WorkflowStatusOutput:
    """
    Read workflow status - active workflows, pending approvals, recent events.
    
    This is a Domain MCP tool - read-only, low risk.
    
    Args:
        input: WorkflowStatusInput
        context: Execution context
    
    Returns:
        WorkflowStatusOutput with workflow status
    """
    # Initialize Kernel API for this tenant (if available)
    kernel_api = None
    try:
        kernel_api = KernelAPI(tenant_id=context.tenant_id)
    except (ValueError, Exception):
        # Kernel API not available (e.g., in tests) - use mock data
        pass
    
    try:
        # Read workflow status from Kernel (tenant-scoped)
        # TODO: Implement actual Kernel API call
        # For now, return mock data
        
        # Get workflow metadata from Kernel
        if kernel_api:
            workflow_metadata = await kernel_api.get_metadata("workflow")
        else:
            workflow_metadata = {"active_count": 5, "pending_approvals": 2}
        
        # In production, this would query active workflows and pending approvals
        active_workflows_count = workflow_metadata.get("active_count", 5)
        pending_approvals_count = workflow_metadata.get("pending_approvals", 2)
        
        recent_events = []
        if input.include_events:
            # In production, this would query workflow events table
            recent_events = [
                WorkflowEvent(
                    event_id="event-001",
                    workflow_id="workflow-001",
                    event_type="approval_requested",
                    timestamp=datetime.now().isoformat(),
                    actor_id=context.user_id,
                    description="Document approval requested",
                ),
                WorkflowEvent(
                    event_id="event-002",
                    workflow_id="workflow-002",
                    event_type="workflow_completed",
                    timestamp=datetime.now().isoformat(),
                    actor_id=context.user_id,
                    description="Payment workflow completed",
                ),
            ][:input.event_limit]
        
        return WorkflowStatusOutput(
            active_workflows_count=active_workflows_count,
            pending_approvals_count=pending_approvals_count,
            recent_events=recent_events,
            tenant_id=context.tenant_id,
        )
    finally:
        if kernel_api:
            await kernel_api.close()


# Register the tool
def register_workflow_status_read_tool(registry) -> None:
    """Register the workflow.domain.status.read tool."""
    tool = MCPTool(
        id="workflow.domain.status.read",
        name="Read Workflow Status",
        description="Returns active workflows count, pending approvals count, and last N workflow events.",
        layer="domain",
        risk="low",
        domain="workflow",
        input_schema=WorkflowStatusInput,
        output_schema=WorkflowStatusOutput,
        required_role=[],  # No specific role required for read-only
        required_scope=[],  # No specific scope required for read-only
        handler=workflow_status_read_handler,
    )
    registry.register(tool)

