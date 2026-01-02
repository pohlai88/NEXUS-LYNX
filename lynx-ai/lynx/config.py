"""
Lynx AI Configuration

Handles environment variables and configuration settings.
"""

import os
from typing import Optional
from enum import Enum


class LynxMode(str, Enum):
    """Lynx execution mode."""
    DEV = "dev"
    STAGING = "staging"
    PROD = "prod"


class LynxRunner(str, Enum):
    """Lynx runner mode."""
    ONESHOT = "oneshot"  # Initialize and exit (for local testing)
    DAEMON = "daemon"    # Long-running process (for Railway/staging)


class Config:
    """Lynx configuration."""
    
    # Protocol Versions
    LYNX_PROTOCOL_VERSION: str = "0.1.0"
    MCP_TOOLSET_VERSION: str = "0.1.0"
    
    # Execution Mode
    LYNX_MODE: LynxMode = LynxMode(os.getenv("LYNX_MODE", "dev").lower())
    
    # Runner Mode
    LYNX_RUNNER: LynxRunner = LynxRunner(os.getenv("LYNX_RUNNER", "oneshot").lower())
    
    # Kernel API
    KERNEL_API_URL: Optional[str] = os.getenv("KERNEL_API_URL")
    
    # Supabase
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")
    
    # Maintenance Mode
    MAINTENANCE_MODE: bool = os.getenv("LYNX_MAINTENANCE_MODE", "false").lower() == "true"
    
    # Daemon Settings
    DAEMON_HEARTBEAT_INTERVAL: int = int(os.getenv("LYNX_DAEMON_HEARTBEAT_INTERVAL", "60"))  # seconds
    DAEMON_STATUS_CHECK_INTERVAL: int = int(os.getenv("LYNX_DAEMON_STATUS_CHECK_INTERVAL", "300"))  # seconds
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode."""
        return cls.LYNX_MODE == LynxMode.PROD
    
    @classmethod
    def requires_explicit_approval_for_high_risk(cls) -> bool:
        """
        Check if high-risk actions require explicit approval.
        
        In production, high-risk Cell tools require:
        - approved draft AND
        - explicit_approval=True
        """
        return cls.is_production()
    
    @classmethod
    def validate(self) -> None:
        """Validate configuration."""
        if self.KERNEL_API_URL is None:
            raise ValueError("KERNEL_API_URL environment variable is required")
        
        if self.SUPABASE_URL is None:
            raise ValueError("SUPABASE_URL environment variable is required")
        
        if self.SUPABASE_KEY is None:
            raise ValueError("SUPABASE_KEY environment variable is required")

