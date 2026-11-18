from dataclasses import dataclass
from enum import Enum

from src.config import Settings


class Role(str, Enum):

    MEMBER = "member"
    ADMIN = "admin"


@dataclass(frozen=True)
class AuthenticatedUser:

    username: str
    role: Role


def get_token_for_role(role: Role, settings: Settings) -> str:
    if role is Role.MEMBER:
        return settings.member_token
    return settings.admin_token


def get_user_for_token(token: str, settings: Settings) -> AuthenticatedUser | None:
    member_token = get_token_for_role(Role.MEMBER, settings)
    admin_token = get_token_for_role(Role.ADMIN, settings)

    if member_token and token == member_token:
        return AuthenticatedUser(username="member", role=Role.MEMBER)
    if admin_token and token == admin_token:
        return AuthenticatedUser(username="admin", role=Role.ADMIN)
    return None
