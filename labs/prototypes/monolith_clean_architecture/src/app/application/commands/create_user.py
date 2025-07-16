from app.domain.entities.user import User


class CreateUser:
    def execute(self, user_id: int, name: str) -> User:
        user = User(user_id, name)
        # Regra simples: deve ter nome
        if not user.is_valid():
            raise ValueError("Nome obrigatório")
        return user
