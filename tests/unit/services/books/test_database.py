from collections.abc import Generator

import pytest
from mockito import args, mock, unstub, verify, when

import src.services.books.database as database_module
from src.exceptions import MemberNotFoundException
from src.schema.books import BookInput
from src.services.books.database import DatabaseBookService


@pytest.fixture()
def session_factory() -> Generator[tuple[object, object, object, object], None, None]:
    session = mock()
    factory = mock()
    member_repository = mock()
    book_repository = mock()
    transaction_context = mock()

    # Simulate: ``with session_factory.begin() as session``.
    when(transaction_context).__enter__().thenReturn(session)
    # `__exit__` receives exception details; `args` matches any such values.
    when(transaction_context).__exit__(*args)
    when(factory).begin().thenReturn(transaction_context)
    try:
        # Yield the fake collaborators to the test. Pytest pauses this fixture
        # here while the test runs.
        yield factory, session, member_repository, book_repository
    finally:
        # Remove Mockito stubs so they cannot affect a later test.
        unstub()


def test_create_book_checks_parent_and_uses_book_repository(
    session_factory: tuple[object, object, object, object],
) -> None:
    factory, session, member_repository, book_repository = session_factory
    when(member_repository).get(1).thenReturn(object())
    book = mock()
    when(book_repository).create(...).thenReturn(book)
    when(book_repository).get_all().thenReturn([])

    with (
        when(database_module).MemberRepository(session).thenReturn(
            member_repository
        ),
        when(database_module).BookRepository(session).thenReturn(book_repository),
    ):
        result = DatabaseBookService(factory).create_book(
            BookInput(title="Creation Test",
                      author="Book Repo",
                      isbn="",
                      published_year=2026,
                      member_id=1)
        )

    assert result is book
    verify(member_repository, times=1).get(1)
    verify(book_repository, times=1).get_all()
    verify(book_repository, times=1).create(...)
    verify(session, times=1).refresh(book)


def test_create_book_rejects_missing_parent_without_creating_book(
    session_factory: tuple[object, object, object, object],
) -> None:
    factory, session, member_repository, book_repository = session_factory
    when(member_repository).get(999).thenReturn(None)

    with (
        when(database_module).MemberRepository(session).thenReturn(
            member_repository
        ),
    ):
        with pytest.raises(MemberNotFoundException):
            DatabaseBookService(factory).create_book(
                BookInput(
                    title="Book with no Member",
                    author="None",
                    isbn="",
                    published_year=2000,
                    member_id=999
                )
            )

    verify(book_repository, times=0).create(...)
