from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class AgentResult:
    """Standard result wrapper for all agents."""
    success: bool
    data: dict | str | None = None
    error: str | None = None
    source: str = ""


class BaseAgent(ABC):
    """Base class for agents that interact with external services.

    Agents wrap a single external concern (an API, a website, a model).
    They own their own config, handle errors, and return AgentResult.
    """

    name: str = "base"

    @abstractmethod
    def run(self, *args, **kwargs) -> AgentResult:
        """Execute the agent's primary action. Must be implemented."""
        ...