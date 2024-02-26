from utils import *
from log import logger


class Filters:
    def __init__(self, inactive_timeout: int = 5) -> None:
        self.inactive_timeout = inactive_timeout

    def _get_data(self, database_path: Path):
        if os.path.exists(database_path):
            return read_json(database_path)
        else:
            raise ValueError("The session id provided is not valid")

    def _reset_session(self, database_path):
        data = {
            "users": {},
            "game": {
                "name": "",
                "host": "",
                "status": "",
                "current_round": 0,
                "players": [],
                "actions": [],
            },
            "chat_history": {},
        }
        write_json(database_path, data)

    def remove_inactive_users(self, session_id: str):
        database_path = Path(f"sessions/{session_id}.json")
        data = self._get_data(database_path)
        user_ids = list(data["users"].keys())
        for user_id in user_ids:
            if get_current_seconds() - data["users"][user_id]["last-active"] > self.inactive_timeout:
                logger.info(f"The user {data['users'][user_id]} has been removed from {database_path}.")
                del data["users"][user_id]  # Safe to delete because we're not iterating over the original dictionary

        if not data["users"]:
            self._reset_session(database_path)
        else:
            write_json(database_path, data)


if __name__ == "__main__":
    print("thread finished...exiting")
