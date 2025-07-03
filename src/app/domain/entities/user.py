from dataclasses import dataclass
from uuid import UUID


@dataclass
class User:
    """Simple user entity."""

    user_id: UUID
    name: str
    email: str
