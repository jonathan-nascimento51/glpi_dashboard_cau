class User:
    def __init__(self, user_id: int, name: str):
        self.user_id = user_id
        self.name = name

    def is_valid(self) -> bool:
        return bool(self.name)
