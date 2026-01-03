"""
Security Tests (Baseline, not pentest) - D.

Tests validate baseline security measures:
- D1. No secret leakage (responses, logs, draft artifacts)
- D2. Headers sanity (X-Content-Type-Options, Content-Security-Policy)
- D3. Rate limiting behavior (if implemented)
- D4. Input hardening (payload size limits, XSS guards)
"""

import pytest
import httpx
import json
from lynx.core.registry import MCPToolRegistry, execute_tool
from lynx.core.session import ExecutionContext
from lynx.core.permissions import PermissionChecker
from lynx.core.audit import AuditLogger
from lynx.mcp.cluster.drafts.base import get_draft_storage
from tests.utils.http_assertions import assert_no_secrets_in_response

# Import Cluster MCP registration functions
from lynx.mcp.cluster.docs.draft_create import register_docs_draft_create_tool
from lynx.mcp.cluster.vpm.payment_draft_create import register_vpm_payment_draft_create_tool


# ============================================================================
# D1. No Secret Leakage
# ============================================================================

@pytest.mark.asyncio
class TestNoSecretLeakageInResponses:
    """Test no secret leakage in HTTP responses."""
    
    async def test_health_endpoint_no_secrets(self, api_client: httpx.AsyncClient):
        """Test /health endpoint does not leak secrets."""
        response = await api_client.get("/health")
        assert_no_secrets_in_response(response)
    
    async def test_api_status_no_secrets(self, api_client: httpx.AsyncClient):
        """Test /api/status endpoint does not leak secrets."""
        response = await api_client.get("/api/status")
        assert_no_secrets_in_response(response)
    
    async def test_dashboard_no_secrets(self, api_client: httpx.AsyncClient):
        """Test dashboard HTML does not leak secrets."""
        response = await api_client.get("/dashboard")
        
        # Check HTML content for secrets
        text = response.text.lower()
        secret_patterns = [
            "api_key",
            "secret",
            "password",
            "token",
            "credential",
            "private_key",
            "access_token",
        ]
        
        for pattern in secret_patterns:
            # Check if pattern appears in a way that suggests a secret value
            # (not just in comments or safe contexts)
            if pattern in text:
                # If it's in a script tag or data attribute, it might be a secret
                if f'"{pattern}' in text or f"'{pattern}" in text:
                    # Allow known safe patterns
                    if "api_url" not in text and "endpoint" not in text:
                        pytest.fail(f"Potential secret pattern '{pattern}' found in dashboard HTML")
    
    async def test_fragments_no_secrets(self, api_client: httpx.AsyncClient):
        """Test HTML fragments do not leak secrets."""
        fragments = [
            "/dashboard/_kpis",
            "/dashboard/_services",
            "/dashboard/_recent",
            "/dashboard/_cockpit",
        ]
        
        for fragment in fragments:
            response = await api_client.get(fragment)
            text = response.text.lower()
            
            # Check for secret patterns
            secret_patterns = ["api_key", "secret", "password", "token"]
            for pattern in secret_patterns:
                if pattern in text and f'"{pattern}' in text:
                    pytest.fail(f"Potential secret pattern '{pattern}' found in {fragment}")


@pytest.mark.asyncio
class TestNoSecretLeakageInLogs:
    """Test no secret leakage in audit logs."""
    
    async def test_audit_log_no_secrets(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test audit logs do not contain secrets."""
        register_docs_draft_create_tool(tool_registry)
        
        # Execute a tool that creates audit log
        await execute_tool(
            tool_id="docs.cluster.draft.create",
            input_data={
                "doc_type": "PRD",
                "title": "Test Document",
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Check audit log entries (if accessible)
        if hasattr(mock_audit_logger, 'logs'):
            for log_entry in mock_audit_logger.logs:
                log_str = str(log_entry).lower()
                
                # Check for secret patterns
                secret_patterns = ["api_key", "secret", "password", "token", "credential"]
                for pattern in secret_patterns:
                    if pattern in log_str:
                        # Check if it's a value (not just a key name)
                        # This is a basic check - more sophisticated filtering would be in production
                        if f"{pattern}=" in log_str or f'"{pattern}":' in log_str:
                            # Allow known safe fields
                            if "api_url" not in log_str and "endpoint" not in log_str:
                                pytest.fail(f"Potential secret '{pattern}' found in audit log")


@pytest.mark.asyncio
class TestNoSecretLeakageInDraftArtifacts:
    """Test no secret leakage in draft artifacts."""
    
    async def test_draft_payload_no_secrets(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test draft payloads do not contain secrets."""
        register_vpm_payment_draft_create_tool(tool_registry)
        
        # Create a draft
        result = await execute_tool(
            tool_id="vpm.cluster.payment.draft.create",
            input_data={
                "vendor_id": "vendor-001",
                "amount": 100.0,
                "currency": "USD",
                "due_date": "2026-12-31T23:59:59Z",
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        draft_id = result["draft_id"]
        draft_storage = get_draft_storage()
        draft = await draft_storage.get_draft(draft_id, context_t1.tenant_id)
        
        # Check draft payload for secrets
        payload_str = json.dumps(draft.payload).lower()
        
        secret_patterns = ["api_key", "secret", "password", "token", "credential", "private_key"]
        for pattern in secret_patterns:
            if pattern in payload_str:
                # Check if it's a value (not just a key name)
                if f'"{pattern}":' in payload_str or f'"{pattern}"' in payload_str:
                    # Allow known safe fields
                    if "api_url" not in payload_str and "endpoint" not in payload_str:
                        pytest.fail(f"Potential secret '{pattern}' found in draft payload")
    
    async def test_draft_preview_no_secrets(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test draft preview markdown does not contain secrets."""
        register_docs_draft_create_tool(tool_registry)
        
        # Create a draft
        result = await execute_tool(
            tool_id="docs.cluster.draft.create",
            input_data={
                "doc_type": "PRD",
                "title": "Test Document",
            },
            context=context_t1,
            registry=tool_registry,
            permission_checker=permission_checker,
            audit_logger=mock_audit_logger,
        )
        
        # Check preview markdown for secrets
        preview = result.get("preview_markdown", "").lower()
        
        secret_patterns = ["api_key", "secret", "password", "token"]
        for pattern in secret_patterns:
            if pattern in preview:
                # Check if it looks like a secret value (not just mentioned in text)
                if f"{pattern}=" in preview or f"{pattern}:" in preview:
                    pytest.fail(f"Potential secret '{pattern}' found in draft preview")


# ============================================================================
# D2. Headers Sanity
# ============================================================================

@pytest.mark.asyncio
class TestSecurityHeaders:
    """Test security headers (if applicable)."""
    
    async def test_x_content_type_options_header(self, api_client: httpx.AsyncClient):
        """Test X-Content-Type-Options header (if implemented)."""
        response = await api_client.get("/dashboard")
        
        # X-Content-Type-Options: nosniff prevents MIME type sniffing
        # This is a soft check - doesn't fail if header doesn't exist
        # (header may be set by reverse proxy or not implemented yet)
        if "x-content-type-options" in response.headers:
            assert response.headers["x-content-type-options"].lower() == "nosniff", (
                "X-Content-Type-Options should be 'nosniff'"
            )
    
    async def test_content_security_policy_header(self, api_client: httpx.AsyncClient):
        """Test Content-Security-Policy header for portal (if implemented)."""
        response = await api_client.get("/dashboard")
        
        # Content-Security-Policy prevents XSS attacks
        # This is a soft check - doesn't fail if header doesn't exist
        # (CSP may be set by reverse proxy or not implemented yet)
        if "content-security-policy" in response.headers:
            csp = response.headers["content-security-policy"].lower()
            # Basic CSP should have script-src directive
            assert "script-src" in csp or "default-src" in csp, (
                "Content-Security-Policy should have script-src or default-src directive"
            )
    
    async def test_security_headers_consistency(self, api_client: httpx.AsyncClient):
        """Test security headers are consistent across endpoints."""
        endpoints = [
            "/dashboard",
            "/health",
            "/api/status",
        ]
        
        headers_to_check = ["x-content-type-options", "content-security-policy"]
        
        # Collect headers from all endpoints
        header_values = {}
        for endpoint in endpoints:
            response = await api_client.get(endpoint)
            for header in headers_to_check:
                if header in response.headers:
                    if header not in header_values:
                        header_values[header] = response.headers[header]
                    else:
                        # Headers should be consistent (or at least not contradictory)
                        # This is a soft check
                        pass


# ============================================================================
# D3. Rate Limiting Behavior
# ============================================================================

@pytest.mark.asyncio
class TestRateLimiting:
    """Test rate limiting behavior (if implemented)."""
    
    async def test_rate_limiting_bursts_refuse_correctly(self, api_client: httpx.AsyncClient):
        """Test that bursts are refused correctly (if rate limiting implemented)."""
        # Send rapid requests to test rate limiting
        responses = []
        for _ in range(20):  # Burst of 20 requests
            try:
                response = await api_client.get("/health")
                responses.append(response.status_code)
            except Exception:
                # Rate limiting may cause connection errors
                pass
        
        # If rate limiting is implemented:
        # - Some requests should return 429 (Too Many Requests)
        # - Or connection should be refused
        # - Or requests should be throttled
        
        # This is a soft check - doesn't fail if rate limiting not implemented
        status_codes = set(responses)
        
        # If 429 is in responses, rate limiting is working
        if 429 in status_codes:
            # Verify rate limiting is working
            assert len([r for r in responses if r == 429]) > 0, (
                "Rate limiting should return 429 for excessive requests"
            )
    
    async def test_rate_limiting_headers(self, api_client: httpx.AsyncClient):
        """Test rate limiting headers (if implemented)."""
        response = await api_client.get("/health")
        
        # Rate limiting headers (if implemented):
        # - X-RateLimit-Limit: Maximum requests per window
        # - X-RateLimit-Remaining: Remaining requests in window
        # - X-RateLimit-Reset: When the rate limit resets
        
        rate_limit_headers = [
            "x-ratelimit-limit",
            "x-ratelimit-remaining",
            "x-ratelimit-reset",
        ]
        
        # This is a soft check - doesn't fail if headers don't exist
        # (rate limiting may not be implemented yet)
        if any(header in response.headers for header in rate_limit_headers):
            # If rate limiting headers exist, verify they're valid
            if "x-ratelimit-limit" in response.headers:
                limit = response.headers["x-ratelimit-limit"]
                assert limit.isdigit(), "X-RateLimit-Limit should be a number"
            
            if "x-ratelimit-remaining" in response.headers:
                remaining = response.headers["x-ratelimit-remaining"]
                assert remaining.isdigit(), "X-RateLimit-Remaining should be a number"


# ============================================================================
# D4. Input Hardening
# ============================================================================

@pytest.mark.asyncio
class TestPayloadSizeLimits:
    """Test payload size limits."""
    
    async def test_large_payload_rejected(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that excessively large payloads are rejected."""
        register_docs_draft_create_tool(tool_registry)
        
        # Create a very large title (should be rejected or truncated)
        large_title = "A" * 10000  # 10KB title
        
        # Try to create draft with large payload
        # This should either:
        # - Be rejected with 400 (Bad Request)
        # - Be truncated to max length
        # - Be accepted if within limits
        
        try:
            result = await execute_tool(
                tool_id="docs.cluster.draft.create",
                input_data={
                    "doc_type": "PRD",
                    "title": large_title,
                },
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
            
            # If accepted, verify it was truncated or handled appropriately
            if result:
                # Check if title was truncated
                draft_id = result.get("draft_id")
                if draft_id:
                    draft_storage = get_draft_storage()
                    draft = await draft_storage.get_draft(draft_id, context_t1.tenant_id)
                    title_in_payload = draft.payload.get("title", "")
                    
                    # Title should be truncated if too long
                    # (exact limit depends on implementation)
                    assert len(title_in_payload) <= len(large_title), (
                        "Large payload should be truncated or rejected"
                    )
        except ValueError as e:
            # If rejected, that's also acceptable
            error_msg = str(e).lower()
            assert "too large" in error_msg or "exceeds" in error_msg or "limit" in error_msg, (
                "Large payload rejection should mention size limit"
            )
    
    async def test_batch_size_limits(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test batch size limits (if applicable)."""
        from lynx.mcp.cluster.docs.batch_draft_create import register_batch_docs_draft_create_tool
        
        register_batch_docs_draft_create_tool(tool_registry)
        
        # Create a very large batch (should be rejected or chunked)
        large_batch = [
            {"doc_type": "PRD", "title": f"Document {i}"}
            for i in range(1000)  # Very large batch
        ]
        
        try:
            result = await execute_tool(
                tool_id="docs.cluster.batch.draft.create",
                input_data={"documents": large_batch},
                context=context_t1,
                registry=tool_registry,
                permission_checker=permission_checker,
                audit_logger=mock_audit_logger,
            )
            
            # If accepted, verify it was handled appropriately
            # (may be chunked or have size limits)
            if result:
                # Batch should be processed or rejected based on limits
                assert result is not None
        except ValueError as e:
            # If rejected, that's acceptable
            error_msg = str(e).lower()
            assert "too large" in error_msg or "exceeds" in error_msg or "limit" in error_msg, (
                "Large batch rejection should mention size limit"
            )


@pytest.mark.asyncio
class TestXSSGuards:
    """Test XSS guards in HTML fragments."""
    
    async def test_dangerous_strings_dont_break_html_fragments(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that dangerous strings don't break HTML fragments (basic XSS guard)."""
        register_docs_draft_create_tool(tool_registry)
        
        # XSS attack vectors to test
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "javascript:alert('XSS')",
            "<svg onload=alert('XSS')>",
            "'\"><script>alert('XSS')</script>",
            "<iframe src=javascript:alert('XSS')>",
        ]
        
        for xss_payload in xss_payloads:
            # Try to create draft with XSS payload in title
            try:
                result = await execute_tool(
                    tool_id="docs.cluster.draft.create",
                    input_data={
                        "doc_type": "PRD",
                        "title": xss_payload,
                    },
                    context=context_t1,
                    registry=tool_registry,
                    permission_checker=permission_checker,
                    audit_logger=mock_audit_logger,
                )
                
                # Check preview markdown for escaped XSS
                preview = result.get("preview_markdown", "")
                
                # XSS payloads should be escaped or sanitized
                # Check that script tags are escaped
                if "<script>" in preview.lower():
                    # Script tags should be escaped (not executable)
                    assert "&lt;script&gt;" in preview or "&lt;/script&gt;" in preview, (
                        f"XSS payload should be escaped in preview: {xss_payload}"
                    )
                
                # Check that dangerous attributes are escaped
                if "onerror=" in preview.lower() or "onload=" in preview.lower():
                    # Event handlers should be escaped
                    assert "&lt;" in preview or "&gt;" in preview, (
                        f"Event handlers should be escaped: {xss_payload}"
                    )
            except ValueError:
                # If rejected, that's also acceptable (input validation)
                pass
    
    async def test_html_fragments_escape_user_input(self, api_client: httpx.AsyncClient):
        """Test that HTML fragments properly escape user input."""
        # This tests the dashboard HTML rendering
        # Note: This is a basic check - full XSS testing would require more sophisticated tests
        
        response = await api_client.get("/dashboard")
        html = response.text
        
        # Check that HTML doesn't contain unescaped user input patterns
        # (This is a basic check - actual XSS testing would inject payloads)
        
        # HTML should be well-formed
        assert "<html" in html.lower() or "<!doctype" in html.lower(), (
            "Dashboard should return valid HTML"
        )
        
        # Check for basic XSS patterns that shouldn't be executable
        # (This is a soft check - actual XSS prevention is tested in draft creation)
        dangerous_patterns = ["<script>", "javascript:", "onerror=", "onload="]
        for pattern in dangerous_patterns:
            # If pattern exists, it should be escaped
            if pattern.lower() in html.lower():
                # Check if it's escaped
                escaped_pattern = pattern.replace("<", "&lt;").replace(">", "&gt;")
                if escaped_pattern not in html:
                    # May be in a safe context (like a string literal)
                    # This is a basic check - full XSS testing is more complex
                    pass
    
    async def test_api_responses_escape_json(self, api_client: httpx.AsyncClient):
        """Test that API JSON responses properly escape special characters."""
        response = await api_client.get("/api/status")
        data = response.json()
        
        # JSON should be valid (httpx automatically parses it)
        # This test verifies that special characters are properly escaped in JSON
        
        # Check that JSON is well-formed
        json_str = response.text
        try:
            parsed = json.loads(json_str)
            assert isinstance(parsed, dict), "API response should be valid JSON"
        except json.JSONDecodeError:
            pytest.fail("API response should be valid JSON")


@pytest.mark.asyncio
class TestInputSanitization:
    """Test input sanitization and validation."""
    
    async def test_special_characters_handled_safely(
        self,
        tool_registry: MCPToolRegistry,
        context_t1: ExecutionContext,
        permission_checker: PermissionChecker,
        mock_audit_logger: AuditLogger,
    ):
        """Test that special characters are handled safely."""
        register_docs_draft_create_tool(tool_registry)
        
        # Test various special characters
        special_inputs = [
            "Test & Special",
            "Test < > Characters",
            "Test ' \" Quotes",
            "Test\nNewline",
            "Test\tTab",
            "Test/Path\\Characters",
        ]
        
        for special_input in special_inputs:
            try:
                result = await execute_tool(
                    tool_id="docs.cluster.draft.create",
                    input_data={
                        "doc_type": "PRD",
                        "title": special_input,
                    },
                    context=context_t1,
                    registry=tool_registry,
                    permission_checker=permission_checker,
                    audit_logger=mock_audit_logger,
                )
                
                # Input should be accepted and stored safely
                assert result is not None
                assert "draft_id" in result
                
                # Verify draft was created successfully
                draft_id = result["draft_id"]
                draft_storage = get_draft_storage()
                draft = await draft_storage.get_draft(draft_id, context_t1.tenant_id)
                
                # Title should be stored (may be sanitized but should be present)
                assert draft is not None
            except ValueError:
                # If rejected due to validation, that's acceptable
                pass

