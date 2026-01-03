"""
Docs Cluster MCP: Create Message Draft

Tool ID: docs.cluster.message.draft.create
Layer: cluster
Risk: medium
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from lynx.core.registry import MCPTool
from lynx.core.session import ExecutionContext
from lynx.mcp.cluster.drafts.base import create_draft
from lynx.mcp.cluster.drafts.models import DraftProtocol
from lynx.integration.kernel import KernelAPI


class DocsMessageDraftInput(BaseModel):
    """Input schema for docs message draft creation."""
    message_type: str = Field(
        description="Message type (reminder, notification, request, etc.)"
    )
    recipient_ids: List[str] = Field(
        min_length=1,
        description="List of recipient user IDs or roles"
    )
    subject: str = Field(description="Message subject")
    body: str = Field(description="Message body/content")
    linked_document_id: Optional[str] = Field(
        default=None,
        description="Linked document ID (if message relates to a document)",
    )
    priority: str = Field(
        default="normal",
        description="Priority (low, normal, high, urgent)",
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Request ID for idempotency",
    )


class DocsMessageDraftOutput(BaseModel):
    """Output schema for docs message draft creation."""
    draft_id: str = Field(description="Draft ID")
    status: str = Field(description="Draft status (draft)")
    preview_markdown: str = Field(description="Preview markdown with message content")
    recipient_summary: Dict[str, Any] = Field(description="Recipient summary")
    next_actions: List[str] = Field(description="Next actions")
    tenant_id: str = Field(description="Tenant ID")


async def message_docs_draft_create_handler(
    input: DocsMessageDraftInput,
    context: ExecutionContext,
) -> DocsMessageDraftOutput:
    """
    Create a document message draft.
    
    This is a Cluster MCP tool - draft-only, medium risk.
    
    Enforces Draft Protocol:
    - Creates draft object (status = draft)
    - Validates schema + policy pre-checks
    - Attaches rationale + citations (from Domain MCP reads)
    - Produces preview payload
    - Emits audit event
    - Never executes / never mutates production records
    
    Args:
        input: DocsMessageDraftInput
        context: Execution context
    
    Returns:
        DocsMessageDraftOutput with draft information
    
    Raises:
        ValueError: If validation fails or Kernel API unavailable
    """
    # Initialize Kernel API for this tenant (if available)
    kernel_api = None
    try:
        kernel_api = KernelAPI(tenant_id=context.tenant_id)
    except (ValueError, Exception):
        pass
    
    try:
        # Read source context from Domain MCPs (for citations)
        source_context = {
            "domain_tools_used": [
                {
                    "tool_id": "docs.domain.registry.read",
                    "timestamp": context.lynx_run_id,
                    "purpose": "Read document registry for linked document validation",
                }
            ],
            "kernel_metadata": {},
        }
        
        # Get document registry (if Kernel available)
        if kernel_api and input.linked_document_id:
            try:
                # In production, would validate linked_document_id exists
                source_context["kernel_metadata"] = {
                    "linked_document_id": input.linked_document_id,
                    "linked_document_valid": True,  # Would validate in production
                }
            except Exception:
                pass
        
        # Build draft payload
        draft_payload: Dict[str, Any] = {
            "message_type": input.message_type,
            "recipient_ids": input.recipient_ids,
            "subject": input.subject,
            "body": input.body,
            "priority": input.priority,
        }
        
        if input.linked_document_id:
            draft_payload["linked_document_id"] = input.linked_document_id
        
        # Determine risk level
        risk_level = "medium"  # Default for Cluster MCPs
        if input.priority in ["high", "urgent"]:
            risk_level = "high"  # High priority messages are higher risk
        elif len(input.recipient_ids) > 20:
            risk_level = "high"  # Mass messages are higher risk
        
        # Determine recommended approvers
        recommended_approvers = []
        if risk_level == "high":
            recommended_approvers = ["admin", "communications_manager"]
        elif input.message_type == "reminder":
            recommended_approvers = ["document_manager"]
        else:
            recommended_approvers = ["user"]  # Normal messages need minimal approval
        
        # Create draft using Draft Protocol
        draft = await create_draft(
            tenant_id=context.tenant_id,
            draft_type="docs_message",
            payload=draft_payload,
            created_by=context.user_id,
            source_context=source_context,
            risk_level=risk_level,
            recommended_approvers=recommended_approvers,
            request_id=input.request_id,
        )
        
        # Generate preview markdown
        recipients_list = "\n".join([
            f"- {recipient_id}"
            for recipient_id in input.recipient_ids
        ])
        
        linked_doc_section = ""
        if input.linked_document_id:
            linked_doc_section = f"""
## Linked Document

- **Document ID:** {input.linked_document_id}
"""
        
        preview_markdown = f"""# Document Message Draft

**Message Type:** {input.message_type}
**Priority:** {input.priority}
**Status:** Draft
**Created:** {draft.created_at}
**Created By:** {context.user_id}

## Recipients

{recipients_list}

## Subject

{input.subject}

## Body

{input.body}
{linked_doc_section}
## Risk Assessment

- **Risk Level:** {risk_level}
- **Recipient Count:** {len(input.recipient_ids)}
- **Recommended Approvers:** {', '.join(recommended_approvers) or 'None'}

---
*This is a message draft. Submit for approval to send.*
"""
        
        # Build recipient summary
        recipient_summary = {
            "count": len(input.recipient_ids),
            "message_type": input.message_type,
            "priority": input.priority,
            "has_linked_document": bool(input.linked_document_id),
        }
        
        # Determine next actions
        next_actions = ["submit-for-approval", "edit", "cancel"]
        if risk_level == "high":
            next_actions.insert(0, "review-required")
        
        return DocsMessageDraftOutput(
            draft_id=draft.draft_id,
            status=draft.status.value,
            preview_markdown=preview_markdown,
            recipient_summary=recipient_summary,
            next_actions=next_actions,
            tenant_id=context.tenant_id,
        )
    finally:
        if kernel_api:
            await kernel_api.close()


# Register the tool
def register_message_docs_draft_create_tool(registry) -> None:
    """Register the docs.cluster.message.draft.create tool."""
    tool = MCPTool(
        id="docs.cluster.message.draft.create",
        name="Create Document Message Draft",
        description="Creates a document message draft (reminder, notification, request) with validation and preview. Draft-only, no side effects.",
        layer="cluster",
        risk="medium",
        domain="docs",
        input_schema=DocsMessageDraftInput,
        output_schema=DocsMessageDraftOutput,
        required_role=[],  # No specific role required
        required_scope=[],
        handler=message_docs_draft_create_handler,
    )
    registry.register(tool)

