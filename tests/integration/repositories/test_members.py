from phonenumbers.phonenumber import PhoneNumber
from sqlalchemy.orm import Session

from src.repositories.member import MemberRepository
from src.schema.members import MemberInput, MemberPatchInput


# Utilities

def create_and_add_member(repository: MemberRepository, session: Session, name: str):
    member = repository.create(
        MemberInput(name=name,
                    email="mail@mail.com",
                    membership_id="",
                    phone="443-307-1473")
    )
    session.commit()
    session.refresh(member)
    return member

# Tests

def test_get_all_returns_members_in_id_order(db_session: Session) -> None:
    repository = MemberRepository(db_session)
    first = create_and_add_member(repository, db_session, "First")
    second = create_and_add_member(repository, db_session, "Second")

    members = repository.get_all()

    assert [member.id for member in members] == [first.id, second.id]


def test_get_returns_existing_member_and_none_when_missing(
    db_session: Session,
) -> None:
    repository = MemberRepository(db_session)
    member = repository.create(
        MemberInput(name="Stored",
                    email="mail@mail.com",
                    membership_id="",
                    phone="443-307-1473")
    )

    found = repository.get(member.id)

    assert found is not None
    assert found.id == member.id
    assert found.name == "Stored"
    assert repository.get(999) is None


def test_create_stores_member_and_generates_id(db_session: Session) -> None:
    repository = MemberRepository(db_session)

    created = create_and_add_member(repository, db_session, "Created")
    db_session.commit()

    assert created.id > 0
    stored = repository.get(created.id)
    assert stored is not None
    assert stored.name == "Created"
    assert stored.email == "mail@mail.com"


def test_replace_updates_persisted_member(db_session: Session) -> None:
    repository = MemberRepository(db_session)
    member = create_and_add_member(repository, db_session, "Original")

    updated = repository.update(
        member,
        MemberPatchInput(name="Updated"),
    )
    db_session.commit()
    db_session.refresh(updated)

    assert updated.name == "Updated"

def test_delete_removes_persisted_member(db_session: Session) -> None:
    repository = MemberRepository(db_session)
    member = create_and_add_member(repository, db_session, "Deleted")

    repository.delete(member)
    db_session.commit()

    assert repository.get(member.id) is None