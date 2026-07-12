from sqlalchemy import inspect

from tests.conftest import post_with_csrf, patch_with_csrf, delete_with_csrf

BASE = {
    "title": "Standup", "start": "2026-07-13T09:00:00", "end": "2026-07-13T09:30:00"
}
RANGE = "start=2026-07-01T00:00:00&end=2026-09-30T00:00:00"


def _list(client):
    return client.get(f"/api/tasks?{RANGE}").json()


def test_create_without_repeat_makes_one_task(regular_client):
    post_with_csrf(regular_client, "/api/tasks", {**BASE, "repeat_weeks": 0})
    assert len(_list(regular_client)) == 1


def test_create_with_repeat_spawns_weekly_copies(regular_client):
    post_with_csrf(regular_client, "/api/tasks", {**BASE, "repeat_weeks": 3})
    tasks = sorted(_list(regular_client), key=lambda t: t["start"])
    assert len(tasks) == 4
    starts = [t["start"] for t in tasks]
    assert starts == [
        "2026-07-13T09:00:00",
        "2026-07-20T09:00:00",
        "2026-07-27T09:00:00",
        "2026-08-03T09:00:00"
    ]
    assert all(t["title"] == "Standup" for t in tasks)
    assert all(t["end"].endswith("09:30:00") for t in tasks)


def test_copies_are_independent(regular_client):
    post_with_csrf(regular_client, "/api/tasks", {**BASE, "repeat_weeks": 2})
    tasks = sorted(_list(regular_client), key=lambda t: t["start"])
    first_id = tasks[0]["id"]
    delete_with_csrf(regular_client, f"/api/tasks/{first_id}")
    remaining = _list(regular_client)
    assert len(remaining) == 2
    assert first_id not in [t["id"] for t in remaining]


def test_edit_with_repeat_spawns_new_copies(regular_client):
    created = post_with_csrf(regular_client, "/api/tasks", BASE).json()
    patch_with_csrf(
        regular_client, f"/api/tasks/{created['id']}",
        {"title": "Daily Standup", "repeat_weeks": 2}
    )
    tasks = _list(regular_client)
    daily = [t for t in tasks if t["title"] == "Daily Standup"]
    assert len(daily) == 3


def test_repeat_weeks_is_not_a_persisted_column(client, database):
    columns = {c["name"] for c in inspect(database.engine).get_columns("tasks")}
    assert "repeat_weeks" not in columns
