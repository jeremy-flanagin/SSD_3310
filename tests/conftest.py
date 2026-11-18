import os
from typing import Generator

import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker
from starlette.testclient import TestClient
from testcontainers.community.postgres import PostgresContainer

from src.auth.users import get_token_for_role, Role
from src.config import Settings, DatabaseBackend
from src.database.session import create_database

@pytest.fixture(scope="session")
def postgres_container() -> Generator[PostgresContainer, None, None]:
    """Start one disposable PostgreSQL database for the entire pytest session."""
    # scope="session" means one container for one `uv run pytest` command, not
    # one container per test file. Pytest creates it only if a test requests a
    # fixture that depends on it; unit tests do not start Docker.
    #
    # Testcontainers communicates with Docker Desktop, starts postgres:18, and
    # waits until PostgreSQL is ready to accept connections.
    # driver="psycopg" makes the generated SQLAlchemy URL use this project's
    # Psycopg 3 driver instead of the Testcontainers default Psycopg 2 driver.
    with PostgresContainer(
        "postgres:18",
        username="postgres",
        password="postgres",
        dbname="library_test",
        driver="psycopg",
    ) as container:
        # Set this before creating the application's database infrastructure.
        # The application then connects to this temporary database rather than
        # the local development database named project_task.
        os.environ["DATABASE_URL"] = container.get_connection_url()

        # `yield container` pauses this fixture while every test that needs the
        # session-scoped container runs. Pytest resumes below only after the
        # entire pytest command has finished.
        yield container

    # Leaving the `with PostgresContainer(...)` block stops and removes the
    # temporary Docker container. Remove the test-only environment value too.
    os.environ.pop("DATABASE_URL", None)


@pytest.fixture(scope="function")
def db_engine(
    postgres_container: PostgresContainer
) -> Engine:
    return create_database(Settings()).engine

@pytest.fixture(scope='function')
def db_session(
    reset_database: None, db_engine: Engine
) -> Generator[Session, None, None]:
    session_factory = sessionmaker(bind=db_engine, autoflush=False, expire_on_commit=False)
    with session_factory() as session:
        yield session
        session.rollback()

@pytest.fixture
def reset_database(db_engine: Engine) -> Generator[None, None, None]:
    from src.models.base import Base

    # Setup for one test function: remove any data/schema from an earlier test,
    # then create empty tables using the real ORM metadata.
    Base.metadata.drop_all(bind=db_engine)
    Base.metadata.create_all(bind=db_engine)

    # Plain `yield` gives no value to the test. It marks the boundary between
    # setup above and cleanup below: pytest runs the test while this fixture is
    # paused here, then resumes at the next line even if the test fails.
    yield

    # Cleanup after the one test function. The PostgreSQL container stays alive
    # for later tests, but no test data or tables are shared between them.
    Base.metadata.drop_all(bind=db_engine)



@pytest.fixture
def database_client(reset_database: None) -> Generator[TestClient, None, None]:
    """Provide a TestClient after the temporary database is ready."""
    # Requesting reset_database ensures the Testcontainers database is ready
    # and empty before FastAPI starts.
    # TestClient runs the FastAPI lifespan, just as an application startup does.
    # At this point DATABASE_URL already points to the Testcontainers database.
    from src.main import api

    with TestClient(api) as test_client:
        # Entering this context starts FastAPI's lifespan function. It does not
        # start Uvicorn, bind localhost:8000, or make a real network connection.
        # TestClient sends ASGI requests directly to this in-process FastAPI app.
        yield test_client

    # Leaving this context closes TestClient and runs FastAPI lifespan cleanup.


@pytest.fixture
def memory_client(
    monkeypatch: pytest.MonkeyPatch,
) -> Generator[TestClient, None, None]:
    """Provide a TestClient whose lifespan selects the in-memory services."""
    # Environment variables override values from .env. Removing DATABASE_URL
    # makes it clear that this test does not need PostgreSQL; the memory
    # backend does not validate or use a database URL.
    monkeypatch.setenv("STORAGE_BACKEND", "memory")
    monkeypatch.delenv("DATABASE_URL", raising=False)

    from src.main import api

    with TestClient(api) as test_client:
        # FastAPI's lifespan creates a fresh InMemoryStore for this client, so
        # projects and tasks cannot leak between memory router tests.
        yield test_client


@pytest.fixture
def no_database_settings() -> Settings:
    return Settings(database_backend=DatabaseBackend.MEMORY)


@pytest.fixture
def member_headers(no_database_settings: Settings) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {get_token_for_role(Role.MEMBER, no_database_settings)}"
    }


@pytest.fixture
def admin_headers(no_database_settings: Settings) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {get_token_for_role(Role.ADMIN, no_database_settings)}"
    }