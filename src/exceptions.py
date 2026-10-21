class BookNotFoundException(Exception):
    """Signals that a book has not been found"""

class DuplicateISBNException(Exception):
    """Caused when trying to make a book with an ISBN that is already used"""

class MemberNotFoundException(Exception):
    """Signals that a member has not been found"""

class MemberHasBooksException(Exception):
    """Signals that a member has books and cannot be deleted"""

class DuplicateMembershipException(Exception):
    """Caused when trying to make a Member with a Membership ID that is already used"""

class DuplicateEmailException(Exception):
    """Caused when trying to make a Member with an Email that is already used"""
