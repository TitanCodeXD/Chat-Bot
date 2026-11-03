from google.genai import types

from config.gemini import client, MODEL_NAME


def process_audio(
    audio_bytes: bytes,
    mime_type: str,
    user_prompt: str
) -> str:
    """Sends audio bytes and a prompt to Gemini."""

    audio_part = types.Part.from_bytes(
        data=audio_bytes,
        mime_type=mime_type,
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[
            user_prompt,
            audio_part,
        ],
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text
