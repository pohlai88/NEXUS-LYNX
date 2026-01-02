# Lynx AI Test Suite

This directory contains the test suite for Lynx AI, organized to validate PRD Law enforcement and foundation correctness.

---

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests (component-level)
├── integration/             # Integration tests (PRD Law gates)
│   ├── test_tenant_isolation.py      # LAW 2: Tenant Absolutism
│   ├── test_tool_registry.py         # LAW 3: Tool-Only Action
│   ├── test_audit_completeness.py    # LAW 5: Audit Is Reality
│   └── test_kernel_supremacy.py      # LAW 1: Kernel Supremacy
└── fixtures/                # Test fixtures and utilities
```

---

## Running Tests

### Run All Tests

```bash
uv run pytest
```

### Run Specific Test Suite

```bash
# Integration tests only
uv run pytest tests/integration/

# Tenant isolation tests only
uv run pytest tests/integration/test_tenant_isolation.py

# Specific test
uv run pytest tests/integration/test_tenant_isolation.py::TestCrossTenantAccessDenied
```

### Run with Verbose Output

```bash
uv run pytest -v
```

### Run with Coverage

```bash
uv run pytest --cov=lynx --cov-report=html
```

---

## Test Categories

### Integration Tests (PRD Law Gates)

These tests validate that PRD Laws are enforced as executable gates:

1. **Tenant Isolation (LAW 2)**
   - `test_tenant_isolation.py`
   - Validates tenant boundaries are never violated

2. **Tool Registry (LAW 3)**
   - `test_tool_registry.py`
   - Validates only registered tools can execute

3. **Audit Completeness (LAW 5)**
   - `test_audit_completeness.py`
   - Validates all actions are logged

4. **Kernel Supremacy (LAW 1)**
   - `test_kernel_supremacy.py`
   - Validates Kernel SSOT is always consulted

---

## Test Fixtures

See `conftest.py` for available fixtures:

- `session_manager` - SessionManager instance
- `tenant_t1`, `tenant_t2` - Tenant IDs
- `session_t1`, `session_t2` - Session instances
- `context_t1`, `context_t2` - ExecutionContext instances
- `tool_registry` - MCPToolRegistry instance
- `registered_tool` - Sample registered tool
- `permission_checker` - PermissionChecker instance
- `mock_audit_logger` - Mocked AuditLogger
- `audit_logger_in_memory` - In-memory audit logger

---

## Writing New Tests

### Example: Test a New Domain MCP

```python
import pytest
from lynx.core.registry import MCPToolRegistry, execute_tool
from lynx.core.session import ExecutionContext
from lynx.core.permissions import PermissionChecker
from lynx.core.audit import AuditLogger

@pytest.mark.asyncio
async def test_new_domain_mcp(
    tool_registry: MCPToolRegistry,
    context_t1: ExecutionContext,
    permission_checker: PermissionChecker,
    mock_audit_logger: AuditLogger,
):
    # Register tool
    # ... tool registration code ...
    
    # Execute tool
    result = await execute_tool(
        tool_id="new.domain.tool",
        input_data={...},
        context=context_t1,
        registry=tool_registry,
        permission_checker=permission_checker,
        audit_logger=mock_audit_logger,
    )
    
    # Assertions
    assert result is not None
    # ... more assertions ...
```

---

## CI Integration

Tests are designed to run in CI/CD pipelines:

```bash
# CI command
uv run pytest --tb=short -v
```

---

## Coverage Goals

- **Integration Tests:** 100% coverage of PRD Law gates
- **Unit Tests:** 80%+ coverage of core components
- **Overall:** 75%+ coverage

---

**Status:** Foundation tests complete ✅

