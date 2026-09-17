from openai import OpenAI

from backend.app.core.config import settings
from backend.app.llm.base import LLMProvider


class OpenAIProvider(LLMProvider):


    def __init__(self):

        self.client = OpenAI(
            api_key=settings.OPENAI_API_KEY
        )


    def generate(
        self,
        prompt: str,
    ) -> str:

        response = (
            self.client.responses.create(
                model=settings.OPENAI_MODEL,
                input=prompt,
            )
        )

        return response.output_text
