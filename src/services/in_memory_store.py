from dataclasses import field, dataclass
from threading import RLock

from src.models.book import Book
from src.models.member import Member


@dataclass()
class InMemoryStorage:
    books: list[Book] = field(default_factory=list)
    members: list[Member] = field(default_factory=list)

    lock: RLock = field(default_factory=RLock, repr=False)

    def find_book(self, book_id: int) -> Book | None:
        for book in self.books:
            if book.id == book_id:
                return book
        return None
    
    def find_member(self, member_id: int) -> Member | None:
        for member in self.members:
            if member.id == member_id:
                return member
        return None