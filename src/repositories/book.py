from abc import ABC
from typing import List

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.book import Book
from src.schema.books import BookInput, BookPatchInput


class BookRepository(ABC):
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Book]:
        statement = select(Book)
        return list(self.session.scalars(statement))

    def get(self, book_id: int) -> Book | None:
        return self.session.get(Book, book_id)

    def create(self, base: BookInput) -> Book:
        book = Book(**base.model_dump())
        self.session.add(book)
        self.session.flush()
        return book

    def update(self, book: Book, data: BookPatchInput) -> Book:
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        book.__dict__.update(update_data)
        self.session.flush()
        return book

    def delete(self, book: Book):
        self.session.delete(book)
