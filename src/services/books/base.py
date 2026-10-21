from abc import ABC, abstractmethod
from typing import List

from src.models.book import Book
from src.schema.books import BookInput, BookPatchInput


class BookService(ABC):
    @abstractmethod
    def create_book(self, base: BookInput) -> Book:
        pass

    @abstractmethod
    def get_books(self) -> List[Book]:
        pass

    @abstractmethod
    def get_book(self, book_id: int) -> Book:
        pass

    @abstractmethod
    def update_book(self, book_id: int, data: BookPatchInput) -> Book:
        pass

    @abstractmethod
    def delete_book(self, book_id: int):
        pass