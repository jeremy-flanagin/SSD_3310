from typing import List

from src.exceptions import BookNotFoundException, MemberNotFoundException, DuplicateISBNException
from src.models.book import Book
from src.schema.books import BookPatchInput, BookInput
from src.services.books.base import BookService
from src.services.in_memory_store import InMemoryStorage


class InMemoryBookService(BookService):
    def __init__(self, store: InMemoryStorage):
        self._store = store

    def get_books(self) -> List[Book]:
        with self._store.lock:
            return list(self._store.books)

    def get_book(self, book_id: int) -> Book:
        with self._store.lock:
            for book in self._store.books:
                if book.id == book_id:
                    return book
            raise BookNotFoundException

    def create_book(self, base: BookInput) -> Book:
        with self._store.lock:
            if self._store.find_member(base.member_id) is None:
                raise MemberNotFoundException
            for book in self._store.books:
                if book.isbn == base.isbn:
                    raise DuplicateISBNException
            next_id = max((book.id for book in self._store.books), default=0) + 1
            book = Book(id=next_id, **base.model_dump())
            self._store.books.append(book)
            return book

    def update_book(self, book_id: int, data: BookPatchInput) -> Book:
        with self._store.lock:
            book = self.get_book(book_id)
            if book is None:
                raise BookNotFoundException
            for book in self._store.books:
                if book.isbn == data.isbn and book.id != book_id:
                    raise DuplicateISBNException
            update_data = data.model_dump(exclude_unset=True, exclude_none=True)
            book.__dict__.update(update_data)
            return book

    def delete_book(self, book_id: int):
        with self._store.lock:
            for index, book in enumerate(self._store.books):
                if book.id == book_id:
                    self._store.books.remove(book)
            raise BookNotFoundException