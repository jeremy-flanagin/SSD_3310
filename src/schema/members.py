from typing import Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator, EmailStr

from src.storage import members

class MemberBase(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True
    )

    name: str = Field(
        min_length=1,
        max_length=120,
        description="The name of the member.",
        examples=["Dane Deckerson"]
    )
    email: EmailStr = Field(
        description="The member's email address.",
        examples=["DaneDeckerson@gmail.com"]
    )
    membership_id: str = Field(
        description="The id of the membership held by the member.",
    )
    phone: str = Field(
        description="The member's phone number.",
        examples=["491-526-5225"],
    )


    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        for member in members:
            if member.email == v:
                raise ValueError("Must be unique")
        return v


    @field_validator("membership_id")
    @classmethod
    def validate_membership_id(cls, v):
        for member in members:
            if member.membership_id == v:
                raise ValueError("Must be unique")
        return v

class MemberInput(MemberBase):
    pass

class MemberPatchInput(MemberBase):
    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
        str_strip_whitespace=True
    )

    name: str
    email: Optional[EmailStr] = Field(
        description="The member's email address.",
        examples=["DaneDeckerson@gmail.com"]
    )
    membership_id: Optional[str] = Field(
        description="The id of the membership held by the member.",
    )
    phone: Optional[str] = Field(
        description="The member's phone number.",
        examples=["491-526-5225"]
    )

    @field_validator("email")
    @classmethod
    def validate_email(cls, v):
        for member in members:
            if member.email == v:
                raise ValueError("Must be unique")
        return v

    @field_validator("membership_id")
    @classmethod
    def validate_membership_id(cls, v):
        for member in members:
            if member.membership_id == v:
                raise ValueError("Must be unique")
        return v

class MemberResponse(MemberBase):
    id: int = Field(
        description="The id of the member.",
        examples=[1]
    )