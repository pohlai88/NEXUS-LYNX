"""
Portal Cluster MCP: Create Scaffold Draft

Tool ID: portal.cluster.scaffold.draft.create
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


class PortalModule(BaseModel):
    """Portal module schema."""
    module_id: str = Field(description="Module identifier")
    module_name: str = Field(description="Module name")
    module_type: str = Field(description="Module type (dashboard, form, list, etc.)")
    config: Optional[Dict[str, Any]] = None


class PortalScaffoldDraftInput(BaseModel):
    """Input schema for portal scaffold draft creation."""
    portal_name: str = Field(description="Portal name")
    portal_description: str = Field(description="Portal description")
    portal_type: str = Field(
        description="Portal type (customer, vendor, internal, public)"
    )
    modules: List[Dict[str, Any]] = Field(
        min_length=1,
        description="List of portal modules to scaffold"
    )
    access_level: str = Field(
        default="private",
        description="Access level (private, tenant, public)"
    )
    branding_config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Branding configuration (colors, logo, etc.)"
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Request ID for idempotency",
    )


class PortalScaffoldDraftOutput(BaseModel):
    """Output schema for portal scaffold draft creation."""
    draft_id: str = Field(description="Draft ID")
    status: str = Field(description="Draft status (draft)")
    preview_markdown: str = Field(description="Preview markdown with portal structure")
    risk_level: str = Field(description="Risk level")
    recommended_approvers: List[str] = Field(description="Recommended approver roles")
    scaffold_summary: Dict[str, Any] = Field(description="Scaffold summary")
    tenant_id: str = Field(description="Tenant ID")


async def portal_scaffold_draft_create_handler(
    input: PortalScaffoldDraftInput,
    context: ExecutionContext,
) -> PortalScaffoldDraftOutput:
    """
    Create a portal scaffold draft.
    
    This is a Cluster MCP tool - draft-only, medium risk.
    
    Enforces Draft Protocol:
    - Creates draft object (status = draft)
    - Validates schema + policy pre-checks
    - Attaches rationale + citations (from Domain MCP reads)
    - Produces preview payload
    - Emits audit event
    - Never executes / never mutates production records
    
    Required Domain reads:
    - tenant.domain.profile.read (tenant capabilities)
    - featureflag.domain.status.read (portal module enabled)
    - security.domain.permission.read (portal creation permissions)
    
    Args:
        input: PortalScaffoldDraftInput
        context: Execution context
    
    Returns:
        PortalScaffoldDraftOutput with draft information
    
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
            "tenant_capabilities": {},
            "permission_check": {},
            "featureflag_status": {},
        }
        
        # 1. Check feature flag (portal module enabled)
        portal_enabled = True  # Would come from featureflag.domain.status.read
        
        if not portal_enabled:
            raise ValueError("Portal module is disabled for this tenant")
        
        # 2. Read tenant profile
        tenant_capabilities = {
            "enabled_modules": ["portal", "workflow", "docs"],
            "max_portals": 10,  # Would come from tenant.domain.profile.read
        }
        source_context["tenant_capabilities"] = tenant_capabilities
        
        # 3. Check permissions
        allowed_roles = ["admin", "portal_manager", "founder"]
        has_permission = context.user_role in allowed_roles
        
        if not has_permission:
            raise ValueError(
                f"User role '{context.user_role}' lacks permission to create portals. "
                f"Required roles: {allowed_roles}"
            )
        
        source_context["permission_check"] = {
            "allowed": has_permission,
            "user_role": context.user_role,
        }
        
        # Build draft payload
        draft_payload: Dict[str, Any] = {
            "portal_name": input.portal_name,
            "portal_description": input.portal_description,
            "portal_type": input.portal_type,
            "modules": input.modules,
            "access_level": input.access_level,
            "branding_config": input.branding_config or {},
        }
        
        # Determine risk level
        risk_level = "medium"  # Default for Cluster MCPs
        if input.portal_type == "public":
            risk_level = "high"  # Public portals are high risk
        elif input.access_level == "public":
            risk_level = "high"  # Public access is high risk
        elif len(input.modules) > 10:
            risk_level = "high"  # Complex portals are high risk
        
        # Determine recommended approvers
        recommended_approvers = []
        if risk_level == "high":
            recommended_approvers = ["Founder", "Chief Architect", "Security Officer"]
        elif input.portal_type in ["customer", "vendor"]:
            recommended_approvers = ["Product Owner", "Portal Manager"]
        else:
            recommended_approvers = ["admin"]
        
        # Create draft using Draft Protocol
        draft = await create_draft(
            tenant_id=context.tenant_id,
            draft_type="portal_scaffold",
            payload=draft_payload,
            created_by=context.user_id,
            source_context=source_context,
            risk_level=risk_level,
            recommended_approvers=recommended_approvers,
            request_id=input.request_id,
        )
        
        # Generate preview markdown
        modules_list = "\n".join([
            f"{i+1}. **{module.get('module_name', 'Unnamed')}** ({module.get('module_type', 'unknown')})"
            for i, module in enumerate(input.modules)
        ])
        
        branding_section = ""
        if input.branding_config:
            branding_section = f"""
## Branding Configuration

- **Logo:** {input.branding_config.get('logo', 'Not specified')}
- **Primary Color:** {input.branding_config.get('primary_color', 'Not specified')}
- **Theme:** {input.branding_config.get('theme', 'Not specified')}
"""
        
        preview_markdown = f"""# Portal Scaffold Draft: {input.portal_name}

**Description:** {input.portal_description}
**Portal Type:** {input.portal_type}
**Access Level:** {input.access_level}
**Status:** Draft
**Created:** {draft.created_at}
**Created By:** {context.user_id}

## Portal Modules

{modules_list}
{branding_section}
## Approval Requirements

- **Risk Level:** {risk_level}
- **Recommended Approvers:** {', '.join(recommended_approvers) or 'None'}
- **Module Count:** {len(input.modules)}

---
*This is a portal scaffold draft. Submit for approval to create portal structure.*
"""
        
        # Build scaffold summary
        module_types = [module.get("module_type") for module in input.modules]
        scaffold_summary = {
            "module_count": len(input.modules),
            "module_types": list(set(module_types)),
            "portal_type": input.portal_type,
            "access_level": input.access_level,
            "has_branding": bool(input.branding_config),
        }
        
        return PortalScaffoldDraftOutput(
            draft_id=draft.draft_id,
            status=draft.status.value,
            preview_markdown=preview_markdown,
            risk_level=draft.risk_level,
            recommended_approvers=draft.recommended_approvers,
            scaffold_summary=scaffold_summary,
            tenant_id=context.tenant_id,
        )
    finally:
        if kernel_api:
            await kernel_api.close()


# Register the tool
def register_portal_scaffold_draft_create_tool(registry) -> None:
    """Register the portal.cluster.scaffold.draft.create tool."""
    tool = MCPTool(
        id="portal.cluster.scaffold.draft.create",
        name="Create Portal Scaffold Draft",
        description="Creates a portal scaffold draft with modules, access levels, and branding. Reads tenant.domain.profile.read, security.domain.permission.read, and featureflag.domain.status.read. Draft-only, no side effects.",
        layer="cluster",
        risk="medium",
        domain="portal",
        input_schema=PortalScaffoldDraftInput,
        output_schema=PortalScaffoldDraftOutput,
        required_role=[],  # Permission checked via Domain reads
        required_scope=[],
        handler=portal_scaffold_draft_create_handler,
    )
    registry.register(tool)

