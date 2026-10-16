"""Functional tests for Jellyfin system endpoints.

Validates that /System/Info/Public and /System/Info return correct data
after the Emby.Naming -> Jellyfin.Naming namespace migration.
"""

import requests
import pytest
import time

BASE_URL = "http://localhost:8096"
AUTH_HEADER_BASE = (
    'MediaBrowser Client="FTRunner", Device="FTDevice", '
    'DeviceId="ft-runner-001", Version="1.0"'
)


class TestSystemInfoPublic:
    """GET /System/Info/Public - No authentication required."""

    def test_system_info_public_happy_path(self):
        """Verify /System/Info/Public returns server name, version, and ID."""
        # May need to wait briefly for the server to finish full initialization
        resp = None
        for attempt in range(10):
            resp = requests.get(f"{BASE_URL}/System/Info/Public", timeout=10)
            if resp.status_code == 200:
                break
            time.sleep(2)
        assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
        body = resp.json()
        assert "ServerName" in body, "Response missing ServerName"
        assert "Version" in body, "Response missing Version"
        assert "Id" in body, "Response missing Id"
        assert body["Version"], "Version is empty"

    def test_system_info_public_startup_wizard_completed(self, setup_wizard_complete):
        """After setup, StartupWizardCompleted should be true."""
        resp = requests.get(f"{BASE_URL}/System/Info/Public", timeout=10)
        assert resp.status_code == 200
        body = resp.json()
        assert body.get("StartupWizardCompleted") is True


class TestSystemInfo:
    """GET /System/Info - Requires authentication."""

    def test_system_info_authenticated(self, auth_headers):
        """Verify /System/Info returns full server info with auth."""
        resp = requests.get(
            f"{BASE_URL}/System/Info", headers=auth_headers, timeout=10
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "ServerName" in body
        assert "Version" in body
        assert "OperatingSystem" in body
        assert body["Version"], "Version is empty"

    def test_system_info_unauthorized(self, setup_wizard_complete):
        """Verify /System/Info returns 401 without auth token (after wizard completed)."""
        resp = requests.get(f"{BASE_URL}/System/Info", timeout=10)
        assert resp.status_code == 401
