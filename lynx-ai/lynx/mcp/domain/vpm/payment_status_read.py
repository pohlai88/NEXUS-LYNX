"""
VPM Domain MCP: Read Payment Status

Tool ID: vpm.domain.payment.status.read
Layer: domain
Risk: low
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from lynx.core.registry import MCPTool
from lynx.core.session import ExecutionContext
from lynx.integration.kernel import KernelAPI


class VPMPaymentStatusInput(BaseModel):
    """Input schema for VPM payment status read."""
    vendor_id: Optional[str] = Field(
        default=None,
        description="Filter by vendor ID",
    )
    status: Optional[str] = Field(
        default=None,
        description="Filter by payment status (pending, approved, paid, failed)",
    )
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of payments to return",
    )


class PaymentSummary(BaseModel):
    """Payment summary schema."""
    payment_id: str
    vendor_id: str
    amount: float
    status: str
    created_at: str
    approved_at: Optional[str] = None
    paid_at: Optional[str] = None


class VPMPaymentStatusOutput(BaseModel):
    """Output schema for VPM payment status read."""
    payments: List[PaymentSummary] = Field(description="List of payments")
    pending_approvals_count: int = Field(description="Number of pending approvals")
    failed_payments_count: int = Field(description="Number of failed payments")
    total_pending_amount: float = Field(description="Total amount pending approval")
    tenant_id: str = Field(description="Tenant ID")


async def vpm_payment_status_read_handler(
    input: VPMPaymentStatusInput,
    context: ExecutionContext,
) -> VPMPaymentStatusOutput:
    """
    Read payment status - payment lifecycle snapshot, pending approvals, failed payments.
    
    This is a Domain MCP tool - read-only, low risk.
    
    Args:
        input: VPMPaymentStatusInput
        context: Execution context
    
    Returns:
        VPMPaymentStatusOutput with payment status
    """
    # Initialize Kernel API for this tenant (if available)
    kernel_api = None
    try:
        kernel_api = KernelAPI(tenant_id=context.tenant_id)
    except (ValueError, Exception):
        pass
    
    try:
        # Read payment data from Kernel (tenant-scoped)
        # TODO: Implement actual Kernel API call
        # For now, return mock data
        
        payments = [
            PaymentSummary(
                payment_id="payment-001",
                vendor_id="vendor-001",
                amount=1000.0,
                status="pending",
                created_at=datetime.now().isoformat(),
            ),
            PaymentSummary(
                payment_id="payment-002",
                vendor_id="vendor-002",
                amount=2500.0,
                status="approved",
                created_at=datetime.now().isoformat(),
                approved_at=datetime.now().isoformat(),
            ),
            PaymentSummary(
                payment_id="payment-003",
                vendor_id="vendor-001",
                amount=500.0,
                status="failed",
                created_at=datetime.now().isoformat(),
            ),
        ]
        
        # Apply filters
        if input.vendor_id:
            payments = [p for p in payments if p.vendor_id == input.vendor_id]
        
        if input.status:
            payments = [p for p in payments if p.status == input.status]
        
        # Limit results
        payments = payments[:input.limit]
        
        # Calculate summary
        pending_approvals_count = len([p for p in payments if p.status == "pending"])
        failed_payments_count = len([p for p in payments if p.status == "failed"])
        total_pending_amount = sum(p.amount for p in payments if p.status == "pending")
        
        return VPMPaymentStatusOutput(
            payments=payments,
            pending_approvals_count=pending_approvals_count,
            failed_payments_count=failed_payments_count,
            total_pending_amount=total_pending_amount,
            tenant_id=context.tenant_id,
        )
    finally:
        if kernel_api:
            await kernel_api.close()


# Register the tool
def register_vpm_payment_status_read_tool(registry) -> None:
    """Register the vpm.domain.payment.status.read tool."""
    tool = MCPTool(
        id="vpm.domain.payment.status.read",
        name="Read Payment Status",
        description="Returns payment lifecycle snapshot, pending approvals, and failed payments to prepare Week 7 Cell MCP candidates.",
        layer="domain",
        risk="low",
        domain="vpm",
        input_schema=VPMPaymentStatusInput,
        output_schema=VPMPaymentStatusOutput,
        required_role=[],
        required_scope=[],
        handler=vpm_payment_status_read_handler,
    )
    registry.register(tool)

