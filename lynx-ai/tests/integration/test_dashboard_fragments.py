"""
Dashboard fragment tests - HTML parsing and structure.

Uses stable selectors (data-testid) to avoid brittle CSS class assertions.
Falls back to class-based selectors for backward compatibility.
"""

import pytest
import httpx
from tests.utils.html_selectors import (
    parse_html,
    assert_kpi_cards_exist,
    assert_status_badge_exists,
    assert_services_list_exists,
    assert_recent_activity_exists,
    find_by_testid,
    find_by_fragment,
)


@pytest.mark.asyncio
class TestKPIFragment:
    """Test KPI fragment rendering."""
    
    async def test_fragment_kpis_contains_cards(self, api_client: httpx.AsyncClient):
        """Test KPI fragment contains KPI cards."""
        response = await api_client.get("/dashboard/_kpis")
        assert response.status_code == 200
        
        soup = parse_html(response.text)
        cards = assert_kpi_cards_exist(soup, min_count=4)
        
        # Verify cards have content
        for card in cards:
            assert card.get_text(strip=True), "KPI card should have content"
    
    async def test_fragment_kpis_has_grid_structure(self, api_client: httpx.AsyncClient):
        """Test KPI fragment has grid layout structure."""
        response = await api_client.get("/dashboard/_kpis")
        soup = parse_html(response.text)
        
        # Look for grid container (class or testid)
        grid = find_by_testid(soup, "kpi-grid")
        if not grid:
            grid = soup.find(class_="na-grid-kpis")
        
        assert grid is not None, "KPI grid container should exist"


@pytest.mark.asyncio
class TestServicesFragment:
    """Test services fragment rendering."""
    
    async def test_fragment_services_contains_list(self, api_client: httpx.AsyncClient):
        """Test services fragment contains services list."""
        response = await api_client.get("/dashboard/_services")
        assert response.status_code == 200
        
        soup = parse_html(response.text)
        services = assert_services_list_exists(soup)
        
        # Verify services list has content
        assert services.get_text(strip=True), "Services list should have content"
    
    async def test_fragment_services_shows_kernel_status(self, api_client: httpx.AsyncClient):
        """Test services fragment shows Kernel API status."""
        response = await api_client.get("/dashboard/_services")
        soup = parse_html(response.text)
        
        # Look for Kernel API entry
        text = soup.get_text()
        assert "Kernel" in text or "kernel" in text.lower(), "Should show Kernel API status"
    
    async def test_fragment_services_shows_supabase_status(self, api_client: httpx.AsyncClient):
        """Test services fragment shows Supabase status."""
        response = await api_client.get("/dashboard/_services")
        soup = parse_html(response.text)
        
        # Look for Supabase entry
        text = soup.get_text()
        assert "Supabase" in text or "supabase" in text.lower(), "Should show Supabase status"


@pytest.mark.asyncio
class TestRecentFragment:
    """Test recent activity fragment rendering."""
    
    async def test_fragment_recent_contains_activity(self, api_client: httpx.AsyncClient):
        """Test recent activity fragment contains activity list."""
        response = await api_client.get("/dashboard/_recent")
        assert response.status_code == 200
        
        soup = parse_html(response.text)
        activity = assert_recent_activity_exists(soup)
        
        # Verify activity list exists (may be empty)
        assert activity is not None, "Recent activity container should exist"
    
    async def test_fragment_recent_handles_empty_state(self, api_client: httpx.AsyncClient):
        """Test recent activity fragment handles empty state gracefully."""
        response = await api_client.get("/dashboard/_recent")
        assert response.status_code == 200
        
        soup = parse_html(response.text)
        # Should render something even if no activity
        assert soup.get_text(strip=True), "Should render empty state message"


@pytest.mark.asyncio
class TestCockpitFragment:
    """Test cockpit fragment rendering."""
    
    async def test_fragment_cockpit_contains_stage(self, api_client: httpx.AsyncClient):
        """Test cockpit fragment contains current stage."""
        response = await api_client.get("/dashboard/_cockpit")
        assert response.status_code == 200
        
        soup = parse_html(response.text)
        text = soup.get_text()
        
        # Should show stage information
        assert "STAGING" in text or "PROD" in text or "stage" in text.lower(), (
            "Should show current stage"
        )
    
    async def test_fragment_cockpit_has_structure(self, api_client: httpx.AsyncClient):
        """Test cockpit fragment has expected structure."""
        response = await api_client.get("/dashboard/_cockpit")
        soup = parse_html(response.text)
        
        # Look for cockpit card
        cockpit = find_by_testid(soup, "developer-cockpit")
        if not cockpit:
            cockpit = soup.find(string=lambda t: t and "Developer Cockpit" in t)
            if cockpit:
                cockpit = cockpit.find_parent(class_="na-card")
        
        assert cockpit is not None, "Cockpit container should exist"


@pytest.mark.asyncio
class TestMainDashboard:
    """Test main dashboard page structure."""
    
    async def test_dashboard_contains_all_fragments(self, api_client: httpx.AsyncClient):
        """Test main dashboard contains all fragment containers."""
        response = await api_client.get("/")
        assert response.status_code == 200
        
        soup = parse_html(response.text)
        
        # Check for fragment containers (by id or data-fragment)
        fragments = ["kpis", "services", "recent", "cockpit"]
        for fragment_id in fragments:
            fragment = find_by_fragment(soup, fragment_id)
            if not fragment:
                # Fallback: check for id attribute
                fragment = soup.find(id=f"fragment-{fragment_id}")
            
            assert fragment is not None, f"Fragment container for '{fragment_id}' should exist"
    
    async def test_dashboard_has_status_badge(self, api_client: httpx.AsyncClient):
        """Test main dashboard has status badge."""
        response = await api_client.get("/")
        soup = parse_html(response.text)
        
        badge = assert_status_badge_exists(soup)
        assert badge is not None, "Status badge should exist in header"
    
    async def test_dashboard_includes_css(self, api_client: httpx.AsyncClient):
        """Test main dashboard includes CSS."""
        response = await api_client.get("/")
        soup = parse_html(response.text)
        
        # Check for style tag or link to CSS
        has_css = (
            soup.find("style") is not None or
            soup.find("link", rel="stylesheet") is not None
        )
        assert has_css, "Dashboard should include CSS"
    
    async def test_dashboard_includes_js(self, api_client: httpx.AsyncClient):
        """Test main dashboard includes JavaScript."""
        response = await api_client.get("/")
        soup = parse_html(response.text)
        
        # Check for script tag
        scripts = soup.find_all("script")
        assert len(scripts) > 0, "Dashboard should include JavaScript"

