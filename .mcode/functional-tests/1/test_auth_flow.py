"""
Functional tests for Jellyfin authentication flow.

Authentication exercises the full server stack including session
management (SessionManager in Emby.Server.Implementations) and
the DI container with all renamed namespace registrations.
"""
import uuid
import requests
import pytest

BASE_URL = "http://localhost:8096"


def _auth_header(device_id=None):
    """Generate an auth header with a unique DeviceId to avoid session conflicts."""
    if device_id is None:
        device_id = f"ft-auth-{uuid.uuid4().hex[:8]}"
    return f'MediaBrowser Client="FTClient", Device="FTDevice", DeviceId="{device_id}", Version="1.0.0"'


class TestAuthenticateByName:
    """POST /Users/AuthenticateByName - login flow.

    Exercises SessionManager and authentication services which
    depend on Emby.Server.Implementations (renamed namespace target).
    """

    def test_authenticate_success(self, setup_wizard_and_auth):
        """Authenticate with valid credentials using a fresh DeviceId."""
        resp = requests.post(
            f"{BASE_URL}/Users/AuthenticateByName",
            json={"Username": "morphagent", "Pw": "admin123"},
            headers={
                "Content-Type": "application/json",
                "Authorization": _auth_header(),
            },
            timeout=10,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "AccessToken" in body
        assert body["User"]["Name"] == "morphagent"
        assert "Id" in body["User"]
        assert body["User"]["HasPassword"] is True

    def test_authenticate_wrong_password(self):
        resp = requests.post(
            f"{BASE_URL}/Users/AuthenticateByName",
            json={"Username": "morphagent", "Pw": "wrongpassword"},
            headers={
                "Content-Type": "application/json",
                "Authorization": _auth_header(),
            },
            timeout=10,
        )
        assert resp.status_code == 401

    def test_authenticate_nonexistent_user(self):
        resp = requests.post(
            f"{BASE_URL}/Users/AuthenticateByName",
            json={"Username": "nonexistent_user_ftrun", "Pw": "whatever"},
            headers={
                "Content-Type": "application/json",
                "Authorization": _auth_header(),
            },
            timeout=10,
        )
        assert resp.status_code == 401


class TestInvalidAuth:
    """Requests with invalid or missing auth tokens."""

    def test_invalid_token_returns_401(self):
        resp = requests.get(
            f"{BASE_URL}/Users/Me",
            headers={"Authorization": 'MediaBrowser Token="invalid_token_ftrun_nonexistent"'},
            timeout=10,
        )
        assert resp.status_code == 401

    def test_missing_auth_on_protected_endpoint(self):
        resp = requests.get(
            f"{BASE_URL}/Users/Me",
            timeout=10,
        )
        assert resp.status_code == 401
