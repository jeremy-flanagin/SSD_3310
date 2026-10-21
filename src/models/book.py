from sqlalchemy import String
from sqlalchemy.orm import mapped_column, relationship, Mapped

from src.models.base import Base


class Book(Base):
    __tablename__ = 'book'
    """Assigns the table's name to books"""
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    author: Mapped[str] = mapped_column(String(120), nullable=False)
    isbn: Mapped[str] = mapped_column(nullable=False)
    published_year: Mapped[int] = mapped_column(nullable=False)
    member_id: Mapped[int] = mapped_column(nullable=False)

    member: Mapped[Member] = relationship(back_populates="book")