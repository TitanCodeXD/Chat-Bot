import os

from dotenv import load_dotenv
from google import genai

load_dotenv()

API_KEY = os.getenv("API_KEY")

if not API_KEY:
    raise RuntimeError(
        "A variável API_KEY não foi encontrada. Verifique o arquivo .env."
    )

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.6-flash"
