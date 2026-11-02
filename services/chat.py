from google.genai import types

from config.gemini import client, MODEL_NAME


def create_chat():
    """Creates a new Gemini conversation."""
    return client.chats.create(
        model=MODEL_NAME,
        config=types.GenerateContentConfig(
            temperature=0.7,
        ),
    )


def send_message(chat, message: str) -> str:
    """Sends a message and returns Gemini's response."""
    response = chat.send_message(message)

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")

    return response.text