"""
Pytest configuration and shared fixtures.

This module provides fixtures for testing Lynx AI components.
"""

import pytest
from typing import Dict, Any
from unittest.mock import AsyncMock, MagicMock
from lynx.core.session import SessionManager, Session, ExecutionContext
from lynx.core.registry import MCPToolRegistry, MCPTool
from lynx.core.permissions import PermissionChecker
from lynx.core.audit import AuditLogger
from pydantic import BaseModel


# ============================================================================
# Session & Context Fixtures
# ============================================================================

@pytest.fixture
def session_manager():
    """Create a SessionManager instance."""
    return SessionManager()


@pytest.fixture
def tenant_t1() -> str:
    """Tenant ID for tenant 1."""
    return "tenant-t1"


@pytest.fixture
def tenant_t2() -> str:
    """Tenant ID for tenant 2."""
    return "tenant-t2"


@pytest.fixture
def user_id() -> str:
    """User ID for testing."""
    return "user-123"


@pytest.fixture
def session_t1(session_manager: SessionManager, tenant_t1: str, user_id: str) -> Session:
    """Create a session for tenant T1."""
    return session_manager.create_session(
        user_id=user_id,
        tenant_id=tenant_t1,
        user_role="admin",
        user_scope=["read", "write"],
    )


@pytest.fixture
def session_t2(session_manager: SessionManager, tenant_t2: str, user_id: str) -> Session:
    """Create a session for tenant T2."""
    return session_manager.create_session(
        user_id=user_id,
        tenant_id=tenant_t2,
        user_role="admin",
        user_scope=["read", "write"],
    )


@pytest.fixture
def context_t1(session_t1: Session) -> ExecutionContext:
    """Create execution context for tenant T1."""
    return ExecutionContext(
        user_id=session_t1.user_id,
        tenant_id=session_t1.tenant_id,
        user_role=session_t1.user_role,
        user_scope=session_t1.user_scope,
        session_id=session_t1.session_id,
    )


@pytest.fixture
def context_t2(session_t2: Session) -> ExecutionContext:
    """Create execution context for tenant T2."""
    return ExecutionContext(
        user_id=session_t2.user_id,
        tenant_id=session_t2.tenant_id,
        user_role=session_t2.user_role,
        user_scope=session_t2.user_scope,
        session_id=session_t2.session_id,
    )


# ============================================================================
# Registry & Tool Fixtures
# ============================================================================

@pytest.fixture
def tool_registry() -> MCPToolRegistry:
    """Create an empty MCPToolRegistry."""
    return MCPToolRegistry()


@pytest.fixture
def sample_input_schema():
    """Sample input schema for testing."""
    class SampleInput(BaseModel):
        query: str
        tenant_id: str
    
    return SampleInput


@pytest.fixture
def sample_output_schema():
    """Sample output schema for testing."""
    class SampleOutput(BaseModel):
        result: str
        status: str
    
    return SampleOutput


@pytest.fixture
async def sample_tool_handler():
    """Sample tool handler for testing."""
    async def handler(input_data: BaseModel, context: ExecutionContext):
        return {
            "result": f"Processed: {input_data.query}",
            "status": "success",
        }
    return handler


@pytest.fixture
def registered_tool(
    tool_registry: MCPToolRegistry,
    sample_input_schema,
    sample_output_schema,
    sample_tool_handler,
) -> MCPTool:
    """Register and return a sample tool."""
    tool = MCPTool(
        id="test.domain.sample.read",
        name="Sample Test Tool",
        description="A test tool for integration tests",
        layer="domain",
        risk="low",
        domain="test",
        input_schema=sample_input_schema,
        output_schema=sample_output_schema,
        required_role=[],
        required_scope=[],
        handler=sample_tool_handler,
    )
    tool_registry.register(tool)
    return tool


# ============================================================================
# Permission Checker Fixtures
# ============================================================================

@pytest.fixture
def permission_checker():
    """Create a PermissionChecker without Kernel API."""
    return PermissionChecker(kernel_api=None)


@pytest.fixture
def permission_checker_with_kernel():
    """Create a PermissionChecker with mocked Kernel API."""
    mock_kernel = AsyncMock()
    mock_kernel.check_permission = AsyncMock(return_value={"allowed": True})
    return PermissionChecker(kernel_api=mock_kernel)


# ============================================================================
# Audit Logger Fixtures
# ============================================================================

@pytest.fixture
def mock_audit_logger():
    """Create a mocked AuditLogger for testing."""
    logger = MagicMock(spec=AuditLogger)
    logger.log_lynx_run = AsyncMock()
    logger.log_execution_start = AsyncMock()
    logger.log_execution_success = AsyncMock()
    logger.log_execution_failure = AsyncMock()
    logger.log_execution_warning = AsyncMock()
    logger.log_refusal = AsyncMock()
    return logger


@pytest.fixture
def audit_logger_in_memory():
    """Create an in-memory audit logger for testing (no Supabase)."""
    class InMemoryAuditLogger:
        def __init__(self):
            self.runs: list[Dict[str, Any]] = []
            self.logs: list[Dict[str, Any]] = []
        
        async def log_lynx_run(self, run_id, user_id, tenant_id, user_query, lynx_response, status="completed"):
            self.runs.append({
                "run_id": run_id,
                "user_id": user_id,
                "tenant_id": tenant_id,
                "user_query": user_query,
                "lynx_response": lynx_response,
                "status": status,
            })
        
        async def log_execution_start(self, context, tool, input_data):
            self.logs.append({
                "type": "execution_start",
                "run_id": context.lynx_run_id,
                "tool_id": tool.id,
                "tenant_id": context.tenant_id,
                "input": input_data,
            })
        
        async def log_execution_success(self, context, tool, output_data):
            self.logs.append({
                "type": "execution_success",
                "run_id": context.lynx_run_id,
                "tool_id": tool.id,
                "tenant_id": context.tenant_id,
                "output": output_data,
            })
        
        async def log_execution_failure(self, context, tool, error):
            self.logs.append({
                "type": "execution_failure",
                "run_id": context.lynx_run_id,
                "tool_id": tool.id,
                "tenant_id": context.tenant_id,
                "error": error,
            })
        
        async def log_refusal(self, context, tool, reason):
            self.logs.append({
                "type": "refusal",
                "run_id": context.lynx_run_id,
                "tool_id": tool.id,
                "tenant_id": context.tenant_id,
                "reason": reason,
            })
        
        def get_runs(self) -> list[Dict[str, Any]]:
            return self.runs
        
        def get_logs(self) -> list[Dict[str, Any]]:
            return self.logs
    
    return InMemoryAuditLogger()


# ============================================================================
# API Testing Fixtures
# ============================================================================

import os
import httpx
from typing import AsyncGenerator


@pytest.fixture
def api_base_url() -> str:
    """Get API base URL from environment or default to localhost."""
    return os.getenv("TEST_API_URL", "http://localhost:8000")


@pytest.fixture
async def api_client(api_base_url: str) -> AsyncGenerator[httpx.AsyncClient, None]:
    """
    Async HTTP client for API testing.
    
    Environment-driven: Set TEST_API_URL to test against Railway or localhost.
    - Local: TEST_API_URL=http://localhost:8000 pytest
    - Railway: TEST_API_URL=https://lynx-ai-production.up.railway.app pytest -m integration
    """
    timeout = httpx.Timeout(30.0, connect=10.0)
    async with httpx.AsyncClient(base_url=api_base_url, timeout=timeout, follow_redirects=True) as client:
        yield client


# Pytest markers
def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "integration: marks tests as integration tests (deselect with '-m \"not integration\"')")
    config.addinivalue_line("markers", "performance: marks tests as performance tests")
    config.addinivalue_line("markers", "stress: marks tests as stress/edge-case tests")
    config.addinivalue_line("markers", "contract: marks tests as contract validation tests")
