"""Speech-to-text port (provisional until Phase 1)."""

from typing import Protocol

from parlora_core.languages import LanguageCode


class SpeechToText(Protocol):
    """Transcribes a learner's speech."""

    async def transcribe(self, audio: bytes, *, language: LanguageCode) -> str:
        """Return the transcript of `audio`, spoken in `language`."""
