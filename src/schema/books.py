import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import date
from src.storage import books


class BookBase(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True
    )
    title: str = Field(
        min_length=1,
        max_length=200,
        description= "The title of the book."
    )
    author: str = Field(
        min_length=1,
        max_length=120,

        description= "The author of the book."
    )
    isbn: str = Field(
        description="The ISBN of the book."
    )
    published_year: int = Field(
        ge=1450,
        le=date.today().year,
        default=date.today().year,
        description= "The year the book was published."
    )
    member_id: int = Field(
        default=-1,
        description="The id of the member holding the book."
    )

    @field_validator("isbn")
    @classmethod
    def ensure_unique_isbn(cls, v):
        for book in books:
            if book.isbn == v:
                raise ValueError("Must be unique")
        return v


class BookInput(BookBase):
    pass

class BookPatchInput(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True
    )
    title: Optional[str] = Field(
        min_length=1,
        max_length=200,
        description="The title of the book."
    )
    author: Optional[str] = Field(
        min_length=1,
        max_length=120,
        description="The author of the book."
    )
    isbn: Optional[str] = Field(
        description="The ISBN of the book."
    )
    published_year: int = Field(
        ge=1450,
        le=date.today().year,
        default=date.today().year,
        description="The year the book was published."
    )
    member_id: int = Field(
        default=-1,
        description="The id of the member holding the book."
    )

    @field_validator("isbn")
    @classmethod
    def ensure_unique_isbn(cls, v):
        for book in books:
            if book.isbn == v:
                raise ValueError("Must be unique")
        return v

class BookResponse(BookBase):
    id: int = Field()