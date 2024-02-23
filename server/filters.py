
class Filters:
    def __init__(self, databases_path: list[str]) -> None:
        pass

    def remove_inactive_users(self, database_path: str):
        for user_id in database_path["users"]:
            pass