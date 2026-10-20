"""
Functional tests for Jellyfin library endpoints.

These endpoints exercise the renamed namespace code paths:
- ItemTypeLookup (relocated from Data/ to Library/) via item queries
- Jellyfin.Naming via library resolvers and available options
- Jellyfin.Photos via photo type registration in library options
"""
import requests
import pytest

BASE_URL = "http://localhost:8096"


class TestItemsQuery:
    """GET /Items - exercises ItemTypeLookup and library resolvers.

    The Items endpoint queries the database through BaseItemRepository
    which uses ItemTypeLookup (relocated from Data/ to Library/) to
    map BaseItemKind enums to database type strings.
    """

    def test_items_list_empty_library(self, auth_headers):
        resp = requests.get(
            f"{BASE_URL}/Items",
            params={"Recursive": "true", "Limit": 10},
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "Items" in body
        assert "TotalRecordCount" in body
        assert isinstance(body["Items"], list)
        assert body["TotalRecordCount"] == 0

    def test_items_with_type_filter(self, auth_headers):
        """Exercises ItemTypeLookup type mapping for Movie type."""
        resp = requests.get(
            f"{BASE_URL}/Items",
            params={"Recursive": "true", "IncludeItemTypes": "Movie", "Limit": 5},
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "Items" in body
        assert "TotalRecordCount" in body

    def test_items_with_series_type_filter(self, auth_headers):
        """Exercises ItemTypeLookup type mapping for Series type."""
        resp = requests.get(
            f"{BASE_URL}/Items",
            params={"Recursive": "true", "IncludeItemTypes": "Series", "Limit": 5},
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "Items" in body

    def test_items_with_photo_type_filter(self, auth_headers):
        """Exercises ItemTypeLookup mapping for Photo type (Jellyfin.Photos)."""
        resp = requests.get(
            f"{BASE_URL}/Items",
            params={"Recursive": "true", "IncludeItemTypes": "Photo", "Limit": 5},
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "Items" in body

    def test_items_with_music_album_type_filter(self, auth_headers):
        """Exercises ItemTypeLookup mapping for MusicAlbum type (Jellyfin.Naming audio)."""
        resp = requests.get(
            f"{BASE_URL}/Items",
            params={"Recursive": "true", "IncludeItemTypes": "MusicAlbum", "Limit": 5},
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "Items" in body


class TestItemsCounts:
    """GET /Items/Counts - exercises ItemTypeLookup for all item types.

    Returns counts per item type. The counting logic goes through
    ItemCountService which uses ItemTypeLookup to resolve type names.
    """

    def test_items_counts_returns_all_types(self, auth_headers):
        resp = requests.get(
            f"{BASE_URL}/Items/Counts",
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        body = resp.json()
        expected_keys = [
            "MovieCount",
            "SeriesCount",
            "EpisodeCount",
            "ArtistCount",
            "ProgramCount",
            "TrailerCount",
            "SongCount",
            "AlbumCount",
            "MusicVideoCount",
            "BoxSetCount",
            "BookCount",
            "ItemCount",
        ]
        for key in expected_keys:
            assert key in body, f"Missing count key: {key}"
            assert isinstance(body[key], int), f"{key} should be int"


class TestLibraryAvailableOptions:
    """GET /Libraries/AvailableOptions - exercises library type registration.

    Returns available library content types and their metadata providers.
    The TypeOptions include types that depend on Jellyfin.Naming resolvers
    (Series, Movie, etc.) and Jellyfin.Photos (Photo type).
    """

    def test_library_options_success(self, auth_headers):
        resp = requests.get(
            f"{BASE_URL}/Libraries/AvailableOptions",
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "TypeOptions" in body
        assert "MetadataSavers" in body
        assert "MetadataReaders" in body
        assert len(body["TypeOptions"]) > 0

    def test_library_options_has_expected_types(self, auth_headers):
        """Verify that content types exercising renamed namespaces are present."""
        resp = requests.get(
            f"{BASE_URL}/Libraries/AvailableOptions",
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        body = resp.json()
        type_names = [opt["Type"] for opt in body["TypeOptions"]]
        # These types depend on Jellyfin.Naming resolvers being properly registered
        assert "Series" in type_names, "Series type missing (depends on Jellyfin.Naming)"
        assert "Movie" in type_names, "Movie type missing (depends on Jellyfin.Naming)"
        assert "Episode" in type_names, "Episode type missing (depends on Jellyfin.Naming)"

    def test_library_options_has_nfo_metadata(self, auth_headers):
        resp = requests.get(
            f"{BASE_URL}/Libraries/AvailableOptions",
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        body = resp.json()
        saver_names = [s["Name"] for s in body["MetadataSavers"]]
        assert "Nfo" in saver_names


class TestVirtualFolders:
    """GET /Library/VirtualFolders - library structure management.

    Exercises LibraryManager which depends on Jellyfin.Naming
    for resolving media types within library folders.
    """

    def test_virtual_folders_list(self, auth_headers):
        resp = requests.get(
            f"{BASE_URL}/Library/VirtualFolders",
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        body = resp.json()
        assert isinstance(body, list)
