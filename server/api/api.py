from openai import OpenAI
import json
from os.path import dirname, abspath, join

with open(join(dirname(abspath(__file__)), "credentials.json"), "r") as f:
    KEYS = json.load(f)

openai_client = OpenAI(api_key=KEYS["open-ai"]["api-key"])

def generate_image(prompt: str) -> str:
    """Generate an image with DALL-E 3 and returns the image url.

    Args:
        prompt (str): Image description

    Returns:
        str: Image url
    """

    response = openai_client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024",
        quality="hd",
        response_format="url",
        user=KEYS["open-ai"]["user-id"],
    )

    return response.data[0].url
