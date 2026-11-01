# -*- coding: utf-8 -*-
"""Save and persistent progress port interface."""

from typing import Protocol
from domain.model.session import Session


class SavePort(Protocol):
    def load(self) -> Session:
        ...

    def save(self, session: Session) -> bool:
        ...
