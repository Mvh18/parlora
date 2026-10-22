"""Languages as a first-class concept (design D6).

A language plays one or both of two roles: a *target* language is the one a
learner practises; a *feedback* language is the one corrections are explained
in. Adding a language is a registry entry plus content (prompts, UI messages,
voice), not a refactor. The UI locale is a separate concept owned by clients.
"""

import re
from collections.abc import Iterable, Iterator
from dataclasses import dataclass

from parlora_core.errors import DuplicateLanguage, InvalidLanguageCode, UnsupportedLanguage

_ISO_639_1 = re.compile(r"[a-z]{2}")


@dataclass(frozen=True, slots=True)
class LanguageCode:
    """A two-letter lowercase ISO 639-1 code such as ``en``.

    Region subtags (``en-US``) are out of scope: accent and voice are a speech
    synthesis concern, not part of a language's identity.
    """

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str) or not _ISO_639_1.fullmatch(self.value):
            raise InvalidLanguageCode(
                f"{self.value!r} is not a two-letter lowercase ISO 639-1 code"
            )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class Language:
    """A language and the roles it may play in a session."""

    code: LanguageCode
    english_name: str
    native_name: str
    as_target: bool
    as_feedback: bool


class LanguageRegistry:
    """Immutable lookup of the languages Parlora supports, in registration order."""

    __slots__ = ("_by_code",)

    def __init__(self, languages: Iterable[Language]) -> None:
        by_code: dict[LanguageCode, Language] = {}
        for language in languages:
            if language.code in by_code:
                raise DuplicateLanguage(f"language {language.code} is registered twice")
            by_code[language.code] = language
        self._by_code = by_code

    def get(self, code: LanguageCode | str) -> Language:
        """Return the language for `code`, or raise `UnsupportedLanguage`."""
        key = _as_code(code)
        try:
            return self._by_code[key]
        except KeyError:
            raise UnsupportedLanguage(f"language {key} is not supported") from None

    def require_target(self, code: LanguageCode | str) -> Language:
        """Return the language for `code` if it can be practised."""
        language = self.get(code)
        if not language.as_target:
            raise UnsupportedLanguage(f"language {language.code} is not supported as a target")
        return language

    def require_feedback(self, code: LanguageCode | str) -> Language:
        """Return the language for `code` if feedback can be given in it."""
        language = self.get(code)
        if not language.as_feedback:
            raise UnsupportedLanguage(
                f"language {language.code} is not supported as a feedback language"
            )
        return language

    def targets(self) -> tuple[Language, ...]:
        return tuple(lang for lang in self._by_code.values() if lang.as_target)

    def feedback_languages(self) -> tuple[Language, ...]:
        return tuple(lang for lang in self._by_code.values() if lang.as_feedback)

    def __contains__(self, code: object) -> bool:
        if not isinstance(code, LanguageCode | str):
            return False
        try:
            return _as_code(code) in self._by_code
        except InvalidLanguageCode:
            return False

    def __iter__(self) -> Iterator[Language]:
        return iter(self._by_code.values())

    def __len__(self) -> int:
        return len(self._by_code)


def default_registry() -> LanguageRegistry:
    """English as target and feedback language; Spanish as feedback language."""
    return LanguageRegistry(
        [
            Language(LanguageCode("en"), "English", "English", as_target=True, as_feedback=True),
            Language(LanguageCode("es"), "Spanish", "español", as_target=False, as_feedback=True),
        ]
    )


def _as_code(code: LanguageCode | str) -> LanguageCode:
    return code if isinstance(code, LanguageCode) else LanguageCode(code)
