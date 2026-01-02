"""
Tenant isolation enforcement.

This module enforces PRD Law 2: Tenant Absolutism.
"""

from typing import Any
from lynx.core.session import ExecutionContext


def enforce_tenant_isolation(
    context: ExecutionContext,
    requested_tenant_id: str,
) -> None:
    """
    Enforce tenant isolation - ensure user can only access their tenant's data.
    
    This enforces PRD Law 2: Tenant Absolutism.
    
    Args:
        context: Execution context
        requested_tenant_id: Tenant ID from the request
    
    Raises:
        PermissionError: If tenant IDs don't match
    """
    if context.tenant_id != requested_tenant_id:
        raise PermissionError(
            f"Tenant isolation violation: "
            f"User from tenant {context.tenant_id} attempted to access "
            f"tenant {requested_tenant_id} data"
        )


def validate_tenant_scope(
    context: ExecutionContext,
    data: Any,
    tenant_id_field: str = "tenant_id",
) -> None:
    """
    Validate that data belongs to the user's tenant.
    
    Args:
        context: Execution context
        data: Data to validate (dict or object with tenant_id attribute)
        tenant_id_field: Field name containing tenant ID
    
    Raises:
        PermissionError: If data doesn't belong to user's tenant
    """
    if isinstance(data, dict):
        data_tenant_id = data.get(tenant_id_field)
    else:
        data_tenant_id = getattr(data, tenant_id_field, None)
    
    if data_tenant_id and data_tenant_id != context.tenant_id:
        raise PermissionError(
            f"Tenant scope violation: "
            f"Data belongs to tenant {data_tenant_id}, "
            f"but user is from tenant {context.tenant_id}"
        )

