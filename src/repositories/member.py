from abc import ABC
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select

from src.models.book import Book
from src.models.member import Member
from src.schema.members import MemberInput, MemberPatchInput


class MemberRepository(ABC):
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> List[Member]:
        statement = select(Member)
        return list(self.session.scalars(statement))

    def get(self, member_id: int) -> Member | None:
        return self.session.get(Member, member_id)

    def create(self, base: MemberInput) -> Member:
        member = Member(**base.model_dump())
        self.session.add(member)
        self.session.flush()
        return member

    def update(self, member: Member, data: MemberPatchInput) -> Member:
        update_data = data.model_dump(exclude_unset=True, exclude_none=True)
        member.__dict__.update(update_data)
        self.session.flush()
        return member

    def delete(self, member: Member):
        self.session.delete(member)