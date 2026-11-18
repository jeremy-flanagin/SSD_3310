from datetime import date
from typing import Dict, Tuple

import pytest
from pydantic import ValidationError, BaseModel

from src.schema.books import BookInput, BookPatchInput, BookResponse


# Utilities
@pytest.fixture(scope="function", params=[BookInput, BookPatchInput])
def book_base(request) -> type[BaseModel]:
    return request.param

@pytest.fixture(scope="function")
def book_fields() -> Dict[str, any]:
    return {
        "title": "How to Test Books",
        "author": "Fee Jee",
        "isbn": "9781566199094",
        "published_year": 2001,
        "member_id": 0
    }

@pytest.fixture(scope='function', params=[
    pytest.param((" filled ", "filled"), id="single_whitespace"),
    pytest.param(("  doublefilled  ", "doublefilled"), id="double_whitespace")
])
def whitespace_values(request) -> Tuple[str, str]:
    return request.param


# BookBase and BookPatchInput

@pytest.mark.parametrize("field", ["title", "author", "isbn", "member_id"])
def test_book_create_requires_fields(book_fields: Dict[str, any], field: str) -> None:
    book_fields.pop(field)

    with pytest.raises(ValidationError):
        BookInput(**book_fields)

def test_book_update_does_not_require_fields() -> None:
    BookPatchInput(**{})


@pytest.mark.parametrize("boundary_value", [
    ("title", "a"),
    ("title", "b" * 200)    ,
    ("author", "c"),
    ("author", "d" * 120),
    ("published_year", 1450),
    ("published_year", date.today().year),
])
def test_book_model_passes_with_valid_boundaries(book_base: type[BaseModel], book_fields: Dict[str, any], boundary_value: Tuple[str, any]) -> None:
    book_fields[boundary_value[0]] = boundary_value[1]
    book_base(**book_fields)

@pytest.mark.parametrize("boundary_value", [
    ("title", " "),
    ("title", "b" * 201),
    ("author", " "),
    ("author", "d" * 121),
    ("published_year", 1449),
    ("published_year", 1449.9999),
    ("published_year", date.today().year + 1),
])
def test_book_model_fails_with_invalid_boundaries(book_base: type[BaseModel],
                                                   book_fields: Dict[str, any],
                                                   boundary_value: Tuple[str, any]) -> None:
    book_fields[boundary_value[0]] = boundary_value[1]

    with pytest.raises(ValidationError):
        book_base(**book_fields)

@pytest.mark.parametrize("published_year", [1000, 3000])
def test_book_model_restricts_published_year(book_base: type[BaseModel], book_fields: Dict[str, any], published_year: int) -> None:
    book_fields["published_year"] = published_year

    with pytest.raises(ValidationError):
        book_base(**book_fields)

@pytest.mark.parametrize("key", ["title", "author"])
def test_book_model_trims_whitespace(book_base: type[BaseModel], 
                                      book_fields: Dict[str, any],
                                      key: str, 
                                      whitespace_values: Tuple[str, str]) -> None:
    book_fields[key] = whitespace_values[0]

    book_input = book_base(**book_fields)
    assert book_input.model_dump()[key] == whitespace_values[1]


def test_book_model_rejects_unknown_fields(book_base: type[BaseModel],
                                            book_fields: Dict[str, any]) -> None:
    book_fields["unknown_field"] = "kaofiensoai"

    with pytest.raises(ValidationError):
        book_base(**book_fields)

# GET

@pytest.mark.parametrize("id", [-1])
def test_book_response_rejects_negative_ids(book_fields: Dict[str, any], id: int) -> None:
    book_fields["id"] = id

    with pytest.raises(ValidationError):
        BookResponse(**book_fields)


@pytest.mark.parametrize("id", [0])
def test_book_response_is_valid_with_boundary_id(book_fields: Dict[str, any], id: int) -> None:
    book_fields["id"] = id

    with pytest.raises(ValidationError):
        BookResponse(**book_fields)