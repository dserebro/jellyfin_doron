"""Functional tests for Jellyfin authentication endpoints.

Validates that POST /Users/AuthenticateByName works correctly
after the Emby.Naming -> Jellyfin.Naming namespace migration.
"""

import requests
import pytest

BASE_URL = "http://localhost:8096"
# Use a DIFFERENT DeviceId than the shared auth fixture to avoid
# invalidating the session-scoped auth token
AUTH_HEADER_TEST = (
    'MediaBrowser Client="FTRunner", Device="FTAuthTest", '
    'DeviceId="ft-auth-test-001", Version="1.0"'
)
ADMIN_USER = "MorphSmokeAdmin"
ADMIN_PASS = "SmokeTest123!"


class TestAuthentication:
    """POST /Users/AuthenticateByName"""

    def test_authenticate_success(self, setup_wizard_complete):
        """Valid credentials return 200 with AccessToken and User object."""
        headers = {
            "Authorization": AUTH_HEADER_TEST,
            "Content-Type": "application/json",
        }
        body = {"Username": ADMIN_USER, "Pw": ADMIN_PASS}
        resp = requests.post(
            f"{BASE_URL}/Users/AuthenticateByName",
            json=body,
            headers=headers,
            timeout=10,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "AccessToken" in data, "Response missing AccessToken"
        assert "User" in data, "Response missing User"
        assert data["User"].get("Name") == ADMIN_USER
        assert data["AccessToken"], "AccessToken is empty"

    def test_authenticate_invalid_password(self, setup_wizard_complete):
        """Invalid password returns 401."""
        headers = {
            "Authorization": AUTH_HEADER_TEST,
            "Content-Type": "application/json",
        }
        body = {"Username": ADMIN_USER, "Pw": "WrongPassword123!"}
        resp = requests.post(
            f"{BASE_URL}/Users/AuthenticateByName",
            json=body,
            headers=headers,
            timeout=10,
        )
        assert resp.status_code == 401
