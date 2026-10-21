from typing import List

from fastapi import APIRouter, status, HTTPException
from fastapi.params import Depends

from src.exceptions import MemberNotFoundException, MemberHasBooksException, DuplicateEmailException, \
    DuplicateMembershipException
from src.models.book import Book
from src.models.member import Member
from src.router.http_errors import member_not_found, member_must_have_no_books, member_must_have_unique_email, \
    member_must_have_unique_membership
from src.schema.books import BookResponse
from src.schema.members import MemberInput, MemberResponse, MemberPatchInput

from src.service_accessor import get_member_service
from src.services.members.base import MemberService

router = APIRouter(prefix="/members", tags=["Members"])

@router.get(
    path="",
    response_model=List[MemberResponse],
    status_code=status.HTTP_200_OK,
    summary="Gets all members",
    description="Gets all members of the library."
)
def get_members(service: MemberService = Depends(get_member_service)) -> List[MemberResponse]:
    return service.get_members()

@router.get(
    path="/{member_id}",
    response_model=MemberResponse,
    status_code=status.HTTP_200_OK,
    summary="Gets a member",
    description="Gets a member with the given id.",
    responses={404:{"description":"Member not found"}}
)
def get_member(member_id: int, service: MemberService = Depends(get_member_service)) -> Member:
    try:
        return service.get_member(member_id)
    except MemberNotFoundException:
        raise member_not_found(member_id)

@router.get(
    path="/{member_id}/books",
    response_model=List[BookResponse],
    status_code=status.HTTP_200_OK,
    summary="Gets the books a member is holding",
    description="Gets the books a member is holding using the given id.",
    responses = {404: {"description": "Member not found"}}
)
def get_member_books(member_id: int, service: MemberService = Depends(get_member_service)) -> list[Book]:
    try:
        return service.get_member_books(member_id)
    except MemberNotFoundException:
        raise member_not_found(member_id)

@router.post(
    path="",
    response_model=MemberResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a member",
    description="Creates a member from all required inputs.",
    responses = {409:{"description":"Unique value was present"}}
)
def create_member(base: MemberInput, service: MemberService = Depends(get_member_service)) -> Member:
    try:
        return service.create_member(base)
    except DuplicateEmailException:
        raise member_must_have_unique_email()
    except DuplicateMembershipException:
        raise member_must_have_unique_membership()

@router.patch(
    path="/{member_id}",
    response_model=MemberResponse,
    status_code=status.HTTP_200_OK,
    summary="Updates a member",
    description="Updates a member to change some of its content.",
    responses={404:{"description":"Member not found"},
               409:{"description":"Unique value was present"}
              }
)
def update_member(member_id: int, data: MemberPatchInput, service: MemberService = Depends(get_member_service)) -> Member:
    try:
        return service.update_member(member_id, data)
    except MemberNotFoundException:
        raise member_not_found(member_id)
    except DuplicateEmailException:
        raise member_must_have_unique_email()
    except DuplicateMembershipException:
        raise member_must_have_unique_membership()


@router.delete(
    path="/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Deletes a member",
    description="Removes a member from the library",
    responses={
        404:{"description":"Member not found"},
        409:{"description":"Member must have no books"}
    }
)
def delete_member(member_id: int, service: MemberService = Depends(get_member_service)):
    try:
        service.delete_member(member_id)
    except MemberHasBooksException:
        raise member_must_have_no_books(member_id)
    except MemberNotFoundException:
        raise member_not_found(member_id)