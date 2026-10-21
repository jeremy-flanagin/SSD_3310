from typing import List

from fastapi import APIRouter, status, HTTPException
from fastapi.params import Depends

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
        200: {
            "description": "A list of books",
        }
    }
)
def get_books(service: BookService = Depends(get_book_service)) -> List[Book]:
    return service.get_books()

@router.get(
    path="/{book_id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK,
    summary="Gets a book",
    description="Gets a book from the library matching the given id.",
    responses={404:{"description":"Book not found"},
               409:{"description":"ISBN must be unique"}}
)
def get_book(book_id: int, service: BookService = Depends(get_book_service)) -> Book:
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
        201: {
            "description": "The created book",
        },
        404: {
            "description": "Member not found",
        }
    }
)
def create_book(base: BookInput, service: BookService = Depends(get_book_service)) -> Book:
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
    responses={404:{"description":"Book not found"},
               409:{"description":"ISBN must be unique"}}
)
def update_book(book_id: int, data: BookPatchInput, service: BookService = Depends(get_book_service)) -> Book:
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
    responses={404:{"description":"Book not found"}}
)
def delete_book(book_id: int, service: BookService = Depends(get_book_service)):
    try:
        service.delete_book(book_id)
    except BookNotFoundException:
        raise book_not_found(book_id)