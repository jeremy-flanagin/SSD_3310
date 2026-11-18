from collections.abc import Generator

import pytest
from mockito import args, mock, unstub, verify, when
from pydantic.v1.networks import EmailStr

import src.services.members.database as member_database
from src.exceptions import MemberNotFoundException, DuplicateMembershipException, DuplicateEmailException
from src.models.member import Member
from src.schema.members import MemberInput
from src.services.members.database import DatabaseMemberService


@pytest.fixture()
def session_factory() -> Generator[tuple[object, object, object], None, None]:
    session = mock()
    factory = mock()
    repository = mock()
    read_context = mock()
    transaction_context = mock()

    # Simulate: ``with session_factory() as session``.
    when(read_context).__enter__().thenReturn(session)
    # `__exit__` receives exception type, value, and traceback; Mockito's
    # `args` matcher accepts any values for those cleanup arguments.
    when(read_context).__exit__(*args)
    when(factory).__call__().thenReturn(read_context)

    # Simulate: ``with session_factory.begin() as session``.
    when(transaction_context).__enter__().thenReturn(session)
    # Match all arguments passed when Python leaves the `with` block.
    when(transaction_context).__exit__(*args)
    when(factory).begin().thenReturn(transaction_context)

    try:
        # Yield the fake collaborators to the test. Pytest pauses this fixture
        # here while the test runs.
        yield factory, session, repository
    finally:
        # Remove Mockito stubs so they cannot affect a later test.
        unstub()


def test_create_member_uses_repository_and_transaction(
    session_factory: tuple[object, object, object],
) -> None:
    factory, session, repository = session_factory
    member = mock()
    existing_member = mock()

    when(Member).id.returns(0)
    when(Member).email.returns("mock@email.com")
    when(Member).membership_id.returns("mock_membership")

    when(repository).create(...).thenReturn(member)
    when(repository).get_all().thenReturn([existing_member])

    with when(member_database).MemberRepository(session).thenReturn(repository):
        result = DatabaseMemberService(factory).create_member(
            MemberInput(
                name="Test Member",
                email=EmailStr("member@tests.net"),
                membership_id="test_membership",
                phone="443-307-1473"
            )
        )

    assert result is member
    verify(repository, times=1).get_all()
    verify(repository, times=1).create(...)
    verify(session, times=1).refresh(member)
    verify(factory, times=1).begin()

def test_create_member_fails_on_duplicate_membership_id(
    session_factory: tuple[object, object, object],
) -> None:
    factory, session, repository = session_factory
    member = mock()
    duplicate_member = Member(
        id=0,
        name="",
        email="",
        membership_id="test_membership",
        phone=""
    )

    when(repository).create(...).thenReturn(member)
    when(repository).get_all().thenReturn([duplicate_member])

    with when(member_database).MemberRepository(session).thenReturn(repository):
        with pytest.raises(DuplicateMembershipException):
            DatabaseMemberService(factory).create_member(
                MemberInput(
                    name="Test Member",
                    email=EmailStr("member@tests.net"),
                    membership_id="test_membership",
                    phone="443-307-1473"
                )
            )

def test_create_member_fails_on_duplicate_email(
    session_factory: tuple[object, object, object],
) -> None:
    factory, session, repository = session_factory
    member = mock()
    duplicate_member = Member(
        id=0,
        name="",
        email="member@tests.net",
        membership_id="",
        phone=""
    )

    when(repository).create(...).thenReturn(member)
    when(repository).get_all().thenReturn([duplicate_member])

    with when(member_database).MemberRepository(session).thenReturn(repository):
        with pytest.raises(DuplicateEmailException):
            DatabaseMemberService(factory).create_member(
                MemberInput(
                    name="Test Member",
                    email=EmailStr("member@tests.net"),
                    membership_id="test_membership",
                    phone="443-307-1473"
                )
            )


def test_get_member_no_member_error_produces_right_exception(
    session_factory: tuple[object, object, object],
) -> None:
    factory, session, repository = session_factory
    when(repository).get(999).thenReturn(None)

    with when(member_database).MemberRepository(session).thenReturn(repository):
        with pytest.raises(MemberNotFoundException):
            DatabaseMemberService(factory).get_member(999)
