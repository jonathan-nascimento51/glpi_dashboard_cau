from __future__ import annotations

"""Service layer managing user registration and login."""

from dataclasses import dataclass
from uuid import uuid4
from hashlib import sha256

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository


@dataclass
class Credentials:
    email: str
    password: str


class UserService:
    def __init__(self, repo: UserRepository) -> None:
        self._repo = repo

    def register(self, name: str, email: str, password: str) -> User:
        hashed = sha256(password.encode()).hexdigest()
        user = User(uuid4(), name, email)
        self._repo.save(user)
        return user

    def login(self, creds: Credentials) -> bool:
        user = self._repo.get_by_email(creds.email)
        return user is not None
