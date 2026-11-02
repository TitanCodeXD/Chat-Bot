from PIL import Image

from config.gemini import client, MODEL_NAME


def analyze_image(prompt: str, image: Image.Image) -> str:
    """Sends an image and a prompt to Gemini and returns its response."""

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[prompt, image],
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text
