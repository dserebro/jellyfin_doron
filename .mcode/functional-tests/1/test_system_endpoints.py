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


class TestScheduledTasks:
    """GET /ScheduledTasks - requires authentication.

    Exercises the TaskManager and DI-resolved task registrations from
    Emby.Server.Implementations. The server must resolve all IScheduledTask
    and ILibraryPostScanTask implementations (including the restored
    CleanDatabaseScheduledTask) without errors for the server to start
    and this endpoint to work.
    """

    def test_scheduled_tasks_list(self, auth_headers):
        resp = requests.get(
            f"{BASE_URL}/ScheduledTasks",
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        assert len(body) >= 15  # Server has ~19 scheduled tasks
        # Verify task structure
        task = body[0]
        assert "Name" in task
        assert "Key" in task
        assert "State" in task
        assert "Category" in task

    def test_scheduled_tasks_has_library_scan(self, auth_headers):
        """Verify Scan Media Library task exists - this task triggers
        ILibraryPostScanTask implementations like CleanDatabaseScheduledTask."""
        resp = requests.get(
            f"{BASE_URL}/ScheduledTasks",
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        body = resp.json()
        task_keys = [t["Key"] for t in body]
        assert "RefreshLibrary" in task_keys, "Scan Media Library task not found"

    def test_scheduled_tasks_has_maintenance_tasks(self, auth_headers):
        """Verify maintenance tasks exist - these share the Emby.Server.Implementations
        namespace with CleanDatabaseScheduledTask."""
        resp = requests.get(
            f"{BASE_URL}/ScheduledTasks",
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        body = resp.json()
        categories = set(t["Category"] for t in body)
        assert "Maintenance" in categories
        assert "Library" in categories
        # Maintenance tasks from Emby.Server.Implementations
        task_keys = [t["Key"] for t in body]
        assert "OptimizeDatabaseTask" in task_keys
        assert "CleanActivityLog" in task_keys
