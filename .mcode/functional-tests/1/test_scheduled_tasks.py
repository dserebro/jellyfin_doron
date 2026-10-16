"""Functional tests for Jellyfin scheduled tasks endpoints.

Validates that /ScheduledTasks returns correct data after
the Emby.Naming -> Jellyfin.Naming namespace migration.
"""

import requests
import pytest

BASE_URL = "http://localhost:8096"


class TestScheduledTasks:
    """GET /ScheduledTasks and GET /ScheduledTasks/{id}"""

    def test_list_scheduled_tasks(self, auth_headers):
        """Returns a list of scheduled tasks with at least 1 entry."""
        resp = requests.get(
            f"{BASE_URL}/ScheduledTasks",
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        tasks = resp.json()
        assert isinstance(tasks, list)
        assert len(tasks) >= 1, f"Expected >=1 task, got {len(tasks)}"
        # Verify structure
        first = tasks[0]
        assert "Id" in first, "Task missing Id"
        assert "Name" in first, "Task missing Name"
        assert "State" in first, "Task missing State"

    def test_get_task_detail(self, auth_headers):
        """Fetch a specific task by ID and verify its detail."""
        # First list tasks to get a valid ID
        list_resp = requests.get(
            f"{BASE_URL}/ScheduledTasks",
            headers=auth_headers,
            timeout=10,
        )
        list_resp.raise_for_status()
        tasks = list_resp.json()
        assert len(tasks) >= 1, "No tasks available"
        task_id = tasks[0]["Id"]

        # Get task detail
        resp = requests.get(
            f"{BASE_URL}/ScheduledTasks/{task_id}",
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 200
        detail = resp.json()
        assert detail["Id"] == task_id
        assert "Name" in detail
        assert "State" in detail
        assert "Triggers" in detail, "Task detail missing Triggers"

    def test_get_task_not_found(self, auth_headers):
        """Requesting a non-existent task ID returns 404."""
        resp = requests.get(
            f"{BASE_URL}/ScheduledTasks/nonexistent-task-id-99999",
            headers=auth_headers,
            timeout=10,
        )
        assert resp.status_code == 404
