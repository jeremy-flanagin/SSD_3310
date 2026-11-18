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
            "email": "member@email.com",
            "membership_id": "membership",
            "phone": "443-307-1473"
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    return response.json()


def create_book(
    database_client: TestClient,
    admin_headers: dict[str, str],
    member_id: int,
    title: str,
) -> dict:
    response = database_client.post(
        "/books",
        json={
            "title": title,
            "author": "None",
            "isbn": "123456789",
            "member_id": member_id,
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    return response.json()


# Tests

def test_create_list_and_get_books(
    database_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    member = create_member(database_client, admin_headers, "Holder")
    first_book = create_book(database_client, admin_headers, member["id"], "First")
    second_book = create_book(database_client, admin_headers, member["id"], "Second")

    list_response = database_client.get("/books", headers=admin_headers)

    assert list_response.status_code == 200
    assert list_response.json() == [first_book, second_book]

    get_response = database_client.get(
        f"/books/{first_book['id']}", headers=admin_headers
    )

    assert get_response.status_code == 200
    assert get_response.json() == first_book


def test_replace_book_updates_the_public_resource(
    database_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    original_member = create_member(database_client, admin_headers, "Original Member")
    replacement_member = create_member(
        database_client, admin_headers, "Replacement Member"
    )
    book = create_book(database_client, admin_headers, original_member["id"], "Original Book")

    replace_response = database_client.put(
        f"/books/{book['id']}",
        json={
            "title": "Updated Book",
            "author": "API",
            "isbn": "123456789",
            "member_id": replacement_member["id"],
        },
        headers=admin_headers,
    )

    assert replace_response.status_code == 200
    updated_book = replace_response.json()
    assert updated_book == {
        "id": book["id"],
        "title": "Updated Book",
        "author": "API",
        "isbn": "123456789",
        "member_id": replacement_member["id"],
    }

    get_response = database_client.get(
        f"/books/{book['id']}", headers=admin_headers
    )
    assert get_response.status_code == 200
    assert get_response.json() == updated_book


def test_delete_book_removes_the_public_resource(
    database_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    member = create_member(database_client, admin_headers, "Holder")
    book = create_book(database_client, admin_headers, member["id"], "Deleted Book")

    delete_response = database_client.delete(
        f"/books/{book['id']}", headers=admin_headers
    )

    assert delete_response.status_code == 204
    assert delete_response.content == b""

    list_response = database_client.get("/books", headers=admin_headers)
    assert list_response.status_code == 200
    assert list_response.json() == []