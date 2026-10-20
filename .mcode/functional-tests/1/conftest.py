"""
Shared fixtures for Jellyfin backend functional tests.

Handles startup wizard completion, authentication, and health verification.
"""
import os
import requests
import pytest

BASE_URL = f"http://localhost:{os.environ.get('JELLYFIN_PORT', '8096')}"
AUTH_HEADER_TEMPLATE = 'MediaBrowser Client="FTClient", Device="FTDevice", DeviceId="ft-test-device", Version="1.0.0"'


@pytest.fixture(scope="session")
def base_url():
    """Return the base URL for the Jellyfin server."""
    return BASE_URL


@pytest.fixture(autouse=True)
def server_reachable():
    """Confirm the Jellyfin server is reachable before each test."""
    resp = requests.get(f"{BASE_URL}/System/Ping", timeout=5)
    assert resp.status_code == 200, f"Server not reachable: {resp.status_code}"


@pytest.fixture(scope="session")
def setup_wizard_and_auth():
    """
    Session-scoped fixture that ensures the startup wizard is completed
    and returns a valid authentication token.

    Idempotent: skips wizard steps if already completed.
    """
    # Check if wizard is already completed
    info = requests.get(f"{BASE_URL}/System/Info/Public", timeout=10).json()
    wizard_completed = info.get("StartupWizardCompleted", False)

    username = "morphagent"
    password = "admin123"

    if not wizard_completed:
        # Get the default user name
        user_resp = requests.get(f"{BASE_URL}/Startup/User", timeout=10)
        if user_resp.status_code == 200:
            default_user = user_resp.json()
            username = default_user.get("Name", username)

        # Set user credentials
        requests.post(
            f"{BASE_URL}/Startup/User",
            json={"Name": username, "Password": password},
            timeout=10,
        )

        # Set configuration
        requests.post(
            f"{BASE_URL}/Startup/Configuration",
            json={
                "UICulture": "en-US",
                "MetadataCountryCode": "US",
                "PreferredMetadataLanguage": "en",
            },
            timeout=10,
        )

        # Set remote access
        requests.post(
            f"{BASE_URL}/Startup/RemoteAccess",
            json={"EnableRemoteAccess": True, "EnableAutomaticPortMapping": False},
            timeout=10,
        )

        # Complete wizard
        requests.post(f"{BASE_URL}/Startup/Complete", timeout=10)

    # Authenticate
    auth_resp = requests.post(
        f"{BASE_URL}/Users/AuthenticateByName",
        json={"Username": username, "Pw": password},
        headers={
            "Content-Type": "application/json",
            "Authorization": AUTH_HEADER_TEMPLATE,
        },
        timeout=10,
    )

    if auth_resp.status_code != 200:
        pytest.fail(f"Authentication failed: {auth_resp.status_code} {auth_resp.text}")

    auth_data = auth_resp.json()
    token = auth_data["AccessToken"]
    user_id = auth_data["User"]["Id"]

    return {
        "token": token,
        "user_id": user_id,
        "username": username,
        "auth_header": f'MediaBrowser Token="{token}"',
    }


@pytest.fixture(scope="session")
def auth_headers(setup_wizard_and_auth):
    """Return headers dict with auth token for authenticated requests."""
    return {"Authorization": setup_wizard_and_auth["auth_header"]}
