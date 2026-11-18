from starlette.testclient import TestClient


# Utilities


def create_member(
    memory_client: TestClient,
    admin_headers: dict[str, str],
) -> dict:
    """Create one Member through the memory-backed public API."""
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

def test_member_crud_works_with_memory_client(
    memory_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    create_response = memory_client.post(
        "/members",
        json={
            "name": "Memory Member",
            "description": "Stored by the in-memory service.",
        },
        headers=admin_headers,
    )

    assert create_response.status_code == 201
    member = create_response.json()

    get_response = memory_client.get(
        f"/members/{member['id']}", headers=admin_headers
    )
    assert get_response.status_code == 200
    assert get_response.json() == member

    replace_response = memory_client.put(
        f"/members/{member['id']}",
        json={
            "name": "Updated Memory Member",
            "description": "Updated without PostgreSQL.",
        },
        headers=admin_headers,
    )
    assert replace_response.status_code == 200

    delete_response = memory_client.delete(
        f"/members/{member['id']}", headers=admin_headers
    )
    assert delete_response.status_code == 204
    assert delete_response.content == b""
    assert memory_client.get("/members", headers=admin_headers).json() == []


def test_member_books_route_works_with_memory_client(
    memory_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    """The memory services preserve the Member-to-Book relationship."""
    member = create_member(memory_client, admin_headers)
    book_response = memory_client.post(
        "/books",
        json={
            "title": "Memory Book",
            "description": "Related to an in-memory member.",
            "completed": False,
            "member_id": member["id"],
        },
        headers=admin_headers,
    )
    assert book_response.status_code == 201

    response = memory_client.get(
        f"/members/{member['id']}/books", headers=admin_headers
    )

    assert response.status_code == 200
    assert response.json() == [book_response.json()]