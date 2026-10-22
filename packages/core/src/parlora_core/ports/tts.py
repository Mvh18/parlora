"""Text-to-speech port (provisional until Phase 1)."""

from typing import Protocol

from parlora_core.languages import LanguageCode


class TextToSpeech(Protocol):
    """Speaks the tutor's replies."""

    async def synthesize(self, text: str, *, language: LanguageCode) -> bytes:
        """Return audio for `text`, spoken in `language`."""
