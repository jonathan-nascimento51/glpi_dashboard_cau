from __future__ import annotations

import abc
from typing import Optional
from uuid import UUID

from app.domain.entities.user import User


class UserRepository(abc.ABC):
    @abc.abstractmethod
    def save(self, user: User) -> None: ...

    @abc.abstractmethod
    def get_by_email(self, email: str) -> Optional[User]: ...
