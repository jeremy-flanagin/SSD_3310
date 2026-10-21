from typing import List

from sqlalchemy.orm import Session, sessionmaker

from src.exceptions import BookNotFoundException, MemberNotFoundException, DuplicateISBNException
from src.models.book import Book
from src.repositories.book import BookRepository
from src.repositories.member import MemberRepository
from src.schema.books import BookPatchInput, BookInput

from src.services.books.base import BookService


class DatabaseBookService(BookService):
    def __init__(self, session: sessionmaker[Session]):
        self._session_factory = session

    def get_books(self) -> List[Book]:
        with self._session_factory() as session:
            return BookRepository(session).get_all()

    def get_book(self, book_id: int) -> Book:
        with self._session_factory() as session:
            book = BookRepository(session).get(book_id)
            if book is None:
                raise BookNotFoundException
            return book

    def create_book(self, base: BookInput) -> Book:
        with self._session_factory().begin().session as session:
            book_repository = BookRepository(session)
            member_repository = MemberRepository(session)
            if not member_repository.get(base.member_id):
                raise MemberNotFoundException
            for book in book_repository.get_all():
                if book.isbn == base.isbn:
                    raise DuplicateISBNException
            book = book_repository.create(base)
            session.refresh(book)
            return book

    def update_book(self, book_id: int, data: BookPatchInput) -> Book:
        with self._session_factory().begin().session as session:
            repository = BookRepository(session)
            book = repository.get(book_id)
            if book is None:
                raise BookNotFoundException
            for book in repository.get_all():
                if book.isbn == data.isbn and book.id != book_id:
                    raise DuplicateISBNException
            book = repository.update(book, data)
            session.refresh(book)
            return book

    def delete_book(self, book_id: int):
        with self._session_factory().begin().session as session:
            repository = BookRepository(session)
            book = repository.get(book_id)
            if book is None:
                raise BookNotFoundException
            repository.delete(book)
            session.refresh(book)