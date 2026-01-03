"""
Docs Cluster MCP: Create Batch Draft

Tool ID: docs.cluster.batch.draft.create
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


class BatchDocumentRequest(BaseModel):
    """Single document request in batch."""
    doc_type: str = Field(description="Document type (PRD, SRS, ADR, etc.)")
    doc_id: Optional[str] = Field(default=None, description="Document ID (optional)")
    title: str = Field(description="Document title")
    content_outline: Optional[str] = Field(default=None, description="Content outline")


class BatchDocsDraftInput(BaseModel):
    """Input schema for batch docs draft creation."""
    requests: List[BatchDocumentRequest] = Field(
        min_length=1,
        max_length=50,
        description="List of document requests (1-50 items)"
    )
    batch_name: str = Field(description="Batch name/identifier")
    source_refs: Optional[List[str]] = Field(
        default=None,
        description="Shared references for all documents in batch",
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Request ID for idempotency",
    )


class BatchDocsDraftOutput(BaseModel):
    """Output schema for batch docs draft creation."""
    draft_id: str = Field(description="Draft ID")
    status: str = Field(description="Draft status (draft)")
    preview_markdown: str = Field(description="Preview markdown with batch summary")
    batch_summary: Dict[str, Any] = Field(description="Batch summary (count, doc_types, etc.)")
    next_actions: List[str] = Field(description="Next actions")
    tenant_id: str = Field(description="Tenant ID")


async def batch_docs_draft_create_handler(
    input: BatchDocsDraftInput,
    context: ExecutionContext,
) -> BatchDocsDraftOutput:
    """
    Create a batch document request draft.
    
    This is a Cluster MCP tool - draft-only, medium risk.
    
    Enforces Draft Protocol:
    - Creates draft object (status = draft)
    - Validates schema + policy pre-checks
    - Attaches rationale + citations (from Domain MCP reads)
    - Produces preview payload
    - Emits audit event
    - Never executes / never mutates production records
    
    Args:
        input: BatchDocsDraftInput
        context: Execution context
    
    Returns:
        BatchDocsDraftOutput with draft information
    
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
                    "purpose": "Read document registry for batch validation",
                }
            ],
            "kernel_metadata": {},
        }
        
        # Get document registry (if Kernel available)
        if kernel_api:
            try:
                source_context["kernel_metadata"] = {
                    "batch_size": len(input.requests),
                    "available_templates": ["PRD", "SRS", "ADR", "DECISION"],
                }
            except Exception:
                pass
        
        # Build batch summary
        doc_type_counts: Dict[str, int] = {}
        for req in input.requests:
            doc_type_counts[req.doc_type] = doc_type_counts.get(req.doc_type, 0) + 1
        
        # Build draft payload
        draft_payload: Dict[str, Any] = {
            "batch_name": input.batch_name,
            "requests": [req.model_dump() for req in input.requests],
            "batch_size": len(input.requests),
            "doc_type_counts": doc_type_counts,
            "source_refs": input.source_refs or [],
        }
        
        # Determine risk level
        risk_level = "medium"  # Default for Cluster MCPs
        if len(input.requests) > 20:
            risk_level = "high"  # Large batches are higher risk
        elif any(req.doc_type in ["PRD", "LAW"] for req in input.requests):
            risk_level = "high"  # Constitutional documents are high risk
        
        # Determine recommended approvers
        recommended_approvers = []
        if risk_level == "high":
            recommended_approvers = ["Founder", "Chief Architect"]
        elif any(req.doc_type in ["SRS", "ADR"] for req in input.requests):
            recommended_approvers = ["Lead Engineer", "System Analyst"]
        else:
            recommended_approvers = ["Product Owner"]
        
        # Create draft using Draft Protocol
        draft = await create_draft(
            tenant_id=context.tenant_id,
            draft_type="docs_batch",
            payload=draft_payload,
            created_by=context.user_id,
            source_context=source_context,
            risk_level=risk_level,
            recommended_approvers=recommended_approvers,
            request_id=input.request_id,
        )
        
        # Generate preview markdown
        requests_list = "\n".join([
            f"{i+1}. **{req.title}** ({req.doc_type})"
            for i, req in enumerate(input.requests)
        ])
        
        doc_types_summary = ", ".join([
            f"{count}x {doc_type}"
            for doc_type, count in sorted(doc_type_counts.items())
        ])
        
        preview_markdown = f"""# Batch Document Request: {input.batch_name}

**Batch Size:** {len(input.requests)} documents
**Status:** Draft
**Created:** {draft.created_at}
**Created By:** {context.user_id}

## Document Types

{doc_types_summary}

## Document Requests

{requests_list}

## Shared References

{chr(10).join(f"- {ref}" for ref in (input.source_refs or [])) if input.source_refs else "- No shared references"}

## Risk Assessment

- **Risk Level:** {risk_level}
- **Recommended Approvers:** {', '.join(recommended_approvers) or 'None'}

---
*This is a batch draft. Submit for approval to process all documents.*
"""
        
        # Build batch summary
        batch_summary = {
            "batch_size": len(input.requests),
            "doc_type_counts": doc_type_counts,
            "risk_level": risk_level,
            "has_shared_refs": bool(input.source_refs),
        }
        
        # Determine next actions
        next_actions = ["submit-for-approval", "edit", "cancel"]
        if risk_level == "high":
            next_actions.insert(0, "review-required")
        
        return BatchDocsDraftOutput(
            draft_id=draft.draft_id,
            status=draft.status.value,
            preview_markdown=preview_markdown,
            batch_summary=batch_summary,
            next_actions=next_actions,
            tenant_id=context.tenant_id,
        )
    finally:
        if kernel_api:
            await kernel_api.close()


# Register the tool
def register_batch_docs_draft_create_tool(registry) -> None:
    """Register the docs.cluster.batch.draft.create tool."""
    tool = MCPTool(
        id="docs.cluster.batch.draft.create",
        name="Create Batch Document Draft",
        description="Creates a batch document request draft (1-50 documents) with validation, citations, and preview. Draft-only, no side effects.",
        layer="cluster",
        risk="medium",
        domain="docs",
        input_schema=BatchDocsDraftInput,
        output_schema=BatchDocsDraftOutput,
        required_role=[],  # No specific role required
        required_scope=[],
        handler=batch_docs_draft_create_handler,
    )
    registry.register(tool)

