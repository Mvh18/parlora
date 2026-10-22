"""Ports the domain needs from the outside world, as `typing.Protocol`s.

PROVISIONAL: these shapes are placeholders until the voice loop of Phase 1
settles them; expect breaking changes. Adapters live in the server, never here.
"""

from parlora_core.ports.llm import LanguageModel, Message
from parlora_core.ports.sessions import SessionRepository
from parlora_core.ports.stt import SpeechToText
from parlora_core.ports.tts import TextToSpeech

__all__ = [
    "LanguageModel",
    "Message",
    "SessionRepository",
    "SpeechToText",
    "TextToSpeech",
]
