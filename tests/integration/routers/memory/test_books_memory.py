from starlette.testclient import TestClient

# Utilities

def create_member(
    memory_client: TestClient,
    admin_headers: dict[str, str],
) -> dict:
    response = memory_client.post(
        "/members",
        json={
            "name": "Memory Member",
            "email": "member@email.com",
            "membership_id": "memory_test",
            "phone": "443-307-1473"
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    return response.json()


# Tests

def test_book_crud_works_with_memory_client(
    memory_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    member = create_member(memory_client, admin_headers)
    create_response = memory_client.post(
        "/books",
        json={
            "title": "Book of Memories",
            "author": "Memory Client",
            "isbn": "123456789",
            "member_id": member["id"],
        },
        headers=admin_headers,
    )

    assert create_response.status_code == 201
    book = create_response.json()

    get_response = memory_client.get(
        f"/books/{book['id']}", headers=admin_headers
    )
    assert get_response.status_code == 200
    assert get_response.json() == book

    update_response = memory_client.patch(
        f"/books/{book['id']}",
        json={
            "title": "Updated Memory Book",
            "author": "Memory Client",
            "isbn": "123456789",
            "member_id": member["id"],
        },
        headers=admin_headers,
    )
    assert update_response.status_code == 200

    delete_response = memory_client.delete(
        f"/books/{book['id']}", headers=admin_headers
    )
    assert delete_response.status_code == 204
    assert delete_response.content == b""
    assert memory_client.get("/books", headers=admin_headers).json() == []