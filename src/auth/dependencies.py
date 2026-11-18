from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.config import Settings
from src.service_accessor import get_settings
from src.auth.users import AuthenticatedUser, Role, get_user_for_token

bearer_scheme = HTTPBearer(auto_error=False, scheme_name="BearerAuthentication")
BearerCredentials = Annotated[
    HTTPAuthorizationCredentials | None,
    Depends(bearer_scheme),
]

UNAUTHORIZED_RESPONSE = {
    "description": "Missing or invalid Bearer token",
    "headers": {
        "WWW-Authenticate": {
            "description": "Authentication scheme required by this endpoint.",
            "schema": {"type": "string"},
        }
    },
}
FORBIDDEN_RESPONSE = {"description": "Administrator role required"}
AUTHENTICATED_RESPONSES = {401: UNAUTHORIZED_RESPONSE}
ADMIN_RESPONSES = {401: UNAUTHORIZED_RESPONSE, 403: FORBIDDEN_RESPONSE}


def unauthenticated() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing or invalid Bearer token",
        headers={"WWW-Authenticate": "Bearer"},
    )


AppSettings = Annotated[Settings, Depends(get_settings)]


def get_current_user(
    credentials: BearerCredentials,
    settings: AppSettings,
) -> AuthenticatedUser:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise unauthenticated()

    user = get_user_for_token(credentials.credentials, settings)
    if user is None:
        raise unauthenticated()
    return user


CurrentUser = Annotated[AuthenticatedUser, Depends(get_current_user)]


def require_admin(current_user: CurrentUser) -> AuthenticatedUser:
    if current_user.role is not Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Administrator role required",
        )
    return current_user


AdminUser = Annotated[AuthenticatedUser, Depends(require_admin)]
