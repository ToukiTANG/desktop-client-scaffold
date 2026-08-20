from api.person_api import PersonApi


class AppApi:
    def __init__(self) -> None:
        self.person = PersonApi()

    def _bind_window(self, window) -> None:
        self.person._bind_window(window)

    def ping(self):
        return {"success": True, "data": "pong", "message": None}
