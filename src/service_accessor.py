from starlette.requests import Request

from src.services.books.base import BookService
from src.services.members.base import MemberService


def get_book_service(request: Request) -> BookService:
    return request.app.state.book_service


def get_member_service(request: Request) -> MemberService:
    return request.app.state.member_service
