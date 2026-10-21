from dataclasses import dataclass

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.config import Settings


@dataclass(frozen=True)
class DatabaseInstance:
    engine: Engine
    session_factory: sessionmaker[Session]


def create_database(settings: Settings) -> DatabaseInstance:

    engine = create_engine(url=settings.database_url, echo=settings.database_debug)
    session_factory = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)

    return DatabaseInstance(engine=engine, session_factory=session_factory)