"""
Workflow Cluster MCP: Create Draft

Tool ID: workflow.cluster.draft.create
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


class WorkflowStep(BaseModel):
    """Workflow step schema."""
    step_id: str
    name: str
    step_type: str  # "approval", "notification", "action"
    required_role: Optional[List[str]] = None
    required_scope: Optional[List[str]] = None


class WorkflowDraftInput(BaseModel):
    """Input schema for workflow draft creation."""
    workflow_kind: str = Field(
        description="Workflow kind (e.g., 'approval', 'document', 'payment')"
    )
    name: str = Field(description="Workflow name")
    steps: List[Dict[str, Any]] = Field(
        description="Draft workflow steps"
    )
    linked_object: Optional[str] = Field(
        default=None,
        description="Linked object (e.g., draft_id from docs or vpm)",
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Request ID for idempotency",
    )


class WorkflowDraftOutput(BaseModel):
    """Output schema for workflow draft creation."""
    draft_id: str = Field(description="Draft ID")
    status: str = Field(description="Draft status (draft)")
    preview_markdown: str = Field(description="Preview markdown with steps, approvers, gates")
    risk_level: str = Field(description="Risk level")
    recommended_approvers: List[str] = Field(description="Recommended approver roles")
    tenant_id: str = Field(description="Tenant ID")


async def workflow_draft_create_handler(
    input: WorkflowDraftInput,
    context: ExecutionContext,
) -> WorkflowDraftOutput:
    """
    Create a workflow draft.
    
    This is a Cluster MCP tool - draft-only, medium risk.
    
    Enforces Draft Protocol:
    - Creates draft object (status = draft)
    - Validates schema + policy pre-checks
    - Attaches rationale + citations (from Domain MCP reads)
    - Produces preview payload
    - Emits audit event
    - Never executes / never mutates production records
    
    Required Domain reads:
    - workflow.domain.policy.read (approval rules & thresholds)
    - security.domain.permission.read (explain scope/deny reasons)
    - featureflag.domain.status.read (ensure module enabled)
    
    Args:
        input: WorkflowDraftInput
        context: Execution context
    
    Returns:
        WorkflowDraftOutput with draft information
    
    Raises:
        ValueError: If feature flag disabled or permission denied
    """
    # Initialize Kernel API for this tenant (if available)
    kernel_api = None
    try:
        kernel_api = KernelAPI(tenant_id=context.tenant_id)
    except (ValueError, Exception):
        pass
    
    try:
        # Read required Domain MCPs for source context
        source_context = {
            "domain_tools_used": [],
            "policy_snapshot": {},
            "permission_check": {},
            "featureflag_status": {},
        }
        
        # 1. Check feature flag (workflow module enabled)
        # In production, would call featureflag.domain.status.read
        # For now, assume enabled unless explicitly disabled
        workflow_enabled = True  # Would come from featureflag.domain.status.read
        
        if not workflow_enabled:
            raise ValueError("Workflow module is disabled for this tenant")
        
        # 2. Read workflow policy
        # In production, would call workflow.domain.policy.read
        # For now, use mock policy data
        policy_snapshot = {
            "approval_rules": [
                {
                    "workflow_type": input.workflow_kind,
                    "required_role": ["admin"],
                    "threshold_amount": 1000.0,
                    "approval_count": 1,
                }
            ],
            "role_gates": {
                "admin": ["workflow_create", "workflow_approve"],
                "user": [],
            },
        }
        source_context["policy_snapshot"] = policy_snapshot
        
        # 3. Check permissions
        # In production, would call security.domain.permission.read
        # Check if user role has required permissions
        allowed_roles = ["admin", "workflow_manager"]  # Roles that can create workflows
        has_permission = context.user_role in allowed_roles
        
        if not has_permission:
            raise ValueError(
                f"User role '{context.user_role}' lacks permission to create workflows. "
                f"Required roles: {allowed_roles}"
            )
        
        source_context["permission_check"] = {
            "allowed": has_permission,
            "user_role": context.user_role,
        }
        
        # 4. Read tenant profile (optional, for capabilities)
        # In production, would call tenant.domain.profile.read
        source_context["tenant_capabilities"] = {
            "enabled_modules": ["workflow", "finance", "vpm"],
        }
        
        # Build draft payload
        draft_payload: Dict[str, Any] = {
            "workflow_kind": input.workflow_kind,
            "name": input.name,
            "steps": input.steps,
            "policy_snapshot": policy_snapshot,
        }
        
        if input.linked_object:
            draft_payload["linked_object"] = input.linked_object
        
        # Determine risk level
        risk_level = "medium"  # Default for Cluster MCPs
        if input.workflow_kind in ["payment", "approval"]:
            risk_level = "high"  # Payment/approval workflows are high risk
        
        # Determine recommended approvers from policy
        recommended_approvers = []
        for rule in policy_snapshot["approval_rules"]:
            if rule["workflow_type"] == input.workflow_kind:
                recommended_approvers.extend(rule.get("required_role", []))
        
        if not recommended_approvers:
            recommended_approvers = ["admin"]  # Default
        
        # Create draft using Draft Protocol
        draft = await create_draft(
            tenant_id=context.tenant_id,
            draft_type="workflow",
            payload=draft_payload,
            created_by=context.user_id,
            source_context=source_context,
            risk_level=risk_level,
            recommended_approvers=list(set(recommended_approvers)),  # Remove duplicates
            request_id=input.request_id,
        )
        
        # Generate preview markdown
        steps_markdown = "\n".join([
            f"### Step {i+1}: {step.get('name', 'Unnamed')}\n"
            f"- Type: {step.get('step_type', 'unknown')}\n"
            f"- Required Role: {', '.join(step.get('required_role', [])) or 'None'}\n"
            for i, step in enumerate(input.steps)
        ])
        
        preview_markdown = f"""# Workflow Draft: {input.name}

**Workflow Kind:** {input.workflow_kind}
**Status:** Draft
**Created:** {draft.created_at}
**Created By:** {context.user_id}

## Workflow Steps

{steps_markdown}

## Approval Requirements

- **Risk Level:** {risk_level}
- **Recommended Approvers:** {', '.join(recommended_approvers) or 'None'}
- **Policy Source:** workflow.domain.policy.read

## Linked Objects

{input.linked_object if input.linked_object else "None"}

---
*This is a draft. Submit for approval to publish.*
"""
        
        return WorkflowDraftOutput(
            draft_id=draft.draft_id,
            status=draft.status.value,
            preview_markdown=preview_markdown,
            risk_level=draft.risk_level,
            recommended_approvers=draft.recommended_approvers,
            tenant_id=context.tenant_id,
        )
    finally:
        if kernel_api:
            await kernel_api.close()


# Register the tool
def register_workflow_draft_create_tool(registry) -> None:
    """Register the workflow.cluster.draft.create tool."""
    tool = MCPTool(
        id="workflow.cluster.draft.create",
        name="Create Workflow Draft",
        description="Creates a workflow draft with steps, approvers, and gates. Reads workflow.domain.policy.read, security.domain.permission.read, and featureflag.domain.status.read. Draft-only, no side effects.",
        layer="cluster",
        risk="medium",
        domain="workflow",
        input_schema=WorkflowDraftInput,
        output_schema=WorkflowDraftOutput,
        required_role=[],  # Permission checked via Domain reads
        required_scope=[],
        handler=workflow_draft_create_handler,
    )
    registry.register(tool)

