"""
Dashboard View Models - Stable Data Contract

Defines the exact structure of data passed to dashboard templates.
This prevents drift between backend and frontend.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class ServiceStatus(str, Enum):
    """Governed status enum - UI cannot invent new statuses."""
    OK = "ok"
    PENDING = "pending"
    BAD = "bad"
    INFO = "info"
    ERROR = "error"


class DashboardViewModel:
    """Stable contract for dashboard data."""
    
    def __init__(self, raw_status: Dict[str, Any]):
        """Convert raw status dict to stable view model."""
        self.service_name: str = raw_status.get("service_name", "Lynx AI")
        self.status: str = raw_status.get("status", "degraded")  # operational, degraded, error
        self.lynx_protocol_version: str = raw_status.get("lynx_protocol_version", "unknown")
        self.mcp_toolset_version: str = raw_status.get("mcp_toolset_version", "unknown")
        self.tool_registry_hash: str = raw_status.get("tool_registry_hash", "unknown")
        
        # System state
        self.current_mode: str = raw_status.get("current_mode", "unknown")
        self.maintenance_mode: bool = raw_status.get("maintenance_mode", False)
        self.storage_backend: str = raw_status.get("storage_backend", "unknown")
        
        # Connectivity
        self.kernel_api_reachable: bool = raw_status.get("kernel_api_reachable", False)
        self.supabase_reachable: bool = raw_status.get("supabase_reachable", False)
        
        # Activity metrics (24h)
        self.draft_count_24h: int = raw_status.get("draft_count_24h", 0)
        self.execution_count_24h: int = raw_status.get("execution_count_24h", 0)
        self.pending_settlement_count: int = raw_status.get("pending_settlement_count", 0)
        
        # Tools
        self.total_mcp_tools_registered: int = raw_status.get("total_mcp_tools_registered", 0)
        
        # Recent runs
        self.last_5_runs_summary: List[Dict[str, Any]] = raw_status.get("last_5_runs_summary", [])
        
        # Error state
        self.error_message: Optional[str] = raw_status.get("error_message")
        self.timestamp: datetime = datetime.now()
    
    def get_status_enum(self) -> ServiceStatus:
        """Convert status string to governed enum."""
        status_map = {
            "operational": ServiceStatus.OK,
            "degraded": ServiceStatus.PENDING,
            "error": ServiceStatus.BAD,
        }
        return status_map.get(self.status, ServiceStatus.INFO)
    
    def get_kernel_status(self) -> ServiceStatus:
        """Get kernel API status as enum."""
        return ServiceStatus.OK if self.kernel_api_reachable else ServiceStatus.BAD
    
    def get_supabase_status(self) -> ServiceStatus:
        """Get Supabase status as enum."""
        return ServiceStatus.OK if self.supabase_reachable else ServiceStatus.BAD
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for template rendering."""
        return {
            "service_name": self.service_name,
            "status": self.status,
            "status_enum": self.get_status_enum().value,
            "lynx_protocol_version": self.lynx_protocol_version,
            "mcp_toolset_version": self.mcp_toolset_version,
            "tool_registry_hash": self.tool_registry_hash,
            "current_mode": self.current_mode,
            "maintenance_mode": self.maintenance_mode,
            "storage_backend": self.storage_backend,
            "kernel_api_reachable": self.kernel_api_reachable,
            "kernel_status": self.get_kernel_status().value,
            "supabase_reachable": self.supabase_reachable,
            "supabase_status": self.get_supabase_status().value,
            "draft_count_24h": self.draft_count_24h,
            "execution_count_24h": self.execution_count_24h,
            "pending_settlement_count": self.pending_settlement_count,
            "total_mcp_tools_registered": self.total_mcp_tools_registered,
            "last_5_runs_summary": self.last_5_runs_summary,
            "error_message": self.error_message,
            "timestamp": self.timestamp.isoformat(),
        }


class DeveloperCockpitViewModel:
    """Developer cockpit data - "Where am I now" block."""
    
    def __init__(self):
        """Initialize developer cockpit data."""
        # TODO: Get from git/config/deployment status
        self.current_stage: str = "STAGING"  # STAGING / PROD
        self.last_successful_task: Optional[str] = None  # commit/tag/build ID
        self.next_recommended_action: Optional[str] = None
        self.top_blockers: List[str] = []
        self.deployment_url: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for template rendering."""
        return {
            "current_stage": self.current_stage,
            "last_successful_task": self.last_successful_task,
            "next_recommended_action": self.next_recommended_action,
            "top_blockers": self.top_blockers,
            "deployment_url": self.deployment_url,
        }

