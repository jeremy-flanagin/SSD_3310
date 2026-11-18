import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.repositories.member import MemberRepository
from src.repositories.book import BookRepository
from src.schema.members import MemberInput
from src.schema.books import BookInput, BookPatchInput


# Utilities

def create_member(session: Session, name: str):
    repository = MemberRepository(session)
    member = repository.create(
        MemberInput(name=name,
`                    email=name + "@mail.com",
                    membership_id=name,
                    phone="443-307-1473")
    )
    session.commit()
    session.refresh(member)
    return member


def create_book(
    repository: BookRepository,
    session: Session,
    member_id: int,
    title: str,
):
    book = repository.create(
        BookInput(
            title=title,
            author="Authed",
            isbn="3785948743",
            member_id=member_id,
        )
    )
    session.commit()
    session.refresh(book)
    return book

# Tasks

def test_get_all_returns_books_in_id_order(db_session: Session) -> None:
    member = create_member(db_session, "Holder")
    repository = BookRepository(db_session)
    first = create_book(repository, db_session, member.id, "First")
    second = create_book(repository, db_session, member.id, "Second")

    books = repository.get_all()

    assert [book.id for book in books] == [first.id, second.id]

def test_get_returns_existing_book_and_none_when_missing(
    db_session: Session,
) -> None:
    member = create_member(db_session, "Holder")
    repository = BookRepository(db_session)
    created = create_book(repository, db_session, member.id, "Created")

    found = repository.get(created.id)

    assert found is not None
    assert found.id == created.id
    assert found.title == "Created"
    assert repository.get(999) is None

def test_create_persists_book_and_generates_id(db_session: Session) -> None:
    member = create_member(db_session, "Holder")
    repository = BookRepository(db_session)

    created = repository.create(
        BookInput(
            title="Created",
            author="None",
            isbn="123456789",
            member_id=member.id,
        )
    )
    db_session.commit()

    assert created.id > 0
    stored = repository.get(created.id)
    assert stored is not None
    assert stored.isbn == "123456789"
    assert stored.member_id == member.id


def test_replace_updates_all_editable_book_columns(db_session: Session) -> None:
    original_member = create_member(db_session, "Old")
    replacement_member = create_member(db_session, "New")
    repository = BookRepository(db_session)
    book = create_book(repository, db_session, original_member.id, "Original")

    updated = repository.update(
        book,
        BookPatchInput(
            title="Updated",
            author="New Author",
            isbn="987654321",
            member_id=replacement_member.id
        )
    )
    db_session.commit()
    db_session.refresh(updated)

    assert updated.title == "Updated"
    assert updated.author == "New Author"
    assert updated.isbn == "987654321"
    assert updated.member_id == replacement_member.id


def test_delete_removes_persisted_book(db_session: Session) -> None:
    member = create_member(db_session, "Holder")
    repository = BookRepository(db_session)
    book = create_book(repository, db_session, member.id, "Deleted")

    repository.delete(book)
    db_session.commit()

    assert repository.get(book.id) is None


def test_create_enforces_book_member_foreign_key(db_session: Session) -> None:
    repository = BookRepository(db_session)

    with pytest.raises(IntegrityError):
        repository.create(
            BookInput(
                title="Book of Fake Members",
                author="None",
                isbn="52526",
                member_id=999
            )
        )

    db_session.rollback()
