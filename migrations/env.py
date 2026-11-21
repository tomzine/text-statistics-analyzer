
from logging.config import fileConfig

from alembic import context

from fastapi_app.database import (
    Base,
    DATABASE_URL,
    engine
)

# Import models to register all tables
import fastapi_app.models


# Alembic configuration
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Tell Alembic where our SQLAlchemy metadata is
target_metadata = Base.metadata


# Use the same database URL as our application
config.set_main_option(
    "sqlalchemy.url",
    DATABASE_URL.replace("%", "%%")
)


# OFFLINE MIGRATIONS
def run_migrations_offline():

    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
        render_as_batch=True
    )

    with context.begin_transaction():
        context.run_migrations()


# ONLINE MIGRATIONS

def run_migrations_online():

    with engine.connect() as connection:

        # Temporarily disable foreign-key enforcement
        # on this migration connection only.
        connection.exec_driver_sql(
            "PRAGMA foreign_keys=OFF"
        )
        connection.commit()

        try:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
                compare_type=True,
                render_as_batch=True
            )

            with context.begin_transaction():
                context.run_migrations()

        finally:
            # End any unfinished transaction first.
            if connection.in_transaction():
                connection.rollback()

            # Restore foreign-key enforcement.
            connection.exec_driver_sql(
                "PRAGMA foreign_keys=ON"
            )
            connection.commit()



if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
