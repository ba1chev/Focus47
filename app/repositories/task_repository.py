import sqlite3
from typing import Optional

from app.constants import COLUMNS
from app.models.tasks.task_create import TaskCreate
from app.models.tasks.task_update import TaskUpdate


class TaskRepository:
    """Data-access for tasks against a SQLite connection."""

    def __init__(self, conn: sqlite3.Connection) -> None:
        self._conn = conn

    def list(self, start: Optional[str] = None,
        end: Optional[str] = None, user_id: Optional[int] = None) -> list[dict]:
        query = f"SELECT {COLUMNS} FROM tasks WHERE 1=1"
        params: list = []
        if end is not None:
            query += " AND start < ?"
            params.append(end)
        if start is not None:
            query += " AND end > ?"
            params.append(start)
        if user_id is not None:
            query += " AND user_id = ?"
            params.append(user_id)
        query += " ORDER BY start"
        rows = self._conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def get(self, task_id: int) -> Optional[dict]:
        row = self._conn.execute(
            f"SELECT {COLUMNS} FROM tasks WHERE id = ?", (task_id,)
        ).fetchone()
        return dict(row) if row else None

    def create(self, task: TaskCreate) -> dict:
        data = task.model_dump(mode="json")
        cursor = self._conn.execute(
            """
            INSERT INTO tasks
                (title, description, start, end, status, priority, category, user_id)
            VALUES (:title, :description, :start, :end, :status, :priority, :category, :user_id)
            """,
            data
        )
        self._conn.commit()
        return self.get(cursor.lastrowid)

    def update(self, task_id: int, task: TaskUpdate) -> Optional[dict]:
        fields = task.model_dump(mode="json", exclude_unset=True)
        if not fields:
            return self.get(task_id)
        assignments = ", ".join(f"{key} = ?" for key in fields)
        params = list(fields.values()) + [task_id]
        self._conn.execute(
            f"UPDATE tasks SET {assignments} WHERE id = ?", params
        )
        self._conn.commit()
        return self.get(task_id)

    def delete(self, task_id: int) -> bool:
        cursor = self._conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        self._conn.commit()
        return cursor.rowcount > 0

