from datetime import date
from typing import Dict, Tuple

import pytest
from phonenumbers import PhoneNumber
from pydantic import ValidationError, BaseModel
from pydantic.fields import FieldInfo

from src.schema.members import MemberInput, MemberPatchInput, MemberResponse


# Utilities
@pytest.fixture(scope="function", params=[MemberInput, MemberPatchInput])
def member_base(request) -> type[BaseModel]:
    return request.param

@pytest.fixture(scope="function")
def member_fields() -> Dict[str, any]:
    return {
        "name": "Dane Deckerson",
        "email": "DaneDeckerson@gmail.com",
        "membership_id": "9781566199094",
        "phone": "214-895-3258"
    }

@pytest.fixture(scope='function', params=[
    pytest.param((" filled ", "filled"), id="single_whitespace"),
    pytest.param(("  doublefilled  ", "doublefilled"), id="double_whitespace")
])
def whitespace_values(request) -> Tuple[str, str]:
    return request.param


# MemberBase and MemberPatchInput

@pytest.mark.parametrize("field", ["name", "email", "membership_id", "phone"])
def test_member_create_requires_fields(member_fields: Dict[str, any], field: str) -> None:
    member_fields.pop(field)

    with pytest.raises(ValidationError):
        MemberInput(**member_fields)


def test_member_update_does_not_require_fields() -> None:
    MemberPatchInput(**{})

@pytest.mark.parametrize("boundary_value", [
    ("name", "a"),
    ("name", "b" * 120),
    ("email","dane.deckerson@gmail.com"),
])
def test_member_model_passes_with_valid_boundaries(member_base: type[BaseModel], member_fields: Dict[str, any], boundary_value: Tuple[str, any]) -> None:
    member_fields[boundary_value[0]] = boundary_value[1]
    member_base(**member_fields)


@pytest.mark.parametrize("boundary_value", [
    ("name", ""),
    ("name", "b" * 121),
    ("email", "dane_deckerson@gmail"),
    ("email","dane.deckerson.gmail.com"),
    ("email", "dane._deckerson@gmail._com"),
    ("phone", "592-382-2849")
])
def test_member_model_fails_with_invalid_boundaries(member_base: type[BaseModel],
                                                   member_fields: Dict[str, any],
                                                   boundary_value: Tuple[str, any]) -> None:
    member_fields[boundary_value[0]] = boundary_value[1]

    with pytest.raises(ValidationError):
        member_base(**member_fields)

@pytest.mark.parametrize("key", ["name", "membership_id"])
def test_member_model_trims_whitespace(member_base: type[BaseModel], 
                                      member_fields: Dict[str, any],
                                      key: str, 
                                      whitespace_values: Tuple[str, str]) -> None:
    member_fields[key] = whitespace_values[0]

    member_input = member_base(**member_fields)
    assert member_input.model_dump()[key] == whitespace_values[1]


def test_member_model_rejects_unknown_fields(member_base: type[BaseModel],
                                            member_fields: Dict[str, any]) -> None:
    member_fields["unknown_field"] = "kaofiensoai"

    with pytest.raises(ValidationError):
        member_base(**member_fields)

# GET

@pytest.mark.parametrize("id", [-1])
def test_member_response_rejects_negative_ids(member_fields: Dict[str, any], id: int) -> None:
    member_fields["id"] = id

    with pytest.raises(ValidationError):
        MemberResponse(**member_fields)


@pytest.mark.parametrize("id", [0])
def test_member_response_is_valid_with_boundary_id(member_fields: Dict[str, any], id: int) -> None:
    member_fields["id"] = id

    with pytest.raises(ValidationError):
        MemberResponse(**member_fields)