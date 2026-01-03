# API Testing Strategy - Railway Deployment

**Date:** 2026-01-27  
**Status:** 🚀 READY TO IMPLEMENT  
**Priority:** 🔴 HIGH - Railway is Live

---

## 🎯 Testing Objectives

Since **Railway is running**, we need to focus on **API testing** to ensure:
1. ✅ All endpoints are working correctly
2. ✅ Error handling is robust
3. ✅ Performance meets requirements (< 350ms)
4. ✅ Integration with backend services works

---

## 📋 Test Scope

### Endpoints to Test

#### Dashboard Endpoints
- `GET /` - Main dashboard (HTML)
- `GET /dashboard` - Dashboard alias
- `GET /health` - Health check (JSON)
- `GET /api/status` - Status API (JSON)

#### Fragment Endpoints
- `GET /dashboard/_kpis` - KPI fragment (HTML)
- `GET /dashboard/_services` - Services fragment (HTML)
- `GET /dashboard/_recent` - Recent activity fragment (HTML)
- `GET /dashboard/_cockpit` - Cockpit fragment (HTML)

#### Static Files
- `GET /static/aibos-design-system.css` - CSS file

---

## 🧪 Test Implementation Plan

### Phase 1: Basic API Tests (Day 1-2)

**File:** `tests/integration/test_dashboard_api_basic.py`

**Test Cases:**
```python
# Basic endpoint tests
- test_dashboard_home_returns_200
- test_dashboard_home_returns_html
- test_health_endpoint_returns_200
- test_health_endpoint_returns_json
- test_api_status_returns_200
- test_api_status_returns_json
- test_fragment_kpis_returns_200
- test_fragment_services_returns_200
- test_fragment_recent_returns_200
- test_fragment_cockpit_returns_200
```

**Implementation:**
- Use `httpx.AsyncClient` for async testing
- Test against Railway URL (or localhost for dev)
- Verify status codes
- Verify content types

---

### Phase 2: Response Validation Tests (Day 3-4)

**File:** `tests/integration/test_dashboard_api_validation.py`

**Test Cases:**
```python
# Response structure tests
- test_health_response_structure
- test_api_status_response_structure
- test_api_status_contains_required_fields
- test_fragment_kpis_contains_expected_elements
- test_fragment_services_contains_expected_elements
- test_fragment_recent_contains_expected_elements
- test_fragment_cockpit_contains_expected_elements
```

**Implementation:**
- Parse JSON responses
- Validate required fields
- Parse HTML responses (BeautifulSoup)
- Verify expected elements exist

---

### Phase 3: Error Handling Tests (Day 5)

**File:** `tests/integration/test_dashboard_api_errors.py`

**Test Cases:**
```python
# Error scenario tests
- test_dashboard_handles_backend_error
- test_fragment_kpis_handles_error
- test_fragment_services_handles_error
- test_fragment_recent_handles_error
- test_api_status_handles_backend_error
- test_404_for_invalid_endpoint
- test_500_error_format
```

**Implementation:**
- Mock backend failures
- Test error response format
- Verify error messages
- Test graceful degradation

---

### Phase 4: Performance Tests (Day 6-7)

**File:** `tests/integration/test_dashboard_api_performance.py`

**Test Cases:**
```python
# Performance tests
- test_dashboard_response_time_under_350ms
- test_fragment_response_time_under_200ms
- test_health_endpoint_response_time
- test_api_status_response_time
- test_concurrent_requests_handling
```

**Implementation:**
- Use `pytest-benchmark` or manual timing
- Test against performance requirements
- Test concurrent requests (10+)
- Measure memory usage

---

## 🛠️ Test Infrastructure

### Test Configuration

**File:** `tests/conftest.py` (add to existing)

```python
import pytest
import httpx
import os
from typing import AsyncGenerator

@pytest.fixture
async def api_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """Async HTTP client for API testing."""
    base_url = os.getenv("TEST_API_URL", "http://localhost:8000")
    async with httpx.AsyncClient(base_url=base_url, timeout=30.0) as client:
        yield client

@pytest.fixture
def railway_url() -> str:
    """Railway deployment URL."""
    return os.getenv("RAILWAY_URL", "https://lynx-ai-production.up.railway.app")

@pytest.fixture
async def railway_client(railway_url: str) -> AsyncGenerator[httpx.AsyncClient, None]:
    """Async HTTP client for Railway testing."""
    async with httpx.AsyncClient(base_url=railway_url, timeout=30.0) as client:
        yield client
```

---

### Test Utilities

**File:** `tests/utils/api_test_helpers.py`

```python
"""Helper functions for API testing."""

from typing import Dict, Any
from bs4 import BeautifulSoup
import httpx

def parse_json_response(response: httpx.Response) -> Dict[str, Any]:
    """Parse JSON response and validate."""
    assert response.status_code == 200
    assert "application/json" in response.headers.get("content-type", "")
    return response.json()

def parse_html_response(response: httpx.Response) -> BeautifulSoup:
    """Parse HTML response."""
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")
    return BeautifulSoup(response.text, "html.parser")

def assert_response_time(response_time: float, max_time: float):
    """Assert response time is under threshold."""
    assert response_time < max_time, f"Response time {response_time}ms exceeds {max_time}ms"
```

---

## 📝 Test Examples

### Example 1: Basic Endpoint Test

```python
# tests/integration/test_dashboard_api_basic.py

import pytest
import httpx

@pytest.mark.asyncio
async def test_dashboard_home_returns_200(api_client: httpx.AsyncClient):
    """Test main dashboard returns 200 OK."""
    response = await api_client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers.get("content-type", "")

@pytest.mark.asyncio
async def test_health_endpoint_returns_json(api_client: httpx.AsyncClient):
    """Test health endpoint returns JSON."""
    response = await api_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
```

---

### Example 2: Response Validation Test

```python
# tests/integration/test_dashboard_api_validation.py

import pytest
from tests.utils.api_test_helpers import parse_json_response, parse_html_response

@pytest.mark.asyncio
async def test_api_status_response_structure(api_client: httpx.AsyncClient):
    """Test status API response structure."""
    response = await api_client.get("/api/status")
    data = parse_json_response(response)
    
    # Required fields
    assert "service_name" in data
    assert "status" in data
    assert "lynx_protocol_version" in data
    assert "mcp_toolset_version" in data
    assert "kernel_api_reachable" in data
    assert "supabase_reachable" in data

@pytest.mark.asyncio
async def test_fragment_kpis_contains_elements(api_client: httpx.AsyncClient):
    """Test KPI fragment contains expected elements."""
    response = await api_client.get("/dashboard/_kpis")
    soup = parse_html_response(response)
    
    # Verify KPI cards exist
    kpi_cards = soup.find_all(class_="na-card")
    assert len(kpi_cards) >= 4  # At least 4 KPI cards
```

---

### Example 3: Performance Test

```python
# tests/integration/test_dashboard_api_performance.py

import pytest
import time

@pytest.mark.asyncio
async def test_dashboard_response_time_under_350ms(api_client: httpx.AsyncClient):
    """Test dashboard response time meets requirement."""
    start = time.time()
    response = await api_client.get("/")
    elapsed = (time.time() - start) * 1000  # Convert to ms
    
    assert response.status_code == 200
    assert elapsed < 350, f"Response time {elapsed}ms exceeds 350ms requirement"
```

---

### Example 4: Railway Deployment Test

```python
# tests/integration/test_railway_deployment.py

import pytest

@pytest.mark.asyncio
@pytest.mark.integration
async def test_railway_dashboard_accessible(railway_client: httpx.AsyncClient):
    """Test Railway deployment is accessible."""
    response = await railway_client.get("/")
    assert response.status_code == 200

@pytest.mark.asyncio
@pytest.mark.integration
async def test_railway_health_endpoint(railway_client: httpx.AsyncClient):
    """Test Railway health endpoint."""
    response = await railway_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
```

---

## 🚀 Running Tests

### Local Testing

```bash
# Run all API tests
uv run pytest tests/integration/test_dashboard_api*.py -v

# Run specific test file
uv run pytest tests/integration/test_dashboard_api_basic.py -v

# Run with coverage
uv run pytest tests/integration/test_dashboard_api*.py --cov=lynx.api.dashboard --cov-report=html
```

### Railway Testing

```bash
# Set Railway URL
export RAILWAY_URL="https://lynx-ai-production.up.railway.app"

# Run Railway tests
uv run pytest tests/integration/test_railway_deployment.py -v -m integration
```

### Performance Testing

```bash
# Run performance tests
uv run pytest tests/integration/test_dashboard_api_performance.py -v --durations=10
```

---

## 📊 Success Criteria

### Coverage Requirements
- [ ] **100% endpoint coverage** - All endpoints tested
- [ ] **95%+ code coverage** - Per project requirements
- [ ] **All tests passing** - 100% pass rate

### Performance Requirements
- [ ] **Dashboard response < 350ms** - Per requirements
- [ ] **Fragment response < 200ms** - Per requirements
- [ ] **Health endpoint < 100ms** - Quick health check
- [ ] **Concurrent requests** - Handle 10+ simultaneous requests

### Quality Requirements
- [ ] **Error handling verified** - All error scenarios tested
- [ ] **Response validation** - All responses validated
- [ ] **Railway deployment verified** - Live deployment tested

---

## 🔄 CI/CD Integration

### GitHub Actions (Future)

```yaml
# .github/workflows/api-tests.yml
name: API Tests

on: [push, pull_request]

jobs:
  api-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
      - run: uv run pytest tests/integration/test_dashboard_api*.py -v
```

---

## 📚 References

- **Testing Plan:** `docs/DEPLOYMENT/TESTING-PLAN.md`
- **GitHub MCP Analysis:** `docs/DEPLOYMENT/GITHUB-MCP-TESTING-ANALYSIS.md`
- **Railway Deployment:** Live at Railway domain
- **Current Tests:** 89/89 passing

---

**Status:** 🚀 **READY TO IMPLEMENT** - Start with Phase 1 (Basic API Tests)

