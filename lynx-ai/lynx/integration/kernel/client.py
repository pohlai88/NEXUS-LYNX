"""
Kernel API client.

Reads metadata, schema, and permissions from Kernel SSOT.
"""

import httpx
from typing import Dict, Any, Optional
import os


class KernelAPI:
    """Client for Kernel SSOT API."""
    
    def __init__(
        self,
        tenant_id: str,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize Kernel API client.
        
        Args:
            tenant_id: Tenant ID (for tenant-scoped requests)
            api_url: Kernel API URL (defaults to KERNEL_API_URL env var)
            api_key: Kernel API key (defaults to KERNEL_API_KEY env var)
        """
        self.tenant_id = tenant_id
        self.api_url = api_url or os.getenv("KERNEL_API_URL")
        self.api_key = api_key or os.getenv("KERNEL_API_KEY")
        
        # Allow initialization without URL/key if using lite mode
        # The factory function will handle mode selection
        if not self.api_url:
            raise ValueError("Kernel API URL not provided. Use KernelLite or set KERNEL_MODE=lite for staging.")
        if not self.api_key:
            raise ValueError("Kernel API key not provided. Use KernelLite or set KERNEL_MODE=lite for staging.")
        
        self.client = httpx.AsyncClient(
            base_url=self.api_url,
            headers={
                "X-Tenant-Id": tenant_id,
                "Authorization": f"Bearer {self.api_key}",
            },
            timeout=30.0,
        )
    
    async def get_metadata(self, entity_type: str) -> Dict[str, Any]:
        """
        Read metadata from Kernel SSOT.
        
        Args:
            entity_type: Entity type (e.g., "document", "workflow", "vendor")
        
        Returns:
            Metadata dictionary
        """
        response = await self.client.get(f"/metadata/{entity_type}")
        response.raise_for_status()
        return response.json()
    
    async def get_schema(self, entity_type: str) -> Dict[str, Any]:
        """
        Read schema from Kernel SSOT.
        
        Args:
            entity_type: Entity type
        
        Returns:
            Schema dictionary
        """
        response = await self.client.get(f"/schema/{entity_type}")
        response.raise_for_status()
        return response.json()
    
    async def check_permission(
        self,
        user_id: str,
        action: str,
        resource_type: str,
    ) -> Dict[str, Any]:
        """
        Check permission via Kernel.
        
        Args:
            user_id: User ID
            action: Action to check (tool ID)
            resource_type: Resource type (domain)
        
        Returns:
            Permission check result with "allowed" field
        """
        response = await self.client.post(
            "/permissions/check",
            json={
                "user_id": user_id,
                "tenant_id": self.tenant_id,
                "action": action,
                "resource_type": resource_type,
            },
        )
        response.raise_for_status()
        return response.json()
    
    async def get_tenant_customizations(self) -> Dict[str, Any]:
        """
        Get tenant customizations.
        
        Returns:
            Tenant customizations dictionary
        """
        response = await self.client.get(f"/tenants/{self.tenant_id}/customizations")
        response.raise_for_status()
        return response.json()
    
    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

