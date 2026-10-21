from fastapi.exceptions import HTTPException
from starlette import status


def book_not_found(book_id: int) -> HTTPException:
    """Returns an 404 HTTP exception detailing that a book
       has not been found."""
    return HTTPException(
        status_code= status.HTTP_404_NOT_FOUND,
        detail="Book not found",
        headers={"book_id": str(book_id)}
    )

def book_must_have_unique_isbn() -> HTTPException:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                        detail="A book with that ISBN already exists",
                        )

def member_not_found(member_id: int) -> HTTPException:
    """Returns an 404 HTTP exception detailing that a member
       has not been found."""
    return HTTPException(
        status_code= status.HTTP_404_NOT_FOUND,
        detail="Member not found",
        headers={"member_id": str(member_id)}
    )

def member_must_have_no_books(member_id: int) -> HTTPException:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                        detail="Member must have no books",
                        headers={"member_id": str(member_id)}
                        )

def member_must_have_unique_email() -> HTTPException:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                        detail="A Member with that email already exists."
                        )

def member_must_have_unique_membership() -> HTTPException:
    raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                        detail="A Member with that membership already exists."
                        )