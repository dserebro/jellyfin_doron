"""
Functional tests for Jellyfin system endpoints.

These verify the server starts correctly after namespace renames
(Emby.Photos -> Jellyfin.Photos, Emby.Naming -> Jellyfin.Naming)
and dead code removal. The server's DI container must resolve all
services from renamed assemblies for these endpoints to work.
"""
import requests
import pytest

BASE_URL = "http://localhost:8096"


class TestSystemInfoPublic:
    """GET /System/Info/Public - no auth required.

    Exercises the full server startup including DI registration
    of all renamed namespaces. Returns server identity info.
    """

    def test_system_info_public_success(self):
        resp = requests.get(f"{BASE_URL}/System/Info/Public", timeout=10)
        assert resp.status_code == 200
        body = resp.json()
        assert body["ProductName"] == "Jellyfin Server"
        assert body["Version"] == "12.0.0"
        assert "Id" in body
        assert "ServerName" in body
        assert body["StartupWizardCompleted"] is True

    def test_system_info_public_has_local_address(self):
        resp = requests.get(f"{BASE_URL}/System/Info/Public", timeout=10)
        assert resp.status_code == 200
        body = resp.json()
        assert "LocalAddress" in body
        assert "127.0.0.1" in body["LocalAddress"] or "localhost" in body["LocalAddress"]


class TestSystemPing:
    """GET /System/Ping - no auth required.

    Basic reachability verification for the server process.
    """

    def test_system_ping_get(self):
        resp = requests.get(f"{BASE_URL}/System/Ping", timeout=10)
        assert resp.status_code == 200

    def test_system_ping_post(self):
        resp = requests.post(f"{BASE_URL}/System/Ping", timeout=10)
        assert resp.status_code == 200


class TestSystemInfoAuthenticated:
    """GET /System/Info - requires authentication.

    Returns detailed system info including paths and configuration.
    Verifies the full server stack is operational with all DI
    registrations intact after namespace renames.
    """

    def test_system_info_full(self, auth_headers):
        resp = requests.get(
            f"{BASE_URL}/System/Info",
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "ProgramDataPath" in body
        assert "LogPath" in body
        assert "CachePath" in body
        assert body["CanSelfRestart"] is True
        assert body["SupportsLibraryMonitor"] is True

    def test_system_info_has_cast_receivers(self, auth_headers):
        resp = requests.get(
            f"{BASE_URL}/System/Info",
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "CastReceiverApplications" in body
        assert len(body["CastReceiverApplications"]) > 0


class TestBrandingConfiguration:
    """GET /Branding/Configuration - no auth required.

    Verifies the configuration subsystem works correctly.
    The configuration manager lives in Emby.Server.Implementations.
    """

    def test_branding_config_success(self):
        resp = requests.get(f"{BASE_URL}/Branding/Configuration", timeout=10)
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, dict)
        assert "SplashscreenEnabled" in body
