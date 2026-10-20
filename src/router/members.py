from typing import List

from fastapi import APIRouter, status, HTTPException

from src.schema.books import BookResponse
from src.schema.members import MemberInput, MemberResponse, MemberPatchInput
from src.storage import members, books

router = APIRouter(prefix="/members", tags=["Members"])


def get_next_member_id() -> int:
    return max((member.id for member in members), default=0) + 1

def get_member_index(member_id: int) -> int:
    for index, member in enumerate(members):
        if member.id == member_id:
            return index

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Member not found",
    )

def find_member(member_id: int) -> MemberResponse:
    for member in members:
        if member.id == member_id:
            return member

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Member not found",
    )

def set_member(member_id: int, new_member: MemberResponse):
    for index, member in enumerate(members):
        if member.id == member_id:
            members[index] = new_member
            return
    members.append(new_member)

@router.post(
    path="",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a member",
    description="Creates a member from all required inputs."
)
def create_member(base: MemberInput) -> MemberResponse:
    next_id = get_next_member_id()
    member = MemberResponse(id=next_id, **base.model_dump())
    members.append(member)
    return member

@router.get(
    path="",
    response_model=List[MemberResponse],
    status_code=status.HTTP_200_OK,
    summary="Gets all members",
    description="Gets all members of the library."
)
def get_members() -> List[MemberResponse]:
    return members

@router.get(
    path="/{member_id}",
    response_model=MemberResponse,
    status_code=status.HTTP_200_OK,
    summary="Gets a member",
    description="Gets a member with the given id.",
    responses={404:{"description":"Member not found"}}
)
def get_member(member_id: int) -> MemberResponse:
    return find_member(member_id)

@router.get(
    path="/{member_id}/books",
    response_model=List[BookResponse],
    status_code=status.HTTP_200_OK,
    summary="Gets the books a member is holding",
    description="Gets the books a member is holding using the given id.",
    responses = {404: {"description": "Member not found"}}
)
def get_member_books(member_id: int) -> List[BookResponse]:
    find_member(member_id)
    return [book for book in books if member_id == book.member_id]

@router.patch(
    path="/{member_id}",
    response_model=MemberResponse,
    status_code=status.HTTP_200_OK,
    summary="Updates a member",
    description="Updates a member to change some of its content.",
    responses={404:{"description":"Member not found"}}
)
def update_member(member_id: int, data: MemberPatchInput) -> MemberResponse:
    member = find_member(member_id)
    update_data = data.model_dump(exclude_unset=True, exclude_none=True)
    modified_member = member.model_copy(update=update_data)
    set_member(member_id, modified_member)
    return modified_member

@router.delete(
    path="/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletes a member",
    description="Removes a member from the library",
    responses={409:{"description":"Member must have no books"}}
)
def delete_member(member_id: int):
    held_books = get_member_books(member_id)
    if len(held_books) > 0: raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Member must have no books")
    index = get_member_index(member_id)
    members.pop(index)