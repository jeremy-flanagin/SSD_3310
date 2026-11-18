import pytest
from starlette.testclient import TestClient

def test_create_member_rejects_missing_required_field(
    database_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    """A request without the required description is rejected with 422."""
    response = database_client.post(
        "/members", json={"name": "Incomplete Member"}, headers=admin_headers
    )

    assert_validation_error(response)


def test_create_member_rejects_undocumented_field(
    database_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    """extra='forbid' prevents a client from sending an unknown JSON field."""
    response = database_client.post(
        "/members",
        json={
            "name": "Unexpected Field",
            "description": "This request includes a field outside the contract.",
            "owner": "Undocumented client value",
        },
        headers=admin_headers,
    )

    assert_validation_error(response)


# PATH-PARAMETER VALIDATION
# FastAPI validates the typed `int` path parameters before it calls a route.


@pytest.mark.parametrize(
    "path",
    ["/members/not-an-integer", "/books/not-an-integer"],
    ids=["member-id", "book-id"],
)
def test_typed_path_parameters_reject_wrong_data_type(
    database_client: TestClient,
    admin_headers: dict[str, str],
    path: str,
) -> None:
    """FastAPI rejects a non-integer resource identifier before the route runs."""
    response = database_client.get(path, headers=admin_headers)

    assert_validation_error(response)


# RESOURCE AND BUSINESS-RULE REJECTIONS
# These requests have a valid shape, so the application layers decide whether
# the requested resource or relationship is allowed and return 404 or 409.


@pytest.mark.parametrize(
    "path",
    ["/members/999999", "/books/999999"],
    ids=["member", "book"],
)
def test_missing_resources_return_not_found(
    database_client: TestClient,
    admin_headers: dict[str, str],
    path: str,
) -> None:
    """A valid identifier with no matching resource returns the documented 404."""
    response = database_client.get(path, headers=admin_headers)

    assert response.status_code == 404
    assert response.json()["detail"]


def test_create_book_rejects_nonexistent_parent_member(
    database_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    """The Book relationship rule becomes a client-visible 404 response."""
    response = database_client.post(
        "/books",
        json={
            "title": "Orphan Book",
             "author": "NONE",
             "isbn": "",
            "member_id": 999999,
        },
        headers=admin_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"]


def test_delete_member_rejects_member_with_related_books(
    database_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    """A Member with Books remains protected by the documented 409 conflict."""
    member = create_member(database_client, admin_headers)
    create_book(database_client, admin_headers, member["id"])

    response = database_client.delete(
        f"/members/{member['id']}", headers=admin_headers
    )

    assert response.status_code == 409
    assert response.json()["detail"]


# Utilities


def assert_validation_error(response) -> None:
    """Check FastAPI's stable 422 status and validation-error response shape."""
    assert response.status_code == 422
    detail = response.json()["detail"]
    assert isinstance(detail, list)
    assert detail


def create_member(
    database_client: TestClient,
    admin_headers: dict[str, str],
) -> dict:
    """Create a Member needed by the deletion-conflict negative test."""
    response = database_client.post(
        "/members",
        json={
            "name": "Protected Member",
            "email": "protection@test.gov",
            "membership_id":"",
            "phone":"443-307-1473"
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    return response.json()


def create_book(
    database_client: TestClient,
    admin_headers: dict[str, str],
    member_id: int,
) -> dict:
    """Create a related Book that makes the Member deletion invalid."""
    response = database_client.post(
        "/books",
        json={
            "title": "Protected Book",
            "author": "NONE",
            "isbn": "",
            "member_id": member_id
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    return response.json()
