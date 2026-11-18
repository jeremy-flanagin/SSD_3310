"""Unit tests for the in-memory Book service contract."""

import pytest

from src.exceptions import MemberNotFoundException, BookNotFoundException
from src.models.member import Member
from src.schema.books import BookInput, BookPatchInput
from src.services.in_memory_store import InMemoryStorage
from src.services.books.memory import InMemoryBookService


@pytest.fixture()
def store() -> InMemoryStorage:
    return InMemoryStorage()


@pytest.fixture()
def service(store: InMemoryStorage) -> InMemoryBookService:
    return InMemoryBookService(store)

@pytest.fixture()
def book_data(request) -> BookInput:
    if request.param_index == 1:
        title = request.param
    else:
        title = "Example Book"

    return BookInput(
        title=title,
        author="Example Author",
        isbn="",
        published_year=2000,
        member_id=1
    )


def add_member(store: InMemoryStorage) -> Member:
    member = Member(id=1,
                    name="Example Member",
                    email="generic_mail@examples.com",
                    membership_id="test_membership",
                    phone="443-307-1473")
    store.members.append(member)
    return member


def test_create_book_requires_existing_member(
    service: InMemoryBookService,
    book_data: BookInput
) -> None:
    with pytest.raises(MemberNotFoundException):
        service.create_book(book_data)


def test_create_list_and_get_book(
    store: InMemoryStorage,
    service: InMemoryBookService,
    book_data: BookInput
) -> None:
    add_member(store)

    created = service.create_book(book_data)

    assert created.id == 1
    assert service.get_books() == [created]
    assert service.get_book(created.id) is created


def test_get_book_raises_for_missing_id(service: InMemoryBookService) -> None:
    with pytest.raises(BookNotFoundException):
        service.get_book(999)

@pytest.mark.parametrize("book_data", ["to_update"], indirect=["book_data"])
def test_modify_book_updates_fields(
    store: InMemoryStorage,
    service: InMemoryBookService,
    book_data: BookInput
) -> None:
    add_member(store)
    book = service.create_book(book_data)

    updated = service.update_book(
        book.id,
        BookPatchInput(
            title="Updated",
            isbn="1234",
            member_id=1
        ),
    )

    assert updated is book
    assert updated.title == "Updated"
    assert updated.isbn == "1234"
    assert updated.published_year == book_data.published_year


@pytest.mark.parametrize("book_data", ["to_delete"], indirect=["book_data"])
def test_delete_book_removes_book(
    store: InMemoryStorage,
    service: InMemoryBookService,
    book_data: BookInput
) -> None:
    add_member(store)
    book = service.create_book(book_data)

    service.delete_book(book.id)

    assert service.get_books() == []
