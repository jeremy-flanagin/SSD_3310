from typing import List

from fastapi import APIRouter, status, HTTPException

from src.router.members import find_member
from src.schema.books import BookInput, BookResponse, BookPatchInput
from src.storage import books

router = APIRouter(prefix="/books", tags=["Books"])


def get_next_book_id() -> int:
    return max((book.id for book in books), default=0) + 1

def get_book_index(book_id: int) -> int:
    for index, book in enumerate(books):
        if book.id == book_id:
            return index

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Book not found",
    )

def find_book(book_id: int) -> BookResponse:
    for book in books:
        if book.id == book_id:
            return book

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Book not found",
    )

def set_book(book_id: int, new_book: BookResponse):
    for index, book in enumerate(books):
        if book.id == book_id:
            books[index] = new_book
            return
    books.append(new_book)

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
def create_book(base: BookInput) -> BookResponse:
    find_member(base.member_id)
    next_id = get_next_book_id()
    book = BookResponse(id=next_id, **base.model_dump())
    books.append(book)
    return book

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
def get_books() -> List[BookResponse]:
    return books

@router.get(
    path="/{book_id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK,
    summary="Gets a book",
    description="Gets a book from the library matching the given id.",
    responses={404:{"description":"Book not found"}}
)
def get_book(book_id: int) -> BookResponse:
    return find_book[book_id]

@router.patch(
    path="/{book_id}",
    response_model=BookResponse,
    status_code=status.HTTP_200_OK,
    summary="Updates a book",
    description="Updates a book to change some of its content.",
    responses={404:{"description":"Book not found"}}
)
def update_book(book_id: int, data: BookPatchInput) -> BookResponse:
    book = find_book(book_id)
    update_data = data.model_dump(exclude_unset=True, exclude_none=True)
    modified_book = book.model_copy(update=update_data)
    set_book(book_id, modified_book)
    return modified_book

@router.delete(
    path="/{book_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletes a book",
    description="Removes a book from the library",
    responses={404:{"description":"Book not found"}}
)
def delete_book(book_id: int):
    index = get_book_index(book_id)
    books.pop(index)