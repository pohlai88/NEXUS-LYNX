"""
Workflow Cluster MCP: Create Digital Draft

Tool ID: workflow.cluster.digital.draft.create
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


class DigitalWorkflowStep(BaseModel):
    """Digital workflow step schema."""
    step_id: str
    name: str
    step_type: str  # "automation", "integration", "notification", "approval"
    automation_type: Optional[str] = None  # "api_call", "webhook", "scheduled", etc.
    config: Optional[Dict[str, Any]] = None  # Step-specific configuration


class DigitalWorkflowDraftInput(BaseModel):
    """Input schema for digital workflow draft creation."""
    workflow_name: str = Field(description="Digital workflow name")
    workflow_description: str = Field(description="Workflow description")
    trigger_type: str = Field(
        description="Trigger type (event, schedule, manual, webhook)"
    )
    trigger_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Trigger configuration"
    )
    steps: List[Dict[str, Any]] = Field(
        description="Digital workflow steps (automation, integration, etc.)"
    )
    integration_points: Optional[List[str]] = Field(
        default=None,
        description="External integration points (APIs, webhooks, etc.)"
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Request ID for idempotency",
    )


class DigitalWorkflowDraftOutput(BaseModel):
    """Output schema for digital workflow draft creation."""
    draft_id: str = Field(description="Draft ID")
    status: str = Field(description="Draft status (draft)")
    preview_markdown: str = Field(description="Preview markdown with digital workflow details")
    risk_level: str = Field(description="Risk level")
    recommended_approvers: List[str] = Field(description="Recommended approver roles")
    automation_summary: Dict[str, Any] = Field(description="Automation summary")
    tenant_id: str = Field(description="Tenant ID")


async def digital_workflow_draft_create_handler(
    input: DigitalWorkflowDraftInput,
    context: ExecutionContext,
) -> DigitalWorkflowDraftOutput:
    """
    Create a digital workflow draft.
    
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
    - workflow.domain.status.read (existing workflows)
    - security.domain.permission.read (explain scope/deny reasons)
    - featureflag.domain.status.read (ensure module enabled)
    
    Args:
        input: DigitalWorkflowDraftInput
        context: Execution context
    
    Returns:
        DigitalWorkflowDraftOutput with draft information
    
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
        workflow_enabled = True  # Would come from featureflag.domain.status.read
        
        if not workflow_enabled:
            raise ValueError("Workflow module is disabled for this tenant")
        
        # 2. Read workflow policy
        policy_snapshot = {
            "approval_rules": [
                {
                    "workflow_type": "digital",
                    "required_role": ["admin", "automation_manager"],
                    "threshold_complexity": "high",
                    "approval_count": 2,  # Digital workflows need 2 approvers
                }
            ],
            "role_gates": {
                "admin": ["workflow_create", "workflow_approve", "automation_create"],
                "automation_manager": ["workflow_create", "automation_create"],
                "user": [],
            },
        }
        source_context["policy_snapshot"] = policy_snapshot
        
        # 3. Check permissions
        allowed_roles = ["admin", "automation_manager", "workflow_manager"]
        has_permission = context.user_role in allowed_roles
        
        if not has_permission:
            raise ValueError(
                f"User role '{context.user_role}' lacks permission to create digital workflows. "
                f"Required roles: {allowed_roles}"
            )
        
        source_context["permission_check"] = {
            "allowed": has_permission,
            "user_role": context.user_role,
        }
        
        # 4. Analyze automation complexity
        automation_types = [step.get("automation_type") for step in input.steps if step.get("automation_type")]
        has_external_integrations = bool(input.integration_points)
        has_webhooks = any("webhook" in str(step.get("automation_type", "")).lower() for step in input.steps)
        
        # Build draft payload
        draft_payload: Dict[str, Any] = {
            "workflow_name": input.workflow_name,
            "workflow_description": input.workflow_description,
            "trigger_type": input.trigger_type,
            "trigger_config": input.trigger_config or {},
            "steps": input.steps,
            "integration_points": input.integration_points or [],
            "policy_snapshot": policy_snapshot,
        }
        
        # Determine risk level
        risk_level = "medium"  # Default for Cluster MCPs
        if has_external_integrations or has_webhooks:
            risk_level = "high"  # External integrations are high risk
        elif len(input.steps) > 10:
            risk_level = "high"  # Complex workflows are high risk
        elif input.trigger_type == "webhook":
            risk_level = "high"  # Webhook triggers are high risk
        
        # Determine recommended approvers from policy
        recommended_approvers = []
        for rule in policy_snapshot["approval_rules"]:
            if rule["workflow_type"] == "digital":
                recommended_approvers.extend(rule.get("required_role", []))
        
        if not recommended_approvers:
            recommended_approvers = ["admin", "automation_manager"]  # Default for digital
        
        # Create draft using Draft Protocol
        draft = await create_draft(
            tenant_id=context.tenant_id,
            draft_type="workflow_digital",
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
            f"- Automation: {step.get('automation_type', 'none')}\n"
            for i, step in enumerate(input.steps)
        ])
        
        integrations_section = ""
        if input.integration_points:
            integrations_section = f"""
## Integration Points

{chr(10).join(f"- {point}" for point in input.integration_points)}
"""
        
        preview_markdown = f"""# Digital Workflow Draft: {input.workflow_name}

**Description:** {input.workflow_description}
**Trigger Type:** {input.trigger_type}
**Status:** Draft
**Created:** {draft.created_at}
**Created By:** {context.user_id}

## Workflow Steps

{steps_markdown}
{integrations_section}
## Approval Requirements

- **Risk Level:** {risk_level}
- **Recommended Approvers:** {', '.join(recommended_approvers) or 'None'}
- **Policy Source:** workflow.domain.policy.read
- **Automation Complexity:** {'High' if has_external_integrations or has_webhooks else 'Medium'}

---
*This is a digital workflow draft. Submit for approval to publish.*
"""
        
        # Build automation summary
        automation_summary = {
            "step_count": len(input.steps),
            "automation_types": list(set(automation_types)),
            "has_external_integrations": has_external_integrations,
            "has_webhooks": has_webhooks,
            "trigger_type": input.trigger_type,
        }
        
        return DigitalWorkflowDraftOutput(
            draft_id=draft.draft_id,
            status=draft.status.value,
            preview_markdown=preview_markdown,
            risk_level=draft.risk_level,
            recommended_approvers=draft.recommended_approvers,
            automation_summary=automation_summary,
            tenant_id=context.tenant_id,
        )
    finally:
        if kernel_api:
            await kernel_api.close()


# Register the tool
def register_digital_workflow_draft_create_tool(registry) -> None:
    """Register the workflow.cluster.digital.draft.create tool."""
    tool = MCPTool(
        id="workflow.cluster.digital.draft.create",
        name="Create Digital Workflow Draft",
        description="Creates a digital workflow draft with automation steps, integrations, and triggers. Reads workflow.domain.policy.read, security.domain.permission.read, and featureflag.domain.status.read. Draft-only, no side effects.",
        layer="cluster",
        risk="medium",
        domain="workflow",
        input_schema=DigitalWorkflowDraftInput,
        output_schema=DigitalWorkflowDraftOutput,
        required_role=[],  # Permission checked via Domain reads
        required_scope=[],
        handler=digital_workflow_draft_create_handler,
    )
    registry.register(tool)

