"""Unit tests for the in-memory Member service contract."""

import pytest
from pydantic.v1.networks import EmailStr

from src.exceptions import MemberHasBooksException, MemberNotFoundException
from src.models.book import Book
from src.models.member import Member
from src.schema.members import MemberInput, MemberPatchInput
from src.services.in_memory_store import InMemoryStorage
from src.services.members.memory import InMemoryMemberService


@pytest.fixture()
def store() -> InMemoryStorage:
    return InMemoryStorage()


@pytest.fixture()
def service(store: InMemoryStorage) -> InMemoryMemberService:
    return InMemoryMemberService(store)

@pytest.fixture()
def member_data(request) -> MemberInput:
    """
    Creates a MemberInput from a given name, if no name
    is given it defaults to 'Example Member'
    """
    if request.param_index == 1:
        name = request.param
    else:
        name = "Example Member"
    return MemberInput(name=name,
                       email=EmailStr("example_member@examples.org"),
                       membership_id="Blank",
                       phone="443-307-1473",
    )


def test_create_and_get_member(
        service: InMemoryMemberService,
        member_data: MemberInput
) -> None:
    created = service.create_member(member_data)

    assert created.id == 1
    assert service.get_members() == [created]
    assert service.get_member(created.id) is created


def test_get_member_raises_for_missing_id(service: InMemoryMemberService) -> None:
    with pytest.raises(MemberNotFoundException):
        service.get_member(999)


def test_replace_member_updates_fields(
        service: InMemoryMemberService,
        member_data: MemberInput
) -> None:
    member = service.create_member(member_data)

    updated = service.update_member(
        member.id,
        MemberPatchInput(name="New Name",
                         email=EmailStr("new@email.net")),
    )

    assert updated is member
    assert updated.name == "New Name"
    assert updated.membership_id == member_data.membership_id
    assert updated.email == "new@email.net"


def test_list_member_books_requires_existing_member(
    service: InMemoryMemberService,
) -> None:
    with pytest.raises(MemberNotFoundException):
        service.get_member_books(999)


def test_list_member_books_returns_held_books(
    store: InMemoryStorage,
    service: InMemoryMemberService,
    member_data: MemberInput
) -> None:
    member = service.create_member(member_data)
    book = Book(
        id=1,
        title="Book",
        author="Author",
        isbn="isbn13",
        published_year=2000,
        member_id=member.id,
    )
    store.books.append(book)

    assert service.get_member_books(member.id) == [book]

def test_delete_member_rejects_holding_books(
    store: InMemoryStorage,
    service: InMemoryMemberService,
    member_data: MemberInput
) -> None:
    member = service.create_member(member_data)
    store.books.append(
        Book(
            id=1,
            title="Book",
            author="Author",
            isbn="isbn13",
            published_year=2000,
            member_id=member.id,
        )
    )

    with pytest.raises(MemberHasBooksException):
        service.delete_member(member.id)

    assert service.get_member(member.id) is member


def test_delete_member_removes_member_without_books(
    service: InMemoryMemberService,
    member_data: MemberInput
) -> None:
    member = service.create_member(member_data)

    service.delete_member(member.id)

    assert service.get_members() == []
