from abc import ABC, abstractmethod
from typing import List

from src.models.book import Book
from src.models.member import Member
from src.schema.members import MemberInput, MemberPatchInput


class MemberService(ABC):
    @abstractmethod
    def create_member(self, base: MemberInput) -> Member:
        pass

    @abstractmethod
    def get_members(self) -> List[Member]:
        pass

    @abstractmethod
    def get_member(self, member_id: int) -> Member:
        pass

    @abstractmethod
    def get_member_books(self, member_id: int) -> List[Book]:
        pass

    @abstractmethod
    def update_member(self, member_id: int, data: MemberPatchInput) -> Member:
        pass

    @abstractmethod
    def delete_member(self, member_id: int):
        pass