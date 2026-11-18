from starlette.requests import Request

from src.services.books.base import BookService
from src.services.members.base import MemberService


def get_settings(request: Request):
    return request.app.settings

def get_book_service(request: Request) -> BookService:
    return request.app.book_service


def get_member_service(request: Request) -> MemberService:
    return request.app.member_service
