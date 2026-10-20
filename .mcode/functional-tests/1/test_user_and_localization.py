"""
Functional tests for Jellyfin user management and localization endpoints.

User management exercises SessionManager and UserManager from
Emby.Server.Implementations. Localization exercises LocalizationManager
which is registered through the server's DI container.
"""
import requests
import pytest

BASE_URL = "http://localhost:8096"


class TestUsersMe:
    """GET /Users/Me - current user info.

    Exercises the user management stack in Emby.Server.Implementations.
    """

    def test_users_me_success(self, auth_headers):
        resp = requests.get(
            f"{BASE_URL}/Users/Me",
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["Name"] == "morphagent"
        assert "Id" in body
        assert "Configuration" in body
        assert "Policy" in body
        assert body["HasPassword"] is True

    def test_users_me_has_policy(self, auth_headers):
        resp = requests.get(
            f"{BASE_URL}/Users/Me",
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        body = resp.json()
        policy = body["Policy"]
        assert "IsAdministrator" in policy
        assert policy["IsAdministrator"] is True


class TestUsersList:
    """GET /Users - list all users."""

    def test_users_list(self, auth_headers):
        resp = requests.get(
            f"{BASE_URL}/Users",
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        assert len(body) >= 1
        user_names = [u["Name"] for u in body]
        assert "morphagent" in user_names


class TestLocalizationCultures:
    """GET /Localization/Cultures - culture/language listing.

    Exercises LocalizationManager from Emby.Server.Implementations.
    """

    def test_cultures_returns_list(self, auth_headers):
        resp = requests.get(
            f"{BASE_URL}/Localization/Cultures",
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        assert len(body) > 100  # Should have hundreds of cultures

    def test_cultures_have_expected_fields(self, auth_headers):
        resp = requests.get(
            f"{BASE_URL}/Localization/Cultures",
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        body = resp.json()
        culture = body[0]
        assert "Name" in culture
        assert "DisplayName" in culture
        assert "TwoLetterISOLanguageName" in culture
        assert "ThreeLetterISOLanguageName" in culture

    def test_cultures_include_english(self, auth_headers):
        resp = requests.get(
            f"{BASE_URL}/Localization/Cultures",
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        body = resp.json()
        en_cultures = [c for c in body if c.get("TwoLetterISOLanguageName") == "en"]
        assert len(en_cultures) > 0, "English culture not found"


class TestLocalizationCountries:
    """GET /Localization/Countries - country listing."""

    def test_countries_returns_list(self, auth_headers):
        resp = requests.get(
            f"{BASE_URL}/Localization/Countries",
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
        assert len(body) > 50  # Should have many countries

    def test_countries_include_us(self, auth_headers):
        resp = requests.get(
            f"{BASE_URL}/Localization/Countries",
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        body = resp.json()
        us = [c for c in body if c.get("TwoLetterISORegionName") == "US"]
        assert len(us) > 0, "US country not found"
