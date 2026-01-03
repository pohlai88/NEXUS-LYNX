"""
HTML parsing and selector utilities.

Provides stable selectors using data-testid attributes to avoid brittle
CSS class assertions.
"""

from typing import List, Optional
from bs4 import BeautifulSoup, Tag


def parse_html(html: str) -> BeautifulSoup:
    """Parse HTML string into BeautifulSoup."""
    return BeautifulSoup(html, "html.parser")


def find_by_testid(soup: BeautifulSoup, testid: str) -> Optional[Tag]:
    """Find element by data-testid attribute."""
    return soup.find(attrs={"data-testid": testid})


def find_all_by_testid(soup: BeautifulSoup, testid: str) -> List[Tag]:
    """Find all elements by data-testid attribute."""
    return soup.find_all(attrs={"data-testid": testid})


def find_by_fragment(soup: BeautifulSoup, fragment_id: str) -> Optional[Tag]:
    """Find fragment container by data-fragment attribute."""
    return soup.find(attrs={"data-fragment": fragment_id})


def assert_testid_exists(soup: BeautifulSoup, testid: str, description: str = "") -> Tag:
    """Assert element with testid exists and return it."""
    element = find_by_testid(soup, testid)
    assert element is not None, (
        f"Element with data-testid='{testid}' not found. {description}"
    )
    return element


def assert_fragment_exists(soup: BeautifulSoup, fragment_id: str) -> Tag:
    """Assert fragment container exists and return it."""
    fragment = find_by_fragment(soup, fragment_id)
    assert fragment is not None, f"Fragment with data-fragment='{fragment_id}' not found"
    return fragment


def count_by_class(soup: BeautifulSoup, class_name: str) -> int:
    """Count elements by CSS class (fallback for legacy assertions)."""
    return len(soup.find_all(class_=class_name))


def assert_kpi_cards_exist(soup: BeautifulSoup, min_count: int = 4) -> List[Tag]:
    """Assert KPI cards exist (using testid or fallback to class)."""
    # Try testid first (preferred)
    cards = find_all_by_testid(soup, "kpi-card")
    
    # Fallback to class if testid not implemented yet
    if not cards:
        cards = soup.find_all(class_="na-card")
        # Filter to only KPI cards (those in na-grid-kpis)
        kpi_grid = soup.find(class_="na-grid-kpis")
        if kpi_grid:
            cards = kpi_grid.find_all(class_="na-card")
    
    assert len(cards) >= min_count, (
        f"Expected at least {min_count} KPI cards, found {len(cards)}"
    )
    return cards


def assert_status_badge_exists(soup: BeautifulSoup) -> Tag:
    """Assert status badge exists."""
    # Try testid first
    badge = find_by_testid(soup, "status-badge")
    
    # Fallback to class
    if not badge:
        badge = soup.find(class_="na-badge")
    
    assert badge is not None, "Status badge not found"
    return badge


def assert_services_list_exists(soup: BeautifulSoup) -> Tag:
    """Assert services list exists."""
    # Try testid first
    services = find_by_testid(soup, "services-list")
    
    # Fallback to finding by structure
    if not services:
        # Look for services card
        services_card = soup.find(string=lambda text: text and "System Health" in text)
        if services_card:
            services = services_card.find_parent(class_="na-card")
    
    assert services is not None, "Services list not found"
    return services


def assert_recent_activity_exists(soup: BeautifulSoup) -> Tag:
    """Assert recent activity list exists."""
    # Try testid first
    activity = find_by_testid(soup, "recent-activity")
    
    # Fallback to finding by structure
    if not activity:
        activity_card = soup.find(string=lambda text: text and "Activity Log" in text)
        if activity_card:
            activity = activity_card.find_parent(class_="na-card")
    
    assert activity is not None, "Recent activity list not found"
    return activity

