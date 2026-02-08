from dataclasses import dataclass
import logging
from typing import Protocol
import anthropic
from pydantic import BaseModel


logger = logging.getLogger(__name__)   

@dataclass
class MessageOptions:
    """Options for formatting messages to the LLM."""
    max_tokens:int = 1000


@dataclass
class MessageResponse:
    """Structured response from the LLM."""
    text: str
    input_tokens: int
    output_tokens:int
    metadata: dict | None = None

class BaseClient(Protocol):
    """Base class for clients that interact with LLMS"""
    api_key: str
    def call(self, prompt: str, options: MessageOptions=MessageOptions(), **kwargs) -> MessageResponse:
        """Make a call to the LLM with the given prompt and return the response text."""
        ...
    def call_json(self, prompt:str, json_model:BaseModel, options: MessageOptions=MessageOptions(), **kwargs) -> MessageResponse:
        """Make a call to the LLM with given prompt and json serializable model, return as valid json."""
        ...

class AnthropicClient:
    """Client for interacting with Anthropic's Claude models."""
    def __init__(self, api_key: str, model: str = "claude-sonnet-4-5", temperature: float = 1.0):
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.client = anthropic.Client(api_key=api_key)

    def call(self, prompt: str, options: MessageOptions = MessageOptions(), **kwargs) -> MessageResponse:
        message = {
            "role": "user",
            "content": prompt
        }
        response = self.client.messages.create(
            model=self.model,
            temperature=self.temperature,
            max_tokens=options.max_tokens,
            messages=[message],
            **kwargs
        )
        message = MessageResponse(
            text=response.content[0].text,
            metadata=None,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens
        )
        return message
    def call_json(self, prompt:str, json_model:BaseModel, options: MessageOptions = MessageOptions(), **kwargs) -> MessageResponse:
        message = {
            "role": "user",
            "content": prompt
        }
        response = self.client.messages.create(
            model = self.model,
            temperature=self.temperature,
            max_tokens=options.max_tokens,
            messages=[message],
            output_config={
                "format": {
                    "type": "json_schema",
                    "schema": anthropic.transform_schema(json_model)
                }
            }
        )
        message = MessageResponse(
            text=response.content[0].text,
            metadata=None,
            input_tokens=response.usage.input_tokens,
            output_tokens=response.usage.output_tokens
        )
        return message