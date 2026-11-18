from typing import List

from fastapi import APIRouter, status, HTTPException
from fastapi.params import Depends

from src.auth.dependencies import AUTHENTICATED_RESPONSES, CurrentUser, ADMIN_RESPONSES, AdminUser
from src.exceptions import BookNotFoundException, MemberNotFoundException, DuplicateISBNException
from src.models.book import Book
from src.router.http_errors import book_not_found, member_not_found, book_must_have_unique_isbn

from src.schema.books import BookInput, BookResponse, BookPatchInput

from src.service_accessor import get_book_service
from src.services.books.base import BookService

router = APIRouter(prefix="/books", tags=["Books"])

@router.get(
    path="",
    response_model=List[BookResponse],
    status_code=status.HTTP_200_OK,
    summary="Gets all books",
    description="Gets all books from the library.",
    responses={
        **AUTHENTICATED_RESPONSES,
        200: {
            "description": "A list of books",
        }
    }
)
def get_books(
        _current_user: CurrentUser,
        service: BookService = Depends(get_book_service)
) -> list[Book]:
    return service.get_books()

@router.get(
    path="/{book_id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK,
    summary="Gets a book",
    description="Gets a book from the library matching the given id.",
    responses={
        **AUTHENTICATED_RESPONSES,
        404:{"description":"Book not found"},
        409:{"description":"ISBN must be unique"}
    }
)
def get_book(
        book_id: int,
        _current_user: CurrentUser,
        service: BookService = Depends(get_book_service)
) -> Book:
    try:
        return service.get_book(book_id)
    except BookNotFoundException:
        raise book_not_found(book_id)

@router.post(
    path="",
    response_model=BookResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a book",
    description="Creates a book from all required inputs.",
    responses= {
        **ADMIN_RESPONSES,
        201: {
            "description": "The created book",
        },
        404: {
            "description": "Member not found",
        }
    }
)
def create_book(
        base: BookInput,
        _admin_user: AdminUser,
        service: BookService = Depends(get_book_service)
) -> Book:
    try:
        return service.create_book(base)
    except MemberNotFoundException:
        raise member_not_found(base.member_id)
    except DuplicateISBNException:
        raise book_must_have_unique_isbn()

@router.patch(
    path="/{book_id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK,
    summary="Updates a book",
    description="Updates a book to change some of its content.",
    responses={
        **ADMIN_RESPONSES,
        404:{"description":"Book not found"},
        409:{"description":"ISBN must be unique"}
    }
)
def update_book(
        book_id: int,
        _admin_user: AdminUser,
        data: BookPatchInput,
        service: BookService = Depends(get_book_service)
) -> Book:
    try:
        return service.update_book(book_id, data)
    except BookNotFoundException:
        raise book_not_found(book_id)
    except DuplicateISBNException:
        raise book_must_have_unique_isbn()

@router.delete(
    path="/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletes a book",
    description="Removes a book from the library",
    responses={
        **ADMIN_RESPONSES,
        404:{"description":"Book not found"}
    }
)
def delete_book(
        book_id: int,
        _admin_user: AdminUser,
        service: BookService = Depends(get_book_service)
):
    try:
        service.delete_book(book_id)
    except BookNotFoundException:
        raise book_not_found(book_id)