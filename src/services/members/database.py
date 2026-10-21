from typing import List

from sqlalchemy.orm import sessionmaker, Session

from src.exceptions import MemberNotFoundException, DuplicateEmailException, DuplicateMembershipException
from src.models.book import Book
from src.models.member import Member
from src.repositories.member import MemberRepository
from src.schema.members import MemberInput, MemberPatchInput
from src.services.members.base import MemberService


class DatabaseMemberService(MemberService):
    def __init__(self, session: sessionmaker[Session]):
        self._session_factory = session

    def get_members(self) -> List[Member]:
        with self._session_factory() as session:
            return MemberRepository(session).get_all()

    def get_member(self, member_id: int) -> Member:
        with self._session_factory() as session:
            member = MemberRepository(session).get(member_id)
            if member is None:
                raise MemberNotFoundException
            return member

    def get_member_books(self, member_id: int) -> List[Book]:
        with self._session_factory() as session:
            member = MemberRepository(session).get(member_id)
            if member is None:
                raise MemberNotFoundException
            return member.books

    def create_member(self, base: MemberInput) -> Member:
        with self._session_factory().begin().session as session:
            member_repository = MemberRepository(session)
            for member in member_repository.get_all():
                if member.id == member.id:
                    continue
                if member.email == base.email:
                    raise DuplicateEmailException
                if member.membership_id == base.membership_id:
                    raise DuplicateMembershipException
            member = member_repository.create(base)
            session.refresh(member)
            return member

    def update_member(self, member_id: int, data: MemberPatchInput) -> Member:
        with self._session_factory().begin().session as session:
            repository = MemberRepository(session)
            member = repository.get(member_id)
            if member is None:
                raise MemberNotFoundException
            for member in repository.get_all():
                if member.id == member.id:
                    continue
                if member.email == data.email:
                    raise DuplicateEmailException
                if member.membership_id == data.membership_id:
                    raise DuplicateMembershipException
            member = repository.update(member, data)
            session.refresh(member)
            return member

    def delete_member(self, member_id: int):
        with self._session_factory().begin().session as session:
            repository = MemberRepository(session)
            member = repository.get(member_id)
            if member is None:
                raise MemberNotFoundException
            repository.delete(member)
            session.refresh(member)