"""
Execution Protocol Models

Core models for the Execution Protocol (separated to avoid circular imports).
"""

from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from enum import Enum


class ExecutionStatus(str, Enum):
    """Execution status enumeration."""
    STARTED = "started"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    DENIED = "denied"


class ExecutionRecord(BaseModel):
    """
    Execution Record - Non-negotiable structure for all Cell MCP executions.
    
    This ensures:
    - Full audit trail
    - Idempotency
    - Rollback capability
    """
    execution_id: str = Field(description="Unique execution identifier")
    draft_id: str = Field(description="Source draft ID")
    tool_id: str = Field(description="Cell MCP tool ID")
    tenant_id: str = Field(description="Tenant ID (enforces tenant isolation)")
    actor_id: str = Field(description="User ID who executed")
    status: ExecutionStatus = Field(description="Execution status")
    result_payload: Dict[str, Any] = Field(
        default_factory=dict,
        description="Execution result (JSON)"
    )
    created_at: str = Field(description="Creation timestamp (ISO format)")
    completed_at: Optional[str] = Field(
        default=None,
        description="Completion timestamp (ISO format)"
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error message (if failed)"
    )
    rollback_instructions: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Rollback plan (if applicable)"
    )
    request_id: Optional[str] = Field(
        default=None,
        description="Request ID for idempotency"
    )
    source_context: Dict[str, Any] = Field(
        default_factory=dict,
        description="Snapshot of relevant Domain/Cluster reads and policy checks at execution time"
    )

