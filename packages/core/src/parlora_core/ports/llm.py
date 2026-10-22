"""Language-model port (provisional until Phase 1)."""

from dataclasses import dataclass
from typing import Literal, Protocol

Role = Literal["system", "user", "assistant"]


@dataclass(frozen=True, slots=True)
class Message:
    """One turn of a conversation sent to the language model."""

    role: Role
    content: str


class LanguageModel(Protocol):
    """Produces the tutor's replies."""

    async def reply(self, messages: list[Message]) -> str:
        """Return the next assistant message for the conversation so far."""
