from sqlalchemy import text, inspect
from sqlalchemy.engine import Engine

from db.models.user_record import UserRecord
from db.models.task_record import TaskRecord


LAZY_COLUMNS: dict[str, dict[str, str]] = {
    UserRecord.__tablename__: {},
    TaskRecord.__tablename__: {}
}


def run_auto_migrations(engine: Engine) -> None:
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())

    for table_name, columns in LAZY_COLUMNS.items():
        if not columns or table_name not in existing_tables:
            continue
        existing = {col["name"] for col in inspector.get_columns(table_name)}
        missing = [(n, t) for n, t in columns.items() if n not in existing]
        if not missing:
            continue
        with engine.begin() as connection:
            for column_name, sql_type in missing:
                connection.execute(text(
                    f"ALTER TABLE {table_name} ADD COLUMN {column_name} {sql_type}"
                ))
