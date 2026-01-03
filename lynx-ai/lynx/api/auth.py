"""
Authentication and Session Management for API Endpoints

Provides get_current_session dependency for FastAPI routes.
Backend derives tenant_id from session (never from client).
"""

from typing import Dict, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
import jwt
from datetime import datetime

# For now, use a simple approach - can be enhanced with proper auth system
# In production, this would integrate with your auth provider (Supabase Auth, Auth.js, etc.)

security = HTTPBearer(auto_error=False)


async def get_current_session(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, str]:
    """
    Get current session from JWT token or session cookie.
    
    ✅ Backend derives tenant_id from session (never from client request).
    ✅ Returns session dict with tenant_id, user_id, role.
    
    Args:
        credentials: HTTP Bearer token (optional)
    
    Returns:
        Session dict with tenant_id, user_id, role
    
    Raises:
        HTTPException: If authentication fails
    """
    # TODO: Implement proper auth integration
    # For now, use a simple mock/staging approach
    
    # Option 1: JWT Token (Bearer)
    if credentials:
        try:
            # In production, verify JWT with your auth provider
            # For now, use a simple secret (replace with proper secret management)
            secret = os.getenv("JWT_SECRET", "staging-secret-key")
            payload = jwt.decode(credentials.credentials, secret, algorithms=["HS256"])
            
            return {
                "tenant_id": payload.get("tenant_id", "default-tenant"),
                "user_id": payload.get("user_id", "default-user"),
                "role": payload.get("role", "user"),
            }
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )
    
    # Option 2: Session Cookie (if using cookies)
    # TODO: Implement cookie-based session extraction
    
    # Option 3: Staging/Mock (for development)
    # In staging, allow mock session for testing
    if os.getenv("ENVIRONMENT") == "staging":
        return {
            "tenant_id": os.getenv("MOCK_TENANT_ID", "tenant-t1"),
            "user_id": os.getenv("MOCK_USER_ID", "user-123"),
            "role": os.getenv("MOCK_ROLE", "admin"),
        }
    
    # No valid auth found
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Authentication required"
    )


def verify_tenant_access(
    session: Dict[str, str],
    requested_tenant_id: Optional[str] = None,
) -> None:
    """
    Verify tenant access (reject if tenant_id mismatch).
    
    ✅ Enforces tenant isolation - backend always checks.
    
    Args:
        session: Current session dict
        requested_tenant_id: Tenant ID from request (if any)
    
    Raises:
        HTTPException: If tenant access denied
    """
    session_tenant_id = session.get("tenant_id")
    
    # If request includes tenant_id, verify it matches session
    if requested_tenant_id and requested_tenant_id != session_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Tenant access denied: session tenant {session_tenant_id} != requested {requested_tenant_id}"
        )
    
    # Session tenant_id is the source of truth
    # All queries should use session_tenant_id, not requested_tenant_id

