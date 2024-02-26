import json
import os
from openai import OpenAI
from pathlib import Path
from datetime import datetime
from random import randint


# Global variables
COLORS = [
    "FE0000",
    "0000FE",
    "028002",
    "B22222",
    "FE7E4F",
    "9BCA31",
    "FE4300",
    "2E8A57",
    "D9A420",
    "D3681E",
    "609E9E",
    "1E90FF",
    "FF69B2",
    "8A2BE1",
]


def get_current_time() -> str:
    """Returns the current date and time formatted as '%d/%m/%y-%H:%M:%S'.
    Example: '31/12/24-23:59:59'.

    Returns:
        str: Current date and time
    """
    return datetime.now().strftime("%x-%X.%f")


def get_current_seconds() -> str:
    """Returns the number of seconds elapsed since January 1, 1970.

    Returns:
        str: _description_
    """
    return int((datetime.now() - datetime(1970, 1, 1)).total_seconds())


def read_json(path: str) -> dict:
    """Read the contents of a json file.

    Args:
        path (str): Path to the json file (relative of absolute)

    Raises:
        FileNotFoundError: The path doesn't exists
        IsADirectoryError: The path leads to a directory
        ValueError: The path leads to a non-json file

    Returns:
        dict: Content of the json file
    """
    path = Path(path).absolute()

    if not path.exists():
        raise FileNotFoundError(f"The path '{path}' doesn't exists.")
    if not path.is_file():
        raise IsADirectoryError(f"The path '{path}' doesn't points to a file but a directory.")
    if path.suffix != ".json":
        raise ValueError(f"The file '{path}' is not json type.")

    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path: str, data: dict) -> None:
    """Write to a json file.

    Args:
        path (str): Path to the json file (relative of absolute)
        data (dict): Dictionary to be written to the json file

    Raises:
        FileNotFoundError: The path doesn't exists
        IsADirectoryError: The path leads to a directory
        ValueError: The path leads to a non-json file
    """
    path = Path(path).absolute()

    if not path.exists():
        raise FileNotFoundError(f"The path '{path}' doesn't exists.")
    if not path.is_file():
        raise IsADirectoryError(f"The path '{path}' doesn't points to a file but a directory.")
    if path.suffix != ".json":
        raise ValueError(f"The file '{path}' is not json type.")

    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def random_digits(n: int) -> str:
    """Generate a random sequence of digits (0-9).

    Args:
        n (int): Number of digits

    Returns:
        str: The random digit sequence
    """
    return "".join(str(randint(0, 9)) for _ in range(n))
