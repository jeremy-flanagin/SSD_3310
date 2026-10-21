from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.config import Settings, DatabaseBackend
from src.database.session import create_database
from src.models.base import Base
from src.router.books import router as books_router
from src.router.members import router as members_router
from src.services.books.database import DatabaseBookService
from src.services.books.memory import InMemoryBookService
from src.services.in_memory_store import InMemoryStorage
from src.services.members.database import DatabaseMemberService
from src.services.members.memory import InMemoryMemberService

tags = [
    {
        "name": "Books",
        "description": "Manages books in the system",
    },
    {
        "name": "Members",
        "description": "Manages members in the system"
    }
]

api = FastAPI(
    title= "Library Management System API",
    description= "Provides an API to manage the library. "
                 "Provides the ability to create, find, delete, and update Members and Books.",
    version= "0.2.0",
    openapi_tags=tags
)

api.include_router(books_router)
api.include_router(members_router)

@asynccontextmanager
async def lifespan(application: FastAPI):
    """Initialize application-scoped infrastructure at startup."""
    settings = Settings()
    application.state.settings = settings

    if settings.database_backend is DatabaseBackend.MEMORY:
        store = InMemoryStorage()
        application.state.book_service = InMemoryBookService(store)
        application.state.member_service = InMemoryMemberService(store)
    elif settings.database_backend is DatabaseBackend.DATABASE:
        database = create_database(settings)
        Base.metadata.create_all(bind=database.engine)
        # Services are stateless and safe to share. They receive the session
        # factory, not one shared Session, so each database operation creates
        # its own unit of work and controls its own transaction.
        application.state.book_service = DatabaseBookService(
            database.session_factory
        )
        application.state.member_service = DatabaseMemberService(
            database.session_factory
        )
    # Code after yield would run during application shutdown.
    yield