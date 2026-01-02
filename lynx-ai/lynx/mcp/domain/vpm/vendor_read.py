"""
VPM Domain MCP: Read Vendor

Tool ID: vpm.domain.vendor.read
Layer: domain
Risk: low
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from lynx.core.registry import MCPTool
from lynx.core.session import ExecutionContext
from lynx.integration.kernel import KernelAPI


class VPMVendorInput(BaseModel):
    """Input schema for VPM vendor read."""
    vendor_id: Optional[str] = Field(
        default=None,
        description="Specific vendor ID (if None, returns summary)",
    )
    include_risk_flags: bool = Field(
        default=True,
        description="Include risk flags",
    )


class VendorProfile(BaseModel):
    """Vendor profile schema."""
    vendor_id: str
    vendor_name: str
    status: str
    risk_flags: List[str]
    payment_terms: Optional[str] = None
    total_payments: Optional[float] = None


class VPMVendorOutput(BaseModel):
    """Output schema for VPM vendor read."""
    vendor: Optional[VendorProfile] = Field(description="Vendor profile (if vendor_id provided)")
    vendors_summary: Optional[Dict[str, int]] = Field(description="Vendor summary by status (if vendor_id not provided)")
    tenant_id: str = Field(description="Tenant ID")


async def vpm_vendor_read_handler(
    input: VPMVendorInput,
    context: ExecutionContext,
) -> VPMVendorOutput:
    """
    Read vendor profile - vendor summary, risk flags, status.
    
    This is a Domain MCP tool - read-only, low risk.
    
    Args:
        input: VPMVendorInput
        context: Execution context
    
    Returns:
        VPMVendorOutput with vendor information
    """
    # Initialize Kernel API for this tenant (if available)
    kernel_api = None
    try:
        kernel_api = KernelAPI(tenant_id=context.tenant_id)
    except (ValueError, Exception):
        pass
    
    try:
        # Read vendor data from Kernel (tenant-scoped)
        # TODO: Implement actual Kernel API call
        # For now, return mock data
        
        if input.vendor_id:
            # Return specific vendor
            vendor = VendorProfile(
                vendor_id=input.vendor_id,
                vendor_name="Example Vendor",
                status="active",
                risk_flags=["outstanding_payments"] if input.include_risk_flags else [],
                payment_terms="Net 30",
                total_payments=50000.0,
            )
            return VPMVendorOutput(
                vendor=vendor,
                vendors_summary=None,
                tenant_id=context.tenant_id,
            )
        else:
            # Return summary
            vendors_summary = {
                "active": 10,
                "inactive": 2,
                "pending_approval": 1,
            }
            return VPMVendorOutput(
                vendor=None,
                vendors_summary=vendors_summary,
                tenant_id=context.tenant_id,
            )
    finally:
        if kernel_api:
            await kernel_api.close()


# Register the tool
def register_vpm_vendor_read_tool(registry) -> None:
    """Register the vpm.domain.vendor.read tool."""
    tool = MCPTool(
        id="vpm.domain.vendor.read",
        name="Read Vendor Profile",
        description="Returns vendor profile summary, risk flags, and status to set up Cluster drafting for VPM without execution risk.",
        layer="domain",
        risk="low",
        domain="vpm",
        input_schema=VPMVendorInput,
        output_schema=VPMVendorOutput,
        required_role=[],
        required_scope=[],
        handler=vpm_vendor_read_handler,
    )
    registry.register(tool)

