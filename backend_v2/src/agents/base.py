from pandas import api
from dataclasses import dataclass
import logging
from typing import Protocol
from pydantic import BaseModel
import anthropic

logger = logging.getLogger(__name__)
class BaseClient(Protocol):
    """Base class for clients that interact with LLMS"""
    api_key: str
    def call(self, prompt: str, **kwargs) -> str:
        """Make a call to the LLM with the given prompt and return the response text."""
        ...

class AnthropicClient:
    """Client for interacting with Anthropic's Claude models."""
    def __init__(self, api_key: str, model: str = "claude-2", temperature: float = 1.0):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.client = anthropic.Client(api_key=api_key)

    def call(self, prompt: str, **kwargs) -> str:
        response = self.client.completions.create(
            model=self.model,
            prompt=prompt,
            temperature=self.temperature,
            max_tokens=kwargs.get("max_tokens", 8192),
        )
        return response.completion


@dataclass
class AgentResult:
    """Standard result wrapper for all agents."""
    success: bool
    data: dict | str | None = None
    error: str | None = None
    source: str = ""


class BaseAgent(Protocol):
    """Base class for agents that interact with external services.

    Agents wrap a single external concern (an API, a website, a model).
    They own their own config, handle errors, and return AgentResult.
    """

    name: str = "base"

    def run(self, *args, **kwargs) -> AgentResult:
        """Execute the agent's primary action. Must be implemented."""
        ...