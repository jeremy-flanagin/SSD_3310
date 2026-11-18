
import pytest
from starlette.testclient import TestClient



def test_root_and_health_remain_public(database_client: TestClient) -> None:
    assert database_client.get("/").status_code == 200
    assert database_client.get("/health").status_code == 200


def test_protected_read_rejects_a_missing_token(database_client: TestClient) -> None:
    response = database_client.get("/members")

    assert response.status_code == 401
    assert response.json() == {"detail": "Missing or invalid Bearer token"}
    assert response.headers["www-authenticate"] == "Bearer"


def test_protected_read_rejects_an_unknown_token(database_client: TestClient) -> None:
    response = database_client.get(
        "/books",
        headers={"Authorization": "Bearer not-a-demo-token"},
    )

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


@pytest.mark.parametrize("path", ["/members", "/books"])
def test_member_can_read_protected_collections(
    database_client: TestClient,
    member_headers: dict[str, str],
    path: str,
) -> None:
    response = database_client.get(path, headers=member_headers)

    assert response.status_code == 200
    assert response.json() == []



@pytest.mark.parametrize(
    ("method", "path", "json_body"),
    [
        ("POST", "/members", {"name": "Member member", "description": "Denied."}),
        ("PUT", "/members/999999", {"name": "Member member", "description": "Denied."}),
        ("DELETE", "/members/999999", None),
        (
            "POST",
            "/books",
            {
                "title": "Member book",
                "author": "None",
                "isbn": "",
                "member_id": 999999,
            },
        ),
        (
            "PUT",
            "/books/999999",
            {
                "title": "Member book",
                "author": "None",
                "isbn": "",
                "member_id": 999999,
            },
        ),
        ("DELETE", "/books/999999", None),
    ],
)
def test_member_cannot_use_administrator_only_write_routes(
    database_client: TestClient,
    member_headers: dict[str, str],
    method: str,
    path: str,
    json_body: dict[str, object] | None,
) -> None:
    response = database_client.request(
        method,
        path,
        json=json_body,
        headers=member_headers,
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Administrator role required"}


def test_administrator_can_complete_a_member_and_book_write_workflow(
    database_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    member_response = database_client.post(
        "/members",
        json={
            "name": "Authorized member",
            "email": "member@email.com",
            "membership_id": "authorized",
            "phone": "443-307-1473"
        },
        headers=admin_headers,
    )
    assert member_response.status_code == 201
    member = member_response.json()

    book_response = database_client.post(
        "/books",
        json={
            "title": "Authorized book",
            "author": "None",
            "isbn": "123456789",
            "member_id": member["id"],
        },
        headers=admin_headers,
    )
    assert book_response.status_code == 201
    book = book_response.json()

    replace_response = database_client.put(
        f"/books/{book['id']}",
        json={
            "title": "Completed book",
            "author": "None",
            "isbn": "123456789",
            "member_id": member["id"],
        },
        headers=admin_headers,
    )
    assert replace_response.status_code == 200
    assert replace_response.json()["completed"] is True

    assert (
        database_client.delete(
            f"/books/{book['id']}", headers=admin_headers
        ).status_code
        == 204
    )
    assert (
        database_client.delete(
            f"/members/{member['id']}", headers=admin_headers
        ).status_code
        == 204
    )
