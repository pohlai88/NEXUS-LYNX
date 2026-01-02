"""
Docs Cell MCP: Submit Draft for Approval

Tool ID: docs.cell.draft.submit_for_approval
Layer: cell
Risk: low
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


class DocsDraftSubmitInput(BaseModel):
    """Input schema for document draft submission."""
    draft_id: str = Field(description="Draft ID to submit for approval")


class DocsDraftSubmitOutput(BaseModel):
    """Output schema for document draft submission."""
    execution_id: str = Field(description="Execution ID")
    draft_id: str = Field(description="Draft ID")
    status: str = Field(description="Draft status after submission (submitted)")
    tenant_id: str = Field(description="Tenant ID")


async def docs_draft_submit_for_approval_handler(
    input: DocsDraftSubmitInput,
    context: ExecutionContext,
) -> DocsDraftSubmitOutput:
    """
    Submit a document draft for approval.
    
    This is a Cell MCP tool - execution layer, low risk.
    
    Enforces Cell Execution Protocol:
    - Validates draft exists & tenant match
    - Validates draft status (must be DRAFT, not CANCELLED)
    - Changes draft status to SUBMITTED
    - Creates execution record
    - Logs audit events
    
    Note: This is "safe execution" - only changes draft state, no production mutation.
    
    Args:
        input: DocsDraftSubmitInput
        context: Execution context
    
    Returns:
        DocsDraftSubmitOutput with execution and draft information
    
    Raises:
        ValueError: If draft not found, wrong tenant, or invalid status
    """
    tool_id = "docs.cell.draft.submit_for_approval"
    
    # Validate execution (draft exists, tenant match, status check)
    # Note: For submit, we allow DRAFT status (not just APPROVED)
    draft_storage = get_draft_storage()
    draft = await draft_storage.get_draft(input.draft_id, context.tenant_id)
    
    if draft is None:
        raise ValueError(
            f"Draft {input.draft_id} not found or does not belong to tenant {context.tenant_id}"
        )
    
    if draft.status == DraftStatus.CANCELLED:
        raise ValueError(f"Draft {input.draft_id} is cancelled and cannot be submitted")
    
    if draft.status == DraftStatus.SUBMITTED:
        raise ValueError(f"Draft {input.draft_id} is already submitted")
    
    if draft.status == DraftStatus.APPROVED:
        raise ValueError(f"Draft {input.draft_id} is already approved")
    
    if draft.status == DraftStatus.REJECTED:
        raise ValueError(f"Draft {input.draft_id} is rejected and cannot be resubmitted without modification")
    
    # Create execution record (STARTED)
    execution = await create_execution_record(
        draft_id=input.draft_id,
        tool_id=tool_id,
        context=context,
    )
    
    try:
        # Update draft status to SUBMITTED
        draft.status = DraftStatus.SUBMITTED
        
        # Complete execution (SUCCEEDED)
        execution = await complete_execution(
            execution_id=execution.execution_id,
            status=ExecutionStatus.SUCCEEDED,
            result_payload={
                "draft_id": input.draft_id,
                "old_status": "draft",
                "new_status": "submitted",
            },
        )
        
        return DocsDraftSubmitOutput(
            execution_id=execution.execution_id,
            draft_id=input.draft_id,
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
def register_docs_draft_submit_for_approval_tool(registry) -> None:
    """Register the docs.cell.draft.submit_for_approval tool."""
    tool = MCPTool(
        id="docs.cell.draft.submit_for_approval",
        name="Submit Document Draft for Approval",
        description="Submits a document draft for approval. Changes draft status from DRAFT to SUBMITTED. Low risk - only changes draft state, no production mutation.",
        layer="cell",
        risk="low",
        domain="docs",
        input_schema=DocsDraftSubmitInput,
        output_schema=DocsDraftSubmitOutput,
        required_role=[],  # Permission checked via draft ownership
        required_scope=[],
        handler=docs_draft_submit_for_approval_handler,
    )
    registry.register(tool)

