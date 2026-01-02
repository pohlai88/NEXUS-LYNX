"""
Finance Domain MCP: Read Financial Health

Tool ID: finance.domain.health.read
Layer: domain
Risk: low
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from lynx.core.registry import MCPTool
from lynx.core.session import ExecutionContext
from lynx.integration.kernel import KernelAPI


class FinanceHealthInput(BaseModel):
    """Input schema for finance health read."""
    period: str = Field(
        default="current_month",
        description="Time period for health analysis (e.g., 'current_month', 'last_quarter')",
    )


class FinanceHealthOutput(BaseModel):
    """Output schema for finance health read."""
    health_score: int = Field(description="Financial health score (0-100)")
    status: str = Field(description="Health status: 'good', 'needs_attention', or 'critical'")
    risks: List[str] = Field(description="List of identified financial risks")
    recommendations: List[str] = Field(description="List of recommendations")


async def finance_health_read_handler(
    input: FinanceHealthInput,
    context: ExecutionContext,
) -> FinanceHealthOutput:
    """
    Read financial health summary.
    
    This is a Domain MCP tool - read-only, low risk.
    
    Args:
        input: FinanceHealthInput
        context: Execution context
    
    Returns:
        FinanceHealthOutput with health summary
    """
    # Initialize Kernel API for this tenant
    kernel_api = KernelAPI(tenant_id=context.tenant_id)
    
    try:
        # Read financial data from Kernel (tenant-scoped)
        # TODO: Implement actual Kernel API call
        # For now, return mock data
        financial_data = {
            "total_revenue": 100000,
            "total_expenses": 80000,
            "outstanding_payments": 5000,
        }
        
        # Calculate health score (simplified)
        net_income = financial_data["total_revenue"] - financial_data["total_expenses"]
        health_score = min(100, max(0, int((net_income / financial_data["total_revenue"]) * 100)))
        
        # Identify risks
        risks = []
        if financial_data["outstanding_payments"] > 0:
            risks.append("Outstanding payments detected")
        if net_income < 0:
            risks.append("Negative cash flow")
        
        # Generate recommendations
        recommendations = []
        if financial_data["outstanding_payments"] > 0:
            recommendations.append("Review and record outstanding payments in VPM")
        if net_income < financial_data["total_revenue"] * 0.1:
            recommendations.append("Review expense management")
        
        status = "good" if health_score > 80 else "needs_attention" if health_score > 50 else "critical"
        
        return FinanceHealthOutput(
            health_score=health_score,
            status=status,
            risks=risks,
            recommendations=recommendations,
        )
    finally:
        await kernel_api.close()


# Register the tool
def register_finance_health_read_tool(registry) -> None:
    """Register the finance.domain.health.read tool."""
    tool = MCPTool(
        id="finance.domain.health.read",
        name="Read Financial Health",
        description="Provides a summary of the company's financial health, including key metrics and potential risks.",
        layer="domain",
        risk="low",
        domain="finance",
        input_schema=FinanceHealthInput,
        output_schema=FinanceHealthOutput,
        required_role=[],  # No specific role required for read-only
        required_scope=[],  # No specific scope required for read-only
        handler=finance_health_read_handler,
    )
    registry.register(tool)

