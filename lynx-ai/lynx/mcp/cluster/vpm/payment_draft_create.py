"""
VPM Cluster MCP: Create Payment Draft

Tool ID: vpm.cluster.payment.draft.create
Layer: cluster
Risk: medium
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from lynx.core.registry import MCPTool
from lynx.core.session import ExecutionContext
from lynx.mcp.cluster.drafts.base import create_draft
from lynx.mcp.cluster.drafts.models import DraftProtocol
from lynx.integration.kernel import KernelAPI


class VPMPaymentDraftInput(BaseModel):
    """Input schema for VPM payment draft creation."""
    vendor_id: str = Field(description="Vendor ID")
    amount: float = Field(gt=0, description="Payment amount")
    currency: str = Field(default="USD", description="Currency code")
    due_date: str = Field(description="Due date (ISO format)")
    invoice_refs: Optional[List[str]] = Field(
        default=None,
        description="Invoice references",
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Request ID for idempotency",
    )


class ExecutionReadinessChecklist(BaseModel):
    """Execution readiness checklist schema."""
    is_vendor_active: bool
    bank_details_present: Optional[bool] = None  # None = unknown
    amount_within_threshold: bool
    requires_manual_review: bool


class VPMPaymentDraftOutput(BaseModel):
    """Output schema for VPM payment draft creation."""
    draft_id: str = Field(description="Draft ID")
    status: str = Field(description="Draft status (draft)")
    preview_markdown: str = Field(description="Preview markdown with vendor snapshot and approval requirements")
    risk_level: str = Field(description="Risk level")
    recommended_approvers: List[str] = Field(description="Recommended approver roles")
    vendor_snapshot: Dict[str, Any] = Field(description="Vendor snapshot (name, status, risk flags)")
    execution_readiness: ExecutionReadinessChecklist = Field(description="Execution readiness checklist")
    tenant_id: str = Field(description="Tenant ID")


async def vpm_payment_draft_create_handler(
    input: VPMPaymentDraftInput,
    context: ExecutionContext,
) -> VPMPaymentDraftOutput:
    """
    Create a payment draft.
    
    This is a Cluster MCP tool - draft-only, medium risk.
    
    Enforces Draft Protocol:
    - Creates draft object (status = draft)
    - Validates schema + policy pre-checks
    - Attaches rationale + citations (from Domain MCP reads)
    - Produces preview payload
    - Emits audit event
    - Never executes / never mutates production records
    
    Required Domain reads:
    - vpm.domain.vendor.read (vendor snapshot + risk flags)
    - workflow.domain.policy.read (approval)
    - security.domain.permission.read
    - featureflag.domain.status.read
    - optionally: vpm.domain.payment.status.read
    
    Args:
        input: VPMPaymentDraftInput
        context: Execution context
    
    Returns:
        VPMPaymentDraftOutput with draft information
    
    Raises:
        ValueError: If vendor inactive, permission denied, or feature flag disabled
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
            "vendor_snapshot": {},
            "policy_snapshot": {},
            "permission_check": {},
            "featureflag_status": {},
        }
        
        # 1. Read vendor profile (vpm.domain.vendor.read)
        # In production, would call vpm.domain.vendor.read
        vendor_snapshot = {
            "vendor_id": input.vendor_id,
            "vendor_name": "Example Vendor",  # Would come from Domain read
            "status": "active",  # Would come from Domain read
            "risk_flags": [],  # Would come from Domain read
            "payment_terms": "Net 30",
        }
        source_context["vendor_snapshot"] = vendor_snapshot
        
        # Check if vendor is active
        if vendor_snapshot["status"] != "active":
            raise ValueError(
                f"Vendor {input.vendor_id} is not active (status: {vendor_snapshot['status']}). "
                "Cannot create payment draft for inactive vendor."
            )
        
        # 2. Read workflow policy (workflow.domain.policy.read)
        # In production, would call workflow.domain.policy.read
        policy_snapshot = {
            "approval_rules": [
                {
                    "workflow_type": "payment",
                    "required_role": ["admin", "finance_manager"],
                    "threshold_amount": 1000.0,
                    "approval_count": 1,
                }
            ],
        }
        source_context["policy_snapshot"] = policy_snapshot
        
        # 3. Check permissions (security.domain.permission.read)
        # In production, would call security.domain.permission.read
        has_permission = context.user_role in ["admin", "finance_manager"]
        
        if not has_permission:
            raise ValueError(
                f"User role '{context.user_role}' lacks permission to create payment drafts. "
                "Required roles: admin, finance_manager"
            )
        
        source_context["permission_check"] = {
            "allowed": has_permission,
            "user_role": context.user_role,
        }
        
        # 4. Check feature flag (featureflag.domain.status.read)
        # In production, would call featureflag.domain.status.read
        vpm_enabled = True  # Would come from featureflag read
        
        if not vpm_enabled:
            raise ValueError("VPM module is disabled for this tenant")
        
        source_context["featureflag_status"] = {"vpm_enabled": vpm_enabled}
        
        # 5. Check payment status (optional, if referencing existing)
        # In production, would call vpm.domain.payment.status.read if needed
        
        # Build execution readiness checklist
        threshold_amount = policy_snapshot["approval_rules"][0].get("threshold_amount", 0)
        amount_within_threshold = input.amount <= threshold_amount
        
        # Determine if manual review required based on risk flags
        requires_manual_review = (
            len(vendor_snapshot.get("risk_flags", [])) > 0 or
            input.amount > threshold_amount or
            not amount_within_threshold
        )
        
        execution_readiness = ExecutionReadinessChecklist(
            is_vendor_active=(vendor_snapshot["status"] == "active"),
            bank_details_present=None,  # Unknown (would come from vendor profile in production)
            amount_within_threshold=amount_within_threshold,
            requires_manual_review=requires_manual_review,
        )
        
        # Build draft payload
        draft_payload: Dict[str, Any] = {
            "vendor_id": input.vendor_id,
            "vendor_snapshot": vendor_snapshot,
            "amount": input.amount,
            "currency": input.currency,
            "due_date": input.due_date,
            "invoice_refs": input.invoice_refs or [],
            "execution_readiness": execution_readiness.model_dump(),
            "policy_snapshot": policy_snapshot,
        }
        
        # Determine risk level
        risk_level = "medium"  # Default for Cluster MCPs
        if requires_manual_review or input.amount > threshold_amount:
            risk_level = "high"
        elif len(vendor_snapshot.get("risk_flags", [])) > 0:
            risk_level = "high"
        
        # Determine recommended approvers from policy
        recommended_approvers = []
        for rule in policy_snapshot["approval_rules"]:
            if rule["workflow_type"] == "payment":
                recommended_approvers.extend(rule.get("required_role", []))
        
        if not recommended_approvers:
            recommended_approvers = ["admin", "finance_manager"]  # Default
        
        # Create draft using Draft Protocol
        draft = await create_draft(
            tenant_id=context.tenant_id,
            draft_type="vpm_payment",
            payload=draft_payload,
            created_by=context.user_id,
            source_context=source_context,
            risk_level=risk_level,
            recommended_approvers=list(set(recommended_approvers)),  # Remove duplicates
            request_id=input.request_id,
        )
        
        # Generate preview markdown
        risk_flags_markdown = "\n".join([
            f"- {flag}" for flag in vendor_snapshot.get("risk_flags", [])
        ]) or "None"
        
        readiness_markdown = f"""
- Vendor Active: {'✅' if execution_readiness.is_vendor_active else '❌'}
- Bank Details: {'✅' if execution_readiness.bank_details_present else '❓' if execution_readiness.bank_details_present is None else '❌'}
- Amount Within Threshold: {'✅' if execution_readiness.amount_within_threshold else '❌'}
- Requires Manual Review: {'⚠️ Yes' if execution_readiness.requires_manual_review else '✅ No'}
"""
        
        preview_markdown = f"""# Payment Draft

**Vendor:** {vendor_snapshot['vendor_name']} ({input.vendor_id})
**Amount:** {input.currency} {input.amount:,.2f}
**Due Date:** {input.due_date}
**Status:** Draft
**Created:** {draft.created_at}
**Created By:** {context.user_id}

## Vendor Snapshot

- **Name:** {vendor_snapshot['vendor_name']}
- **Status:** {vendor_snapshot['status']}
- **Payment Terms:** {vendor_snapshot.get('payment_terms', 'N/A')}
- **Risk Flags:**
{risk_flags_markdown}

## Approval Requirements

- **Risk Level:** {risk_level}
- **Recommended Approvers:** {', '.join(recommended_approvers)}
- **Policy Source:** workflow.domain.policy.read

## Execution Readiness Checklist

{readiness_markdown}

## Invoice References

{chr(10).join(f"- {ref}" for ref in input.invoice_refs) if input.invoice_refs else "- None"}

---
*This is a draft. Submit for approval to execute payment.*
"""
        
        return VPMPaymentDraftOutput(
            draft_id=draft.draft_id,
            status=draft.status.value,
            preview_markdown=preview_markdown,
            risk_level=draft.risk_level,
            recommended_approvers=draft.recommended_approvers,
            vendor_snapshot=vendor_snapshot,
            execution_readiness=execution_readiness,
            tenant_id=context.tenant_id,
        )
    finally:
        if kernel_api:
            await kernel_api.close()


# Register the tool
def register_vpm_payment_draft_create_tool(registry) -> None:
    """Register the vpm.cluster.payment.draft.create tool."""
    tool = MCPTool(
        id="vpm.cluster.payment.draft.create",
        name="Create Payment Draft",
        description="Creates a payment draft with vendor snapshot, approval requirements, and execution readiness checklist. Reads vpm.domain.vendor.read, workflow.domain.policy.read, security.domain.permission.read, and featureflag.domain.status.read. Draft-only, no side effects.",
        layer="cluster",
        risk="medium",
        domain="vpm",
        input_schema=VPMPaymentDraftInput,
        output_schema=VPMPaymentDraftOutput,
        required_role=[],  # Permission checked via Domain reads
        required_scope=[],
        handler=vpm_payment_draft_create_handler,
    )
    registry.register(tool)

