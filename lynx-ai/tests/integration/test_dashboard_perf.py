"""
Dashboard performance tests - Response time and concurrency.

Tests response times with percentile measurements (p95) to avoid false
failures from cold starts. Includes concurrency smoke tests.
"""

import pytest
import httpx
import asyncio
import time
from typing import List


def calculate_percentile(times: List[float], percentile: float) -> float:
    """Calculate percentile from list of times."""
    sorted_times = sorted(times)
    index = int(len(sorted_times) * percentile / 100)
    return sorted_times[index] if index < len(sorted_times) else sorted_times[-1]


@pytest.mark.asyncio
@pytest.mark.performance
class TestResponseTimes:
    """Test response time requirements."""
    
    async def test_dashboard_response_time_p95(self, api_client: httpx.AsyncClient):
        """
        Test dashboard response time p95 < 350ms.
        
        Uses warm-up request + N=20 requests to avoid cold start issues.
        """
        # Warm-up request
        await api_client.get("/")
        
        # N=20 requests
        times = []
        for _ in range(20):
            start = time.time()
            response = await api_client.get("/")
            elapsed = (time.time() - start) * 1000  # Convert to ms
            assert response.status_code == 200
            times.append(elapsed)
        
        # Calculate p95
        p95 = calculate_percentile(times, 95)
        
        assert p95 < 350, (
            f"Dashboard p95 response time {p95:.2f}ms exceeds 350ms requirement. "
            f"Times: min={min(times):.2f}ms, max={max(times):.2f}ms, avg={sum(times)/len(times):.2f}ms"
        )
    
    async def test_fragment_response_time_p95(self, api_client: httpx.AsyncClient):
        """Test fragment response time p95 < 200ms."""
        fragments = ["_kpis", "_services", "_recent", "_cockpit"]
        
        for fragment in fragments:
            # Warm-up
            await api_client.get(f"/dashboard/{fragment}")
            
            # N=20 requests
            times = []
            for _ in range(20):
                start = time.time()
                response = await api_client.get(f"/dashboard/{fragment}")
                elapsed = (time.time() - start) * 1000
                assert response.status_code == 200
                times.append(elapsed)
            
            # Calculate p95
            p95 = calculate_percentile(times, 95)
            
            assert p95 < 200, (
                f"Fragment {fragment} p95 response time {p95:.2f}ms exceeds 200ms requirement. "
                f"Times: min={min(times):.2f}ms, max={max(times):.2f}ms, avg={sum(times)/len(times):.2f}ms"
            )
    
    async def test_health_endpoint_response_time(self, api_client: httpx.AsyncClient):
        """Test /health endpoint response time is fast."""
        # Warm-up
        await api_client.get("/health")
        
        # N=20 requests
        times = []
        for _ in range(20):
            start = time.time()
            response = await api_client.get("/health")
            elapsed = (time.time() - start) * 1000
            assert response.status_code == 200
            times.append(elapsed)
        
        # Health should be very fast (p95 < 100ms)
        p95 = calculate_percentile(times, 95)
        
        assert p95 < 100, (
            f"Health endpoint p95 response time {p95:.2f}ms exceeds 100ms. "
            f"Times: min={min(times):.2f}ms, max={max(times):.2f}ms, avg={sum(times)/len(times):.2f}ms"
        )
    
    async def test_api_status_response_time(self, api_client: httpx.AsyncClient):
        """Test /api/status response time."""
        # Warm-up
        await api_client.get("/api/status")
        
        # N=20 requests
        times = []
        for _ in range(20):
            start = time.time()
            response = await api_client.get("/api/status")
            elapsed = (time.time() - start) * 1000
            assert response.status_code == 200
            times.append(elapsed)
        
        # Status should be reasonably fast (p95 < 350ms, same as dashboard)
        p95 = calculate_percentile(times, 95)
        
        assert p95 < 350, (
            f"Status API p95 response time {p95:.2f}ms exceeds 350ms. "
            f"Times: min={min(times):.2f}ms, max={max(times):.2f}ms, avg={sum(times)/len(times):.2f}ms"
        )


@pytest.mark.asyncio
@pytest.mark.performance
class TestConcurrency:
    """Test concurrent request handling."""
    
    async def test_concurrent_kpi_requests(self, api_client: httpx.AsyncClient):
        """Test handling 10 concurrent requests to KPI fragment."""
        async def make_request():
            response = await api_client.get("/dashboard/_kpis")
            return response.status_code == 200
        
        # Fire 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(results), "All concurrent requests should succeed"
        assert len(results) == 10, "Should handle 10 concurrent requests"
    
    async def test_concurrent_dashboard_requests(self, api_client: httpx.AsyncClient):
        """Test handling 10 concurrent requests to main dashboard."""
        async def make_request():
            response = await api_client.get("/")
            return response.status_code == 200
        
        # Fire 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(results), "All concurrent dashboard requests should succeed"
    
    async def test_concurrent_mixed_requests(self, api_client: httpx.AsyncClient):
        """Test handling concurrent requests to different endpoints."""
        async def make_request(endpoint):
            response = await api_client.get(endpoint)
            return response.status_code == 200
        
        # Mix of endpoints
        endpoints = ["/", "/health", "/api/status", "/dashboard/_kpis", "/dashboard/_services"]
        
        # Fire 5 requests to each endpoint concurrently
        tasks = [make_request(ep) for ep in endpoints * 5]
        results = await asyncio.gather(*tasks)
        
        # All should succeed
        assert all(results), "All concurrent mixed requests should succeed"
        assert len(results) == 25, "Should handle 25 concurrent mixed requests"
    
    async def test_concurrent_requests_average_time(self, api_client: httpx.AsyncClient):
        """Test average response time under concurrent load."""
        async def make_request():
            start = time.time()
            response = await api_client.get("/dashboard/_kpis")
            elapsed = (time.time() - start) * 1000
            return response.status_code == 200, elapsed
        
        # Fire 10 concurrent requests
        tasks = [make_request() for _ in range(10)]
        results = await asyncio.gather(*tasks)
        
        # Extract times
        times = [elapsed for success, elapsed in results if success]
        
        # Average should be reasonable (under 500ms even under load)
        if times:
            avg_time = sum(times) / len(times)
            assert avg_time < 500, (
                f"Average response time under concurrent load {avg_time:.2f}ms exceeds 500ms"
            )

