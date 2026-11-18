from typing import List

from src.exceptions import MemberNotFoundException, MemberHasBooksException, DuplicateEmailException, \
    DuplicateMembershipException
from src.models.book import Book
from src.models.member import Member
from src.schema.members import MemberInput, MemberPatchInput
from src.services.in_memory_store import InMemoryStorage
from src.services.members.base import MemberService


class InMemoryMemberService(MemberService):
    def __init__(self, store: InMemoryStorage):
        self._store = store

    def get_members(self) -> List[Member]:
        with self._store.lock:
            return list(self._store.members)

    def get_member(self, member_id: int) -> Member:
        with self._store.lock:
            for member in self._store.members:
                if member.id == member_id:
                    return member
            raise MemberNotFoundException

    def get_member_books(self, member_id: int) -> List[Book]:
        with self._store.lock:
            if not self.get_member(member_id):
                raise MemberNotFoundException
            return [book for book in self._store.books if member_id == book.member_id]

    def create_member(self, base: MemberInput) -> Member:
        with self._store.lock:
            next_id = max((member.id for member in self._store.members), default=0) + 1
            member = Member(id=next_id, **base.model_dump())
            for oMember in self._store.members:
                if oMember.email == member.email:
                    raise DuplicateEmailException
                if oMember.membership_id == member.membership_id:
                    raise DuplicateMembershipException
            self._store.members.append(member)
            return member

    def update_member(self, member_id: int, data: MemberPatchInput) -> Member:
        with self._store.lock:
            member = self.get_member(member_id)
            if member is None:
                raise MemberNotFoundException
            for oMember in self._store.members:
                if oMember.id == member.id:
                    continue
                if oMember.email == member.email:
                    raise DuplicateEmailException
                if oMember.membership_id == member.membership_id:
                    raise DuplicateMembershipException
            for field, value in data.model_dump(exclude_unset=True, exclude_none=True).items():
                setattr(member, field, value)
            return member

    def delete_member(self, member_id: int):
        with self._store.lock:
            for index, member in enumerate(self._store.members):
                if member.id == member_id:
                    held_books = self.get_member_books(member_id)
                    if len(held_books) > 0: raise MemberHasBooksException
                    self._store.members.remove(member)
                    return
            raise MemberNotFoundException