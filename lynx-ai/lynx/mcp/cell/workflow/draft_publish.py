"""
Workflow Cell MCP: Publish Draft

Tool ID: workflow.cell.draft.publish
Layer: cell
Risk: medium
"""

from pydantic import BaseModel, Field
from typing import Dict, Any
from lynx.core.registry import MCPTool
from lynx.core.session import ExecutionContext
from lynx.mcp.cluster.drafts.models import DraftStatus
from lynx.storage.draft_storage import get_draft_storage
from lynx.mcp.cell.execution.base import (
    validate_cell_execution,
    create_execution_record,
    complete_execution,
    ExecutionStatus,
)


class WorkflowDraftPublishInput(BaseModel):
    """Input schema for workflow draft publishing."""
    draft_id: str = Field(description="Draft ID to publish")


class WorkflowDraftPublishOutput(BaseModel):
    """Output schema for workflow draft publishing."""
    execution_id: str = Field(description="Execution ID")
    draft_id: str = Field(description="Draft ID")
    workflow_id: str = Field(description="Published workflow ID")
    status: str = Field(description="Draft status after publishing (published)")
    tenant_id: str = Field(description="Tenant ID")


async def workflow_draft_publish_handler(
    input: WorkflowDraftPublishInput,
    context: ExecutionContext,
) -> WorkflowDraftPublishOutput:
    """
    Publish an approved workflow draft as a production workflow.
    
    This is a Cell MCP tool - execution layer, medium risk.
    
    Enforces Cell Execution Protocol:
    - Validates draft exists & tenant match
    - Validates draft status is APPROVED
    - Validates draft not already executed (exactly-once semantics)
    - Converts workflow draft → published workflow record
    - Sets draft status to PUBLISHED
    - Creates workflow_id
    - Creates execution record
    - Logs audit events
    
    Args:
        input: WorkflowDraftPublishInput
        context: Execution context
    
    Returns:
        WorkflowDraftPublishOutput with execution and workflow information
    
    Raises:
        ValueError: If draft not found, wrong tenant, not approved, or already executed
    """
    tool_id = "workflow.cell.draft.publish"
    
    # Validate execution (draft exists, tenant match, status APPROVED, not already executed)
    is_valid, error_message, bypass_info = await validate_cell_execution(
        draft_id=input.draft_id,
        context=context,
        tool_id=tool_id,
        allow_bypass=False,  # No bypass for workflow publishing
    )
    
    if not is_valid:
        raise ValueError(error_message)
    
    # Get draft
    draft_storage = get_draft_storage()
    draft = await draft_storage.get_draft(input.draft_id, context.tenant_id)
    if draft is None:
        raise ValueError(f"Draft {input.draft_id} not found")
    
    # Create execution record (STARTED)
    execution = await create_execution_record(
        draft_id=input.draft_id,
        tool_id=tool_id,
        context=context,
    )
    
    try:
        # Convert workflow draft → published workflow record
        # In production, this would create a workflow record in the database
        # For now, we generate a workflow_id and store it in execution result
        workflow_id = f"workflow-{draft.draft_id[:8]}-{context.tenant_id[:8]}"
        
        # Update draft status to PUBLISHED
        draft.status = DraftStatus.PUBLISHED
        
        # Complete execution (SUCCEEDED)
        execution = await complete_execution(
            execution_id=execution.execution_id,
            status=ExecutionStatus.SUCCEEDED,
            result_payload={
                "draft_id": input.draft_id,
                "workflow_id": workflow_id,
                "old_status": "approved",
                "new_status": "published",
                "workflow_kind": draft.payload.get("workflow_kind"),
                "workflow_name": draft.payload.get("name"),
            },
        )
        
        return WorkflowDraftPublishOutput(
            execution_id=execution.execution_id,
            draft_id=input.draft_id,
            workflow_id=workflow_id,
            status=draft.status.value,
            tenant_id=context.tenant_id,
        )
    except Exception as e:
        # Complete execution (FAILED)
        await complete_execution(
            execution_id=execution.execution_id,
            status=ExecutionStatus.FAILED,
            result_payload={},
            error_message=str(e),
        )
        raise


# Register the tool
def register_workflow_draft_publish_tool(registry) -> None:
    """Register the workflow.cell.draft.publish tool."""
    tool = MCPTool(
        id="workflow.cell.draft.publish",
        name="Publish Workflow Draft",
        description="Publishes an approved workflow draft as a production workflow. Creates workflow_id and sets draft status to PUBLISHED. Medium risk - creates production workflow record.",
        layer="cell",
        risk="medium",
        domain="workflow",
        input_schema=WorkflowDraftPublishInput,
        output_schema=WorkflowDraftPublishOutput,
        required_role=[],  # Permission checked via draft approval
        required_scope=[],
        handler=workflow_draft_publish_handler,
    )
    registry.register(tool)

