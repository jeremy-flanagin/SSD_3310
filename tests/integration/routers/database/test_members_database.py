from starlette.testclient import TestClient


# Utilities

def create_member(
    database_client: TestClient,
    admin_headers: dict[str, str],
    name: str,
) -> dict:
    response = database_client.post(
        "/members",
        json={
            "name": name,
            "email": name + "@email.com",
            "membership_id": name + "_membership",
            "phone": "443-307-1473"
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    return response.json()


# Tests

def test_create_list_and_get_members(
    database_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    first_member = create_member(database_client, admin_headers, "First")
    second_member = create_member(database_client, admin_headers, "Second")

    list_response = database_client.get("/members", headers=admin_headers)

    assert list_response.status_code == 200
    assert list_response.json() == [first_member, second_member]

    get_response = database_client.get(
        f"/members/{first_member['id']}", headers=admin_headers
    )

    assert get_response.status_code == 200
    assert get_response.json() == first_member


def test_replace_member_updates_the_public_resource(
    database_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    member = create_member(database_client, admin_headers, "Original")

    update_response = database_client.patch(
        f"/members/{member['id']}",
        json={
            "name": "Updated",
            "email": "member@email.com",
            "membership_id": "membership",
            "phone": "443-307-1473"
        },
        headers=admin_headers,
    )

    assert update_response.status_code == 200
    updated_member = update_response.json()
    assert updated_member == {
        "id": member["id"],
        "name": "Updated",
        "email": "member@email.com",
        "membership_id": "membership",
        "phone": "tel:+1-443-307-1473"
    }

    get_response = database_client.get(
        f"/members/{member['id']}", headers=admin_headers
    )
    assert get_response.status_code == 200
    assert get_response.json() == updated_member


def test_delete_member_removes_the_public_resource(
    database_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    member = create_member(database_client, admin_headers, "Deleted")

    delete_response = database_client.delete(
        f"/members/{member['id']}", headers=admin_headers
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    list_response = database_client.get("/members", headers=admin_headers)
    assert list_response.status_code == 200
    assert list_response.json() == []


def test_list_member_books_returns_related_books(
    database_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    member = create_member(database_client, admin_headers, "Holder")

    first_book_response = database_client.post(
        "/books",
        json={
            "title": "First Book",
            "author": "First Author",
            "isbn": "123456789",
            "member_id": member["id"],
        },
        headers=admin_headers,
    )
    second_book_response = database_client.post(
        "/books",
        json={
            "title": "Second Book",
            "author": "Second Author",
            "isbn": "2345678910",
            "member_id": member["id"],
        },
        headers=admin_headers,
    )
    assert first_book_response.status_code == 201
    assert second_book_response.status_code == 201

    response = database_client.get(
        f"/members/{member['id']}/books", headers=admin_headers
    )

    assert response.status_code == 200
    assert response.json() == [first_book_response.json(), second_book_response.json()]