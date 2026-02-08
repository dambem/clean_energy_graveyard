import google.generativeai as genai
from pathlib import Path
from .base import BaseAgent, AgentResult
from schemas import NimbyScore


class GeminiAgent(BaseAgent):
    """Agent that sends content to Google Gemini for NIMBY analysis."""

    name = "gemini"

    def __init__(self, api_key: str, model: str = "gemini-2.0-flash", temperature: float = 1.0):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model,
            generation_config={
                "temperature": temperature,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 8192,
                "response_mime_type": "application/json",
            },
        )
        self._prompt: str | None = None

    def load_prompt(self, path: Path) -> None:
        self._prompt = path.read_text()

    def run(self, content: str) -> AgentResult:
        if not self._prompt:
            return self._fail("No system prompt loaded. Call load_prompt() first.")
        try:
            chat = self.model.start_chat(
                history=[{"role": "user", "parts": [self._prompt]}]
            )
            response = chat.send_message(content)
            score = NimbyScore.model_validate_json(response.text)
            return self._ok(score.model_dump())
        except Exception as e:
            return self._fail(f"Gemini processing failed: {e}")
