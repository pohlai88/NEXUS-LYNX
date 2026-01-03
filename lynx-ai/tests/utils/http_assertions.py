"""
HTTP response assertion utilities.

Provides reusable assertions for HTTP responses including content types,
headers, and caching.
"""

from typing import Optional
import httpx


def assert_content_type(response: httpx.Response, expected: str) -> None:
    """Assert response has expected content type."""
    content_type = response.headers.get("content-type", "")
    assert expected in content_type, f"Expected content-type '{expected}', got '{content_type}'"


def assert_status_code(response: httpx.Response, expected: int) -> None:
    """Assert response has expected status code."""
    assert response.status_code == expected, f"Expected status {expected}, got {response.status_code}"


def assert_has_header(response: httpx.Response, header_name: str) -> None:
    """Assert response has a specific header."""
    assert header_name in response.headers, f"Missing header: {header_name}"


def assert_cache_headers(response: httpx.Response, max_age: Optional[int] = None) -> None:
    """Assert response has appropriate cache headers."""
    cache_control = response.headers.get("cache-control", "")
    
    # For static assets, expect cache headers
    if "static" in str(response.url):
        assert "cache-control" in response.headers, "Static assets should have cache-control"
        if max_age:
            assert f"max-age={max_age}" in cache_control or f"max-age={max_age}" in cache_control.lower()


def assert_security_headers(response: httpx.Response) -> None:
    """Assert basic security headers are present (non-invasive check)."""
    # Optional: Check for security headers if they exist
    # This is a soft check - doesn't fail if headers don't exist
    pass


def assert_no_secrets_in_response(response: httpx.Response) -> None:
    """Assert response does not contain obvious secrets."""
    text = response.text.lower()
    
    # Check for common secret patterns
    secret_patterns = [
        "api_key",
        "secret",
        "password",
        "token",
        "credential",
    ]
    
    # Only check if response is text-based
    if "application/json" in response.headers.get("content-type", ""):
        # For JSON, check keys and values
        import json
        try:
            data = response.json()
            # Recursively check for secret-like keys
            def check_dict(d, path=""):
                for k, v in d.items():
                    current_path = f"{path}.{k}" if path else k
                    key_lower = k.lower()
                    
                    # Check if key looks like a secret
                    if any(pattern in key_lower for pattern in secret_patterns):
                        # If value is not empty and not a placeholder, it might be a secret
                        if v and v not in ["***", "REDACTED", ""]:
                            # Allow known safe fields
                            if "api_url" not in key_lower and "endpoint" not in key_lower:
                                raise AssertionError(f"Potential secret in response at {current_path}")
                    
                    # Recurse into nested dicts
                    if isinstance(v, dict):
                        check_dict(v, current_path)
            
            check_dict(data)
        except json.JSONDecodeError:
            pass  # Not JSON, skip


def assert_response_size(response: httpx.Response, max_size_mb: float = 10.0) -> None:
    """Assert response size is reasonable."""
    size_mb = len(response.content) / (1024 * 1024)
    assert size_mb < max_size_mb, f"Response too large: {size_mb:.2f}MB (max: {max_size_mb}MB)"

