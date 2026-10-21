from typing import List

from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.models.base import Base
from src.models.book import Book


class Member(Base):
    __tablename__ = 'member'
    """Assigns the table's name to books"""

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)
    membership_id: Mapped[str] = mapped_column(nullable=False)
    phone: Mapped[str] = mapped_column(nullable=False)

    books: Mapped[List[Book]] = relationship(back_populates="member")