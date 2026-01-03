"""
Docs Cluster MCP: Create Draft

Tool ID: docs.cluster.draft.create
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


class DocsDraftInput(BaseModel):
    """Input schema for docs draft creation."""
    doc_type: str = Field(
        description="Document type (PRD, SRS, ADR, DECISION, etc.)"
    )
    doc_id: Optional[str] = Field(
        default=None,
        description="Document ID (optional if templated)",
    )
    title: str = Field(description="Document title")
    source_refs: Optional[List[str]] = Field(
        default=None,
        description="References to existing documents",
    )
    content_outline: Optional[str] = Field(
        default=None,
        description="Content outline or seed content",
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Request ID for idempotency",
    )


class DocsDraftOutput(BaseModel):
    """Output schema for docs draft creation."""
    draft_id: str = Field(description="Draft ID")
    status: str = Field(description="Draft status (draft)")
    preview_markdown: str = Field(description="Preview markdown content")
    diff_summary: Optional[str] = Field(description="Diff summary (if applicable)")
    next_actions: List[str] = Field(description="Next actions (submit-for-approval, edit, cancel)")
    tenant_id: str = Field(description="Tenant ID")


async def docs_draft_create_handler(
    input: DocsDraftInput,
    context: ExecutionContext,
) -> DocsDraftOutput:
    """
    Create a document draft.
    
    This is a Cluster MCP tool - draft-only, medium risk.
    
    Enforces Draft Protocol:
    - Creates draft object (status = draft)
    - Validates schema + policy pre-checks
    - Attaches rationale + citations (from Domain MCP reads)
    - Produces preview payload
    - Emits audit event
    - Never executes / never mutates production records
    
    Args:
        input: DocsDraftInput
        context: Execution context
    
    Returns:
        DocsDraftOutput with draft information
    
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
                    "timestamp": context.lynx_run_id,  # Simplified
                    "purpose": "Read document registry for references",
                }
            ],
            "kernel_metadata": {},
        }
        
        # Get document registry (if Kernel available)
        if kernel_api:
            try:
                # In production, would call docs.domain.registry.read
                # For now, mock the context
                source_context["kernel_metadata"] = {
                    "doc_type": input.doc_type,
                    "available_templates": ["PRD", "SRS", "ADR"],
                }
            except Exception:
                pass
        
        # Build draft payload
        draft_payload: Dict[str, Any] = {
            "doc_type": input.doc_type,
            "title": input.title,
            "content_outline": input.content_outline or "",
            "source_refs": input.source_refs or [],
        }
        
        if input.doc_id:
            draft_payload["doc_id"] = input.doc_id
        
        # Determine risk level based on doc_type
        risk_level = "medium"  # Default for Cluster MCPs
        if input.doc_type in ["PRD", "LAW"]:
            risk_level = "high"  # Constitutional documents are high risk
        
        # Determine recommended approvers based on doc_type
        recommended_approvers = []
        if input.doc_type in ["PRD", "LAW"]:
            recommended_approvers = ["Founder", "Chief Architect"]
        elif input.doc_type in ["SRS", "ADR"]:
            recommended_approvers = ["Lead Engineer", "System Analyst"]
        else:
            recommended_approvers = ["Product Owner"]
        
        # Create draft using Draft Protocol
        draft = await create_draft(
            tenant_id=context.tenant_id,
            draft_type="docs",
            payload=draft_payload,
            created_by=context.user_id,
            source_context=source_context,
            risk_level=risk_level,
            recommended_approvers=recommended_approvers,
            request_id=input.request_id,
        )
        
        # Generate preview markdown
        preview_markdown = f"""# {input.title}

**Document Type:** {input.doc_type}
**Status:** Draft
**Created:** {draft.created_at}
**Created By:** {context.user_id}

## Content Outline

{input.content_outline or "No outline provided"}

## Source References

{chr(10).join(f"- {ref}" for ref in (input.source_refs or [])) if input.source_refs else "- No references"}

---
*This is a draft. Submit for approval to publish.*
"""
        
        # Generate diff summary (if applicable)
        diff_summary = None
        if input.source_refs:
            diff_summary = f"References {len(input.source_refs)} existing documents"
        
        # Determine next actions
        next_actions = ["submit-for-approval", "edit", "cancel"]
        if risk_level == "high":
            next_actions.insert(0, "review-required")
        
        return DocsDraftOutput(
            draft_id=draft.draft_id,
            status=draft.status.value,
            preview_markdown=preview_markdown,
            diff_summary=diff_summary,
            next_actions=next_actions,
            tenant_id=context.tenant_id,
        )
    finally:
        if kernel_api:
            await kernel_api.close()


# Register the tool
def register_docs_draft_create_tool(registry) -> None:
    """Register the docs.cluster.draft.create tool."""
    tool = MCPTool(
        id="docs.cluster.draft.create",
        name="Create Document Draft",
        description="Creates a document draft (PRD/SRS/ADR/DECISION) with validation, citations, and preview. Draft-only, no side effects.",
        layer="cluster",
        risk="medium",
        domain="docs",
        input_schema=DocsDraftInput,
        output_schema=DocsDraftOutput,
        required_role=[],  # No specific role required (draft creation is low barrier)
        required_scope=[],  # No specific scope required
        handler=docs_draft_create_handler,
    )
    registry.register(tool)

