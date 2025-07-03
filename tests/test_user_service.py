from app.application.commands.user_service import Credentials, UserService
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository


class DummyRepo(UserRepository):
    def __init__(self) -> None:
        self.saved: list[User] = []

    def save(self, user: User) -> None:
        self.saved.append(user)

    def get_by_email(self, email: str) -> User | None:
        return next((u for u in self.saved if u.email == email), None)


def test_register_and_login() -> None:
    repo = DummyRepo()
    service = UserService(repo)
    service.register("Alice", "alice@example.com", "pass")
    saved_user = repo.saved[0]
    assert saved_user.name == "Alice"
    assert saved_user.hashed_password

    assert service.login(Credentials("alice@example.com", "pass"))
    assert not service.login(Credentials("alice@example.com", "wrong"))
