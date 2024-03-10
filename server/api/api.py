import os
import json
from openai import OpenAI

credentials_path = os.path.join(os.path.dirname(__file__), "credentials.json")
with open(credentials_path, "r") as f:
    TOKENS = json.load(f)
openai_client = OpenAI(api_key=TOKENS["open-ai"]["api-key"])


def generate_image(prompt: str) -> str:
    """Generate an image with DALL-E 3 and returns the image url.

    Args:
        prompt (str): The image description.

    Returns:
        str: The image url.
    """

    try:
        response = openai_client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="hd",
            response_format="url",
            user=TOKENS["open-ai"].get("user-id", None),
        )
        return response.data[0].url
    except Exception as e:
        return f"Couldn't load the image: '{e}'"
