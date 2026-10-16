"""Shared fixtures for Jellyfin functional tests."""

import requests
import pytest
import time

BASE_URL = "http://localhost:8096"
AUTH_HEADER_BASE = (
    'MediaBrowser Client="FTRunner", Device="FTDevice", '
    'DeviceId="ft-runner-001", Version="1.0"'
)
ADMIN_USER = "MorphSmokeAdmin"
ADMIN_PASS = "SmokeTest123!"


@pytest.fixture(autouse=True)
def health_check():
    """Confirm the Jellyfin server is reachable before running any test."""
    resp = requests.get(f"{BASE_URL}/health", timeout=10)
    assert resp.status_code == 200, f"Health check failed: {resp.status_code}"
    assert resp.text.strip() == "Healthy", f"Server not healthy: {resp.text}"


@pytest.fixture(scope="session")
def setup_wizard_complete():
    """Ensure the startup wizard is completed. Session-scoped so it runs once."""
    # Wait for /System/Info/Public to be available (may return 503 during startup)
    info = None
    for attempt in range(20):
        resp = requests.get(f"{BASE_URL}/System/Info/Public", timeout=10)
        if resp.status_code == 200:
            info = resp.json()
            break
        time.sleep(3)
    assert info is not None, "Server never returned 200 for /System/Info/Public"

    if not info.get("StartupWizardCompleted", False):
        # Complete the first-time setup
        headers = {"Authorization": AUTH_HEADER_BASE}

        # Initialize the first user
        requests.get(f"{BASE_URL}/Startup/User", headers=headers, timeout=10)

        # Set admin username and password
        user_body = {"Name": ADMIN_USER, "Password": ADMIN_PASS}
        requests.post(
            f"{BASE_URL}/Startup/User",
            json=user_body,
            headers=headers,
            timeout=10,
        )

        # Complete the wizard
        requests.post(
            f"{BASE_URL}/Startup/Complete",
            headers=headers,
            timeout=10,
        )

        # Brief pause to let the server finalize
        time.sleep(2)

    return True


@pytest.fixture(scope="session")
def auth_token(setup_wizard_complete):
    """Authenticate and return an access token. Session-scoped."""
    headers = {
        "Authorization": AUTH_HEADER_BASE,
        "Content-Type": "application/json",
    }
    body = {"Username": ADMIN_USER, "Pw": ADMIN_PASS}
    resp = requests.post(
        f"{BASE_URL}/Users/AuthenticateByName",
        json=body,
        headers=headers,
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    token = data.get("AccessToken")
    assert token, "Failed to obtain access token"
    return token


@pytest.fixture(scope="session")
def auth_headers(auth_token):
    """Return headers with the auth token for authenticated requests."""
    return {
        "Authorization": (
            f'MediaBrowser Token="{auth_token}", Client="FTRunner", '
            f'Device="FTDevice", DeviceId="ft-runner-001", Version="1.0"'
        ),
    }
