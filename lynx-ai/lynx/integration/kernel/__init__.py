"""
Kernel SSOT integration.

This module enforces PRD Law 1: Kernel Supremacy.

Supports two modes:
- "api": Real Kernel API (requires KERNEL_API_URL and KERNEL_API_KEY)
- "lite": Temporary in-memory implementation (for staging/testing)
"""

from typing import Optional, Union
from lynx.integration.kernel.client import KernelAPI
from lynx.integration.kernel.lite import KernelLite
from lynx.config import Config

__all__ = ["KernelAPI", "KernelLite", "create_kernel_client"]


def create_kernel_client(
    tenant_id: str,
    api_url: Optional[str] = None,
    api_key: Optional[str] = None,
) -> Union[KernelAPI, KernelLite]:
    """
    Factory function to create Kernel client based on configuration.
    
    If KERNEL_MODE=lite or KERNEL_API_URL is not set, returns KernelLite.
    Otherwise, returns KernelAPI.
    
    Args:
        tenant_id: Tenant ID
        api_url: Kernel API URL (optional, uses env var if not provided)
        api_key: Kernel API key (optional, uses env var if not provided)
    
    Returns:
        KernelAPI or KernelLite instance
    """
    # Check if lite mode is explicitly requested
    if Config.KERNEL_MODE == "lite":
        return KernelLite(tenant_id=tenant_id, api_url=api_url, api_key=api_key)
    
    # Check if Kernel API URL is available
    kernel_url = api_url or Config.KERNEL_API_URL
    if not kernel_url:
        # No Kernel API URL - use lite mode
        return KernelLite(tenant_id=tenant_id, api_url=api_url, api_key=api_key)
    
    # Kernel API URL available - use real API
    # Note: KernelAPI will raise ValueError if api_key is missing, which is fine
    return KernelAPI(tenant_id=tenant_id, api_url=api_url, api_key=api_key)
