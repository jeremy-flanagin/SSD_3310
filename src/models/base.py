from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Allows the class to be used as a Table in a session"""
