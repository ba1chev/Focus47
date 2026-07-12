from db.models.user_record import UserRecord
from db.models.task_record import TaskRecord


# Columns added to existing tables after their initial creation.
# create_all only builds missing *tables*, not missing columns — listing a
# column here patches it in via ALTER TABLE ... ADD COLUMN (a no-op once it
# exists). Map each table name to {column_name: sql_type_with_default}.
LAZY_COLUMNS: dict[str, dict[str, str]] = {
    UserRecord.__tablename__: {},
    TaskRecord.__tablename__: {}
}
