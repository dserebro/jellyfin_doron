"""Functional tests for Jellyfin localization endpoints.

Validates that /Localization/Cultures and /Localization/ParentalRatings
return correct data after the Emby.Naming -> Jellyfin.Naming migration.
"""

import requests

BASE_URL = "http://localhost:8096"


class TestLocalizationCultures:
    """GET /Localization/Cultures"""

    def test_cultures_happy_path(self, auth_headers):
        """Returns a list of cultures with at least 5 entries."""
        resp = requests.get(
            f"{BASE_URL}/Localization/Cultures",
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        cultures = resp.json()
        assert isinstance(cultures, list)
        assert len(cultures) >= 5, f"Expected >=5 cultures, got {len(cultures)}"
        # Verify structure of culture entries
        first = cultures[0]
        assert "Name" in first, "Culture entry missing Name"
        assert "DisplayName" in first, "Culture entry missing DisplayName"


class TestLocalizationParentalRatings:
    """GET /Localization/ParentalRatings"""

    def test_parental_ratings_happy_path(self, auth_headers):
        """Returns a list of parental ratings with at least 1 entry."""
        resp = requests.get(
            f"{BASE_URL}/Localization/ParentalRatings",
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        ratings = resp.json()
        assert isinstance(ratings, list)
        assert len(ratings) >= 1, f"Expected >=1 rating, got {len(ratings)}"
        # Verify structure: all entries have Name, most have Value
        # ("Unrated" is a special entry without a Value field)
        for rating in ratings:
            assert "Name" in rating, "Rating entry missing Name"
        # Check that at least some entries have the full structure
        rated = [r for r in ratings if "Value" in r]
        assert len(rated) >= 1, "No ratings with Value field found"
