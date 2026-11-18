from datetime import date
from typing import Any

from openapi_spec_validator import validate
from pydantic_extra_types.phone_numbers import PhoneNumber
from starlette.testclient import TestClient

# Utilities

def assert_schema_fields(schema: dict[str, Any], expected_fields: set[str]) -> None:
    """Confirm a component is an object with the expected documented fields."""
    assert schema["type"] == "object"
    assert schema["additionalProperties"] is False
    assert set(schema["properties"]) == expected_fields


def paths_response_schema(
    openapi_document: dict[str, Any],
    path: str,
    method: str,
    status_code: str,
) -> dict[str, str]:
    """Return one operation's JSON response schema from the OpenAPI document."""
    return openapi_document["paths"][path][method]["responses"][status_code][
        "content"
    ]["application/json"]["schema"]


def create_conflict_member(
    database_client: TestClient,
    admin_headers: dict[str, str],
) -> dict[str, Any]:
    """Create a parent Member required by the conflict scenario."""
    response = database_client.post(
        "/members",
        json={
            "name": "Conflict Member",
            "email": "member@email.com",
            "membership_id": "conflict",
            "phone": "443-307-1473"
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    return response.json()


def create_delete_conflict_book(
    database_client: TestClient,
    admin_headers: dict[str, str],
    member_id: int,
) -> dict[str, Any]:
    """Create the Book that makes Member deletion a conflict."""
    response = database_client.post(
        "/books",
        json={
            "title": "Book that causes a Delete Conflict",
            "author": "None",
            "isbn": "123456789",
            "member_id": member_id,
        },
        headers=admin_headers,
    )
    assert response.status_code == 201
    return response.json()

# OPENAPI DOCUMENT VALIDATION


# OPENAPI-SPEC-VALIDATOR TEST
# This is the one direct use of openapi-spec-validator in this member. It
# checks whether the complete generated OpenAPI document is structurally valid.
def test_generated_openapi_document_is_valid(database_client: TestClient) -> None:
    """The API publishes a structurally valid OpenAPI document."""
    response = database_client.get("/openapi.json")

    assert response.status_code == 200
    openapi_document = response.json()
    # The validator raises an exception if FastAPI generated an invalid OpenAPI
    # document. It validates the complete document, not a single data schema.
    validate(openapi_document)


# APPROVED CONTRACT ASSERTIONS
# These tests protect the paths, methods, status codes, and
# component schemas that API consumers are expected to depend on.


def test_openapi_document_declares_the_approved_public_operations(
    database_client: TestClient,
) -> None:
    openapi_document = database_client.get("/openapi.json").json()
    paths = openapi_document["paths"]

    expected_statuses = {
        "/members": {"get": {"200", "401"}, "post": {"201", "401", "403", "409", "422"}},
        "/members/{member_id}": {
            "get": {"200", "401", "404", "422"},
            "patch": {"200", "401", "403", "404", "409", "422"},
            "delete": {"204", "401", "403", "404", "409", "422"},
        },
        "/members/{member_id}/books": {"get": {"200", "401", "404", "422"}},
        "/books": {"get": {"200", "401"}, "post": {"201", "401", "403", "404", "422"}},
        "/books/{book_id}": {
            "get": {"200", "401", "404", "409", "422"},
            "patch": {"200", "401", "403", "404", "409", "422"},
            "delete": {"204", "401", "403", "404", "422"},
        },
    }

    for path, operations in expected_statuses.items():
        assert path in paths
        for method, statuses in operations.items():
            assert method in paths[path]
            documented_statuses = set(paths[path][method]["responses"])
            assert statuses <= documented_statuses


def test_openapi_document_describes_member_and_book_schemas(
    database_client: TestClient,
) -> None:
    """Pydantic request and response rules appear in the public contract."""
    openapi_document = database_client.get("/openapi.json").json()
    schemas = openapi_document["components"]["schemas"]

    assert_schema_fields(schemas["MemberInput"], {"name", "email", "membership_id", "phone"})
    assert_schema_fields(schemas["MemberPatchInput"], {"name", "email", "membership_id", "phone"})
    assert_schema_fields(schemas["MemberResponse"], {"id", "name", "email", "membership_id", "phone"})
    assert_schema_fields(
        schemas["BookInput"],
        {"title", "author", "isbn", "published_year", "member_id"},
    )
    assert_schema_fields(
        schemas["BookPatchInput"],
        {"title", "author", "isbn", "published_year", "member_id"},
    )
    assert_schema_fields(
        schemas["BookResponse"],
        {"id", "title", "author", "isbn", "published_year", "member_id"},
    )

    member_name = schemas["MemberInput"]["properties"]["name"]
    assert member_name["type"] == "string"
    assert member_name["minLength"] == 1
    assert member_name["maxLength"] == 120

    assert "required" not in schemas["MemberPatchInput"]
    patch_name = schemas["MemberPatchInput"]["properties"]["name"]
    assert patch_name["minLength"] == 1
    assert patch_name["maxLength"] == 120


    book_name = schemas["BookInput"]["properties"]["title"]
    assert book_name["type"] == "string"
    assert book_name["minLength"] == 1
    assert book_name["maxLength"] == 200
    book_author = schemas["BookInput"]["properties"]["author"]
    assert book_author["type"] == "string"
    assert book_author["minLength"] == 1
    assert book_author["maxLength"] == 120
    book_date = schemas["BookInput"]["properties"]["published_year"]
    assert book_date["type"] == "integer"
    assert book_date["minimum"] == 1450
    assert book_date["maximum"] == date.today().year

    assert "required" not in schemas["BookPatchInput"]


    member_post_schema = paths_response_schema(
        openapi_document,
        "/members",
        "post",
        "201",
    )
    book_post_schema = paths_response_schema(
        openapi_document,
        "/books",
        "post",
        "201",
    )
    assert member_post_schema == {"$ref": "#/components/schemas/MemberResponse"}
    assert book_post_schema == {"$ref": "#/components/schemas/BookResponse"}


# TARGETED RESPONSE CONFORMANCE
# These tests send known requests and confirm their visible
# HTTP behavior matches the important outcomes documented by the API.


def test_create_member_matches_its_documented_public_response(
    database_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    """A created Member has the documented status and response shape."""
    response = database_client.post(
        "/members",
        json={
            "name": "Contract Test Member",
            "email": "contract_member@testing.org",
            "membership_id": "test_membership",
            "phone": "443-307-1473",
        },
        headers=admin_headers,
    )

    assert response.status_code == 201
    member = response.json()
    assert set(member) == {"id", "name", "email", "membership_id", "phone"}
    assert isinstance(member["id"], int)
    assert member["id"] > 0
    assert member["name"] == "Contract Test Member"
    assert member["email"] == "contract_member@testing.org"
    assert member["membership_id"] == "test_membership"
    assert member["phone"] == "tel:+1-443-307-1473"


def test_missing_member_matches_documented_not_found_response(
    database_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    """A consumer receives the documented 404 outcome for a missing Member."""
    response = database_client.get("/members/999999", headers=admin_headers)

    assert response.status_code == 404
    assert response.json()["detail"]


def test_member_with_books_matches_documented_conflict_response(
    database_client: TestClient,
    admin_headers: dict[str, str],
) -> None:
    """Deleting a Member with Books returns the documented 409 outcome."""
    member = create_conflict_member(database_client, admin_headers)
    create_delete_conflict_book(database_client, admin_headers, member["id"])

    response = database_client.delete(
        f"/members/{member['id']}", headers=admin_headers
    )

    assert response.status_code == 409
    assert response.json()["detail"]
