"""
Kernel Lite - Temporary in-memory Kernel implementation.

This is a lightweight, temporary implementation that provides Kernel API
functionality without requiring a backend. It's designed to be easily
replaced when the real Kernel API is ready.

**Purpose:**
- Enable staging deployment without waiting for Kernel backend
- Provide sensible defaults for metadata, schema, and permissions
- Allow all permissions (for staging/testing)
- Easy to swap out when real Kernel is available

**Usage:**
Set `KERNEL_MODE=lite` in environment variables to use this instead of real Kernel API.
"""

from typing import Dict, Any, Optional
import os


class KernelLite:
    """
    Lightweight in-memory Kernel implementation.
    
    Provides the same interface as KernelAPI but uses in-memory data
    instead of HTTP requests. Perfect for staging/testing.
    """
    
    def __init__(
        self,
        tenant_id: str,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
    ):
        """
        Initialize Kernel Lite.
        
        Args:
            tenant_id: Tenant ID (for tenant-scoped responses)
            api_url: Ignored (kept for interface compatibility)
            api_key: Ignored (kept for interface compatibility)
        """
        self.tenant_id = tenant_id
        self._metadata_cache: Dict[str, Dict[str, Any]] = {}
        self._schema_cache: Dict[str, Dict[str, Any]] = {}
    
    async def get_metadata(self, entity_type: str) -> Dict[str, Any]:
        """
        Get metadata for entity type (lite implementation).
        
        Returns sensible defaults for staging/testing.
        
        Args:
            entity_type: Entity type (e.g., "document", "workflow", "vendor")
        
        Returns:
            Metadata dictionary with default values
        """
        # Return cached or default metadata
        if entity_type in self._metadata_cache:
            return self._metadata_cache[entity_type]
        
        # Default metadata based on entity type
        defaults: Dict[str, Dict[str, Any]] = {
            "document": {
                "entity_type": "document",
                "metadata": {
                    "active_count": 0,
                    "pending_approvals": 0,
                    "lifecycle_states": ["draft", "submitted", "approved", "published", "executed"],
                    "supported_types": ["docs", "workflow", "vpm_payment"],
                },
            },
            "workflow": {
                "entity_type": "workflow",
                "metadata": {
                    "active_count": 0,
                    "pending_approvals": 0,
                    "lifecycle_states": ["draft", "submitted", "approved", "published"],
                    "approval_required": True,
                },
            },
            "vendor": {
                "entity_type": "vendor",
                "metadata": {
                    "active_count": 0,
                    "risk_flags": [],
                    "lifecycle_states": ["active", "inactive", "suspended"],
                },
            },
            "payment": {
                "entity_type": "payment",
                "metadata": {
                    "pending_count": 0,
                    "settlement_statuses": ["queued", "processing", "completed", "failed"],
                    "approval_threshold": 1000.0,
                },
            },
        }
        
        # Return default or generic metadata
        metadata = defaults.get(
            entity_type,
            {
                "entity_type": entity_type,
                "metadata": {
                    "active_count": 0,
                    "lifecycle_states": ["draft", "active"],
                },
            },
        )
        
        # Cache it
        self._metadata_cache[entity_type] = metadata
        return metadata
    
    async def get_schema(self, entity_type: str) -> Dict[str, Any]:
        """
        Get schema for entity type (lite implementation).
        
        Returns basic JSON schema structures.
        
        Args:
            entity_type: Entity type
        
        Returns:
            Schema dictionary
        """
        # Return cached or default schema
        if entity_type in self._schema_cache:
            return self._schema_cache[entity_type]
        
        # Default schemas based on entity type
        defaults: Dict[str, Dict[str, Any]] = {
            "document": {
                "entity_type": "document",
                "schema": {
                    "type": "object",
                    "properties": {
                        "document_id": {"type": "string"},
                        "document_type": {"type": "string", "enum": ["docs", "workflow", "vpm_payment"]},
                        "status": {"type": "string"},
                        "payload": {"type": "object"},
                    },
                    "required": ["document_id", "document_type"],
                },
            },
            "workflow": {
                "entity_type": "workflow",
                "schema": {
                    "type": "object",
                    "properties": {
                        "workflow_id": {"type": "string"},
                        "workflow_type": {"type": "string"},
                        "status": {"type": "string"},
                        "steps": {"type": "array"},
                    },
                    "required": ["workflow_id", "workflow_type"],
                },
            },
            "vendor": {
                "entity_type": "vendor",
                "schema": {
                    "type": "object",
                    "properties": {
                        "vendor_id": {"type": "string"},
                        "vendor_name": {"type": "string"},
                        "status": {"type": "string", "enum": ["active", "inactive", "suspended"]},
                        "risk_flags": {"type": "array"},
                    },
                    "required": ["vendor_id", "vendor_name"],
                },
            },
            "payment": {
                "entity_type": "payment",
                "schema": {
                    "type": "object",
                    "properties": {
                        "payment_id": {"type": "string"},
                        "amount": {"type": "number"},
                        "vendor_id": {"type": "string"},
                        "status": {"type": "string"},
                    },
                    "required": ["payment_id", "amount", "vendor_id"],
                },
            },
        }
        
        # Return default or generic schema
        schema = defaults.get(
            entity_type,
            {
                "entity_type": entity_type,
                "schema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string"},
                        "status": {"type": "string"},
                    },
                    "required": ["id"],
                },
            },
        )
        
        # Cache it
        self._schema_cache[entity_type] = schema
        return schema
    
    async def check_permission(
        self,
        user_id: str,
        action: str,
        resource_type: str,
    ) -> Dict[str, Any]:
        """
        Check permission (lite implementation).
        
        **Staging Mode:** Allows all permissions by default.
        This is safe for staging but should be replaced with real
        permission checks in production.
        
        Args:
            user_id: User ID
            action: Action to check (tool ID)
            resource_type: Resource type (domain)
        
        Returns:
            Permission check result with "allowed": True (staging mode)
        """
        # In staging/lite mode, allow all permissions
        # This can be made more restrictive later if needed
        return {
            "allowed": True,
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "tenant_id": self.tenant_id,
            "reason": "Kernel Lite mode - all permissions allowed for staging",
            "mode": "lite",
        }
    
    async def get_tenant_customizations(self) -> Dict[str, Any]:
        """
        Get tenant customizations (lite implementation).
        
        Returns default tenant configuration.
        
        Returns:
            Tenant customizations dictionary
        """
        return {
            "tenant_id": self.tenant_id,
            "customizations": {
                "theme": "default",
                "features": {
                    "workflow": True,
                    "vpm": True,
                    "docs": True,
                },
                "settings": {
                    "approval_threshold": 1000.0,
                    "auto_approve_low_risk": False,
                },
            },
            "mode": "lite",
        }
    
    async def close(self):
        """
        Close the Kernel Lite client.
        
        No-op for lite implementation (no connections to close).
        """
        pass

