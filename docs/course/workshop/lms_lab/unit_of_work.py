"""Small transaction boundary: repositories never commit."""
from typing import Protocol


class Transaction(Protocol):
    def commit(self) -> None: ...
    def rollback(self) -> None: ...


class SqlTransaction:
    def __init__(self, session):
        self.session = session

    def commit(self) -> None:
        self.session.commit()

    def rollback(self) -> None:
        self.session.rollback()
