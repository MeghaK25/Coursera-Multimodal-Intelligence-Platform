import os
from dotenv import load_dotenv

from google import genai
from google.genai import types

load_dotenv()

MODEL_NAME = "gemini-3.6-flash"


class GeminiModel:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY environment variable is not set."
            )

        self.client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(
                retry_options=types.HttpRetryOptions(
                    attempts=1,
                    http_status_codes=[429, 500, 502, 503, 504]
                )
            )
        )

    def generate(self, prompt: str) -> str:
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        try:
            interaction = self.client.interactions.create(
                model=MODEL_NAME,
                input=prompt
            )

            if not interaction.output_text:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return interaction.output_text

        except Exception as exc:
            error_message = str(exc).lower()

            if (
                "429" in error_message
                or "too many requests" in error_message
                or "quota" in error_message
                or "resource exhausted" in error_message
            ):
                raise RuntimeError(
                    "Gemini API rate limit or quota was reached. "
                    "Please check the Gemini API usage and quota."
                ) from exc

            if (
                "503" in error_message
                or "service unavailable" in error_message
            ):
                raise RuntimeError(
                    f"Gemini API returned HTTP 429. "
                    f"Full error: {exc}"
                ) from exc

            raise RuntimeError(
                f"LLM generation failed: {exc}"
            ) from exc