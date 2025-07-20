from typing import Union


class GLPI_APP_TOKEN:
    def __init__(self, token: str):
        self.token = token

    def __str__(self):
        return self.token


class SomeClass:
    def __init__(self, app_token: Union[str, GLPI_APP_TOKEN]):
        self.app_token = str(app_token)  # Ensure it's stored as a string


token = GLPI_APP_TOKEN("my-token")
instance = SomeClass(app_token=token)
