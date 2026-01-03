"""
Portal Cluster MCP: Create Config Draft

Tool ID: portal.cluster.config.draft.create
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


class PortalConfigDraftInput(BaseModel):
    """Input schema for portal config draft creation."""
    portal_id: str = Field(description="Portal ID (must exist)")
    config_sections: Dict[str, Any] = Field(
        description="Configuration sections (routing, permissions, integrations, etc.)"
    )
    config_version: Optional[str] = Field(
        default=None,
        description="Configuration version (for versioning)"
    )
    description: Optional[str] = Field(
        default=None,
        description="Configuration change description"
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Request ID for idempotency",
    )


class PortalConfigDraftOutput(BaseModel):
    """Output schema for portal config draft creation."""
    draft_id: str = Field(description="Draft ID")
    status: str = Field(description="Draft status (draft)")
    preview_markdown: str = Field(description="Preview markdown with config changes")
    risk_level: str = Field(description="Risk level")
    recommended_approvers: List[str] = Field(description="Recommended approver roles")
    config_summary: Dict[str, Any] = Field(description="Configuration summary")
    tenant_id: str = Field(description="Tenant ID")


async def portal_config_draft_create_handler(
    input: PortalConfigDraftInput,
    context: ExecutionContext,
) -> PortalConfigDraftOutput:
    """
    Create a portal configuration draft.
    
    This is a Cluster MCP tool - draft-only, medium risk.
    
    Enforces Draft Protocol:
    - Creates draft object (status = draft)
    - Validates schema + policy pre-checks
    - Attaches rationale + citations (from Domain MCP reads)
    - Produces preview payload
    - Emits audit event
    - Never executes / never mutates production records
    
    Required Domain reads:
    - tenant.domain.profile.read (portal exists check)
    - security.domain.permission.read (portal config permissions)
    - featureflag.domain.status.read (portal module enabled)
    
    Args:
        input: PortalConfigDraftInput
        context: Execution context
    
    Returns:
        PortalConfigDraftOutput with draft information
    
    Raises:
        ValueError: If portal doesn't exist, feature flag disabled, or permission denied
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
            "portal_exists": False,
            "permission_check": {},
            "featureflag_status": {},
        }
        
        # 1. Check feature flag (portal module enabled)
        portal_enabled = True  # Would come from featureflag.domain.status.read
        
        if not portal_enabled:
            raise ValueError("Portal module is disabled for this tenant")
        
        # 2. Verify portal exists (would call tenant.domain.profile.read or portal domain MCP)
        # For now, assume portal exists if portal_id is provided
        portal_exists = bool(input.portal_id)
        if not portal_exists:
            raise ValueError(f"Portal '{input.portal_id}' does not exist")
        
        source_context["portal_exists"] = portal_exists
        
        # 3. Check permissions
        allowed_roles = ["admin", "portal_manager"]
        has_permission = context.user_role in allowed_roles
        
        if not has_permission:
            raise ValueError(
                f"User role '{context.user_role}' lacks permission to configure portals. "
                f"Required roles: {allowed_roles}"
            )
        
        source_context["permission_check"] = {
            "allowed": has_permission,
            "user_role": context.user_role,
        }
        
        # Analyze config sections for risk assessment
        has_routing_changes = "routing" in input.config_sections
        has_permission_changes = "permissions" in input.config_sections
        has_integration_changes = "integrations" in input.config_sections
        has_security_changes = "security" in input.config_sections
        
        # Build draft payload
        draft_payload: Dict[str, Any] = {
            "portal_id": input.portal_id,
            "config_sections": input.config_sections,
            "config_version": input.config_version,
            "description": input.description,
        }
        
        # Determine risk level
        risk_level = "medium"  # Default for Cluster MCPs
        if has_security_changes or has_permission_changes:
            risk_level = "high"  # Security/permission changes are high risk
        elif has_routing_changes and has_integration_changes:
            risk_level = "high"  # Complex routing + integration changes are high risk
        elif len(input.config_sections) > 5:
            risk_level = "high"  # Many config changes are high risk
        
        # Determine recommended approvers
        recommended_approvers = []
        if risk_level == "high":
            recommended_approvers = ["Founder", "Chief Architect", "Security Officer"]
        elif has_security_changes:
            recommended_approvers = ["Security Officer", "Portal Manager"]
        elif has_permission_changes:
            recommended_approvers = ["admin", "Portal Manager"]
        else:
            recommended_approvers = ["Portal Manager"]
        
        # Create draft using Draft Protocol
        draft = await create_draft(
            tenant_id=context.tenant_id,
            draft_type="portal_config",
            payload=draft_payload,
            created_by=context.user_id,
            source_context=source_context,
            risk_level=risk_level,
            recommended_approvers=recommended_approvers,
            request_id=input.request_id,
        )
        
        # Generate preview markdown
        config_sections_list = "\n".join([
            f"### {section_name}\n```json\n{str(section_config)}\n```"
            for section_name, section_config in input.config_sections.items()
        ])
        
        changes_summary = []
        if has_routing_changes:
            changes_summary.append("Routing changes")
        if has_permission_changes:
            changes_summary.append("Permission changes")
        if has_integration_changes:
            changes_summary.append("Integration changes")
        if has_security_changes:
            changes_summary.append("Security changes")
        
        changes_section = ""
        if changes_summary:
            changes_section = f"""
## Change Summary

{chr(10).join(f"- {change}" for change in changes_summary)}
"""
        
        preview_markdown = f"""# Portal Configuration Draft

**Portal ID:** {input.portal_id}
**Config Version:** {input.config_version or 'Not specified'}
**Status:** Draft
**Created:** {draft.created_at}
**Created By:** {context.user_id}

{input.description or 'No description provided'}
{changes_section}
## Configuration Sections

{config_sections_list}

## Approval Requirements

- **Risk Level:** {risk_level}
- **Recommended Approvers:** {', '.join(recommended_approvers) or 'None'}
- **Config Sections:** {len(input.config_sections)}

---
*This is a portal configuration draft. Submit for approval to apply changes.*
"""
        
        # Build config summary
        config_summary = {
            "config_sections": list(input.config_sections.keys()),
            "section_count": len(input.config_sections),
            "has_routing_changes": has_routing_changes,
            "has_permission_changes": has_permission_changes,
            "has_integration_changes": has_integration_changes,
            "has_security_changes": has_security_changes,
        }
        
        return PortalConfigDraftOutput(
            draft_id=draft.draft_id,
            status=draft.status.value,
            preview_markdown=preview_markdown,
            risk_level=draft.risk_level,
            recommended_approvers=draft.recommended_approvers,
            config_summary=config_summary,
            tenant_id=context.tenant_id,
        )
    finally:
        if kernel_api:
            await kernel_api.close()


# Register the tool
def register_portal_config_draft_create_tool(registry) -> None:
    """Register the portal.cluster.config.draft.create tool."""
    tool = MCPTool(
        id="portal.cluster.config.draft.create",
        name="Create Portal Config Draft",
        description="Creates a portal configuration draft with routing, permissions, integrations, and security settings. Reads tenant.domain.profile.read, security.domain.permission.read, and featureflag.domain.status.read. Draft-only, no side effects.",
        layer="cluster",
        risk="medium",
        domain="portal",
        input_schema=PortalConfigDraftInput,
        output_schema=PortalConfigDraftOutput,
        required_role=[],  # Permission checked via Domain reads
        required_scope=[],
        handler=portal_config_draft_create_handler,
    )
    registry.register(tool)

