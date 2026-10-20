from fastapi import FastAPI

from src.router.books import router as books_router
from src.router.members import router as members_router

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
    version= "0.1.0",
    openapi_tags=tags
)

api.include_router(books_router)
api.include_router(members_router)