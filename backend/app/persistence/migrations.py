from sqlalchemy import text

from app.core.config import get_settings
from app.core.snowflake import SnowflakeIdGenerator
from app.database import engine


def migrate_legacy_user_ids() -> None:
    """Convert former sequential user IDs to Snowflake IDs.

    There are currently no foreign keys pointing to users. New IDs are much larger
    than historical sequential IDs, so only those legacy rows are transformed.
    """
    generator = SnowflakeIdGenerator(get_settings().snowflake_worker_id)
    with engine.begin() as connection:
        legacy_ids = connection.execute(text("SELECT id FROM users WHERE id < :limit"), {"limit": 1 << 22}).scalars().all()
        for legacy_id in legacy_ids:
            connection.execute(
                text("UPDATE users SET id = :new_id WHERE id = :old_id"),
                {"new_id": generator.next_id(), "old_id": legacy_id},
            )


def migrate_user_email_column() -> None:
    """Add the nullable email column for databases created before email support."""
    with engine.begin() as connection:
        columns = connection.execute(text("PRAGMA table_info(users)")).mappings().all()
        if not any(column["name"] == "email" for column in columns):
            connection.execute(text("ALTER TABLE users ADD COLUMN email VARCHAR(255)"))
        connection.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email)"))
