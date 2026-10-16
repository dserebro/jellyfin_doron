"""Functional tests for Jellyfin API keys CRUD endpoints.

Validates that /Auth/Keys create/list/delete works correctly after
the Emby.Naming -> Jellyfin.Naming namespace migration.
"""

import requests
import uuid

BASE_URL = "http://localhost:8096"
# Unique app name per test run to avoid collisions
APP_NAME = f"FTKeyTest_{uuid.uuid4().hex[:8]}"


class TestApiKeysCrud:
    """POST /Auth/Keys, GET /Auth/Keys, DELETE /Auth/Keys/{key}"""

    def test_api_keys_create_list_delete(self, auth_headers):
        """Full CRUD cycle: create, verify exists, delete, verify gone."""
        # CREATE
        create_resp = requests.post(
            f"{BASE_URL}/Auth/Keys",
            params={"app": APP_NAME},
            headers=auth_headers,
            timeout=10,
        )
        assert create_resp.status_code == 204, (
            f"Expected 204 on key creation, got {create_resp.status_code}"
        )

        # LIST and find the created key
        list_resp = requests.get(
            f"{BASE_URL}/Auth/Keys",
            headers=auth_headers,
            timeout=10,
        )
        assert list_resp.status_code == 200
        keys_data = list_resp.json()
        assert "Items" in keys_data
        matching = [
            k for k in keys_data["Items"] if k.get("AppName") == APP_NAME
        ]
        assert len(matching) == 1, (
            f"Expected 1 key with AppName={APP_NAME}, found {len(matching)}"
        )
        key_token = matching[0]["AccessToken"]

        # DELETE
        del_resp = requests.delete(
            f"{BASE_URL}/Auth/Keys/{key_token}",
            headers=auth_headers,
            timeout=10,
        )
        assert del_resp.status_code == 204

        # VERIFY DELETED
        verify_resp = requests.get(
            f"{BASE_URL}/Auth/Keys",
            headers=auth_headers,
            timeout=10,
        )
        verify_resp.raise_for_status()
        remaining = [
            k
            for k in verify_resp.json()["Items"]
            if k.get("AppName") == APP_NAME
        ]
        assert len(remaining) == 0, "API key still exists after deletion"
