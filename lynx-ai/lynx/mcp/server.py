"""
MCP Server for Lynx AI.

This module sets up the MCP server that exposes Lynx MCP tools.
Following PRD-LYNX-003 requirements and mcp-agent best practices.
"""

from lynx.core.registry import MCPToolRegistry

# Domain MCPs
from lynx.mcp.domain.finance.health_read import register_finance_health_read_tool
from lynx.mcp.domain.kernel.registry_read import register_kernel_registry_read_tool
from lynx.mcp.domain.tenant.profile_read import register_tenant_profile_read_tool
from lynx.mcp.domain.audit.run_read import register_audit_run_read_tool
from lynx.mcp.domain.security.permission_read import register_security_permission_read_tool
from lynx.mcp.domain.workflow.status_read import register_workflow_status_read_tool
from lynx.mcp.domain.workflow.policy_read import register_workflow_policy_read_tool
from lynx.mcp.domain.docs.registry_read import register_docs_registry_read_tool
from lynx.mcp.domain.featureflag.status_read import register_featureflag_status_read_tool
from lynx.mcp.domain.system.health_read import register_system_health_read_tool
from lynx.mcp.domain.vpm.vendor_read import register_vpm_vendor_read_tool
from lynx.mcp.domain.vpm.payment_status_read import register_vpm_payment_status_read_tool

# Cluster MCPs
from lynx.mcp.cluster.docs.draft_create import register_docs_draft_create_tool
from lynx.mcp.cluster.docs.batch_draft_create import register_batch_docs_draft_create_tool
from lynx.mcp.cluster.docs.message_draft_create import register_message_docs_draft_create_tool
from lynx.mcp.cluster.workflow.draft_create import register_workflow_draft_create_tool
from lynx.mcp.cluster.workflow.digital_draft_create import register_digital_workflow_draft_create_tool
from lynx.mcp.cluster.vpm.payment_draft_create import register_vpm_payment_draft_create_tool
from lynx.mcp.cluster.portal.scaffold_draft_create import register_portal_scaffold_draft_create_tool
from lynx.mcp.cluster.portal.config_draft_create import register_portal_config_draft_create_tool

# Cell MCPs
from lynx.mcp.cell.docs.draft_submit_for_approval import register_docs_draft_submit_for_approval_tool
from lynx.mcp.cell.workflow.draft_publish import register_workflow_draft_publish_tool
from lynx.mcp.cell.vpm.payment_execute import register_vpm_payment_execute_tool


def initialize_mcp_server(registry: MCPToolRegistry) -> None:
    """
    Initialize MCP server with all registered tools.
    
    Args:
        registry: MCP tool registry
    """
    # Register Domain MCPs
    register_finance_health_read_tool(registry)
    register_kernel_registry_read_tool(registry)
    register_tenant_profile_read_tool(registry)
    register_audit_run_read_tool(registry)
    register_security_permission_read_tool(registry)
    register_workflow_status_read_tool(registry)
    register_workflow_policy_read_tool(registry)
    register_docs_registry_read_tool(registry)
    register_featureflag_status_read_tool(registry)
    register_system_health_read_tool(registry)
    register_vpm_vendor_read_tool(registry)
    register_vpm_payment_status_read_tool(registry)
    
    # Register Cluster MCPs
    register_docs_draft_create_tool(registry)
    register_batch_docs_draft_create_tool(registry)
    register_message_docs_draft_create_tool(registry)
    register_workflow_draft_create_tool(registry)
    register_digital_workflow_draft_create_tool(registry)
    register_vpm_payment_draft_create_tool(registry)
    register_portal_scaffold_draft_create_tool(registry)
    register_portal_config_draft_create_tool(registry)
    
    # Register Cell MCPs
    register_docs_draft_submit_for_approval_tool(registry)
    register_workflow_draft_publish_tool(registry)
    register_vpm_payment_execute_tool(registry)
    
    # All Cluster MCPs registered (8 tools total)
    # TODO: Register more Cell MCPs (if needed)
    
    print(f"[OK] MCP Server initialized with {len(registry.list_all())} tools")

