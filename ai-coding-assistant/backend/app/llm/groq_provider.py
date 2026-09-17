from groq import Groq

from app.core.config import settings
from app.llm.base import LLMProvider


class GroqProvider(LLMProvider):
    """
    LLM provider for open-weight models served through Groq.
    """

    def __init__(self):
        if not settings.GROQ_API_KEY:
            raise ValueError(
                "GROQ_API_KEY is not configured."
            )

        self.client = Groq(
            api_key=settings.GROQ_API_KEY
        )

    def generate(
        self,
        prompt: str,
    ) -> str:

        if not prompt or not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        response = self.client.chat.completions.create(
            model=settings.GROQ_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        return response.choices[0].message.content or ""