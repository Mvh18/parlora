import dataclasses
import re

import pytest
from hypothesis import given
from hypothesis import strategies as st

from parlora_core.errors import DuplicateLanguage, InvalidLanguageCode, UnsupportedLanguage
from parlora_core.languages import Language, LanguageCode, LanguageRegistry, default_registry

pytestmark = pytest.mark.unit

ENGLISH = Language(LanguageCode("en"), "English", "English", as_target=True, as_feedback=True)
SPANISH = Language(LanguageCode("es"), "Spanish", "español", as_target=False, as_feedback=True)


# ── LanguageCode ────────────────────────────────────────────────────────────


def test_valid_code() -> None:
    code = LanguageCode("en")
    assert code.value == "en"
    assert str(code) == "en"


@pytest.mark.parametrize("raw", ["EN", "eng", "e", "", "en-US", "e1", " en"])
def test_invalid_codes(raw: str) -> None:
    with pytest.raises(InvalidLanguageCode):
        LanguageCode(raw)


def test_non_string_code_is_rejected() -> None:
    with pytest.raises(InvalidLanguageCode):
        LanguageCode(42)  # type: ignore[arg-type]


@given(st.text(max_size=4) | st.from_regex(r"[a-z]{2}", fullmatch=True))
def test_code_accepts_exactly_two_lowercase_ascii_letters(raw: str) -> None:
    if re.fullmatch(r"[a-z]{2}", raw):
        assert LanguageCode(raw).value == raw
    else:
        with pytest.raises(InvalidLanguageCode):
            LanguageCode(raw)


def test_codes_compare_by_value() -> None:
    assert LanguageCode("en") == LanguageCode("en")
    assert len({LanguageCode("en"), LanguageCode("en")}) == 1


# ── Language ────────────────────────────────────────────────────────────────


def test_language_is_immutable() -> None:
    with pytest.raises(dataclasses.FrozenInstanceError):
        ENGLISH.as_target = False  # type: ignore[misc]
    assert ENGLISH.as_target is True


# ── LanguageRegistry ────────────────────────────────────────────────────────


def test_default_registry_targets_only_english() -> None:
    assert [lang.code.value for lang in default_registry().targets()] == ["en"]


def test_default_registry_feedback_languages() -> None:
    assert [lang.code.value for lang in default_registry().feedback_languages()] == ["en", "es"]


def test_lookup_by_code_or_string() -> None:
    registry = default_registry()
    assert registry.get("es") == registry.get(LanguageCode("es"))
    assert registry.get("es").native_name == "español"


def test_unknown_language_lookup() -> None:
    with pytest.raises(UnsupportedLanguage, match="fr"):
        default_registry().get("fr")


def test_membership() -> None:
    registry = default_registry()
    assert "en" in registry
    assert LanguageCode("es") in registry
    assert "fr" not in registry
    assert "EN" not in registry
    assert 42 not in registry


def test_duplicate_registration() -> None:
    with pytest.raises(DuplicateLanguage, match="en") as excinfo:
        LanguageRegistry([ENGLISH, SPANISH, ENGLISH])
    assert isinstance(excinfo.value, ValueError)


def test_registry_keeps_registration_order() -> None:
    registry = LanguageRegistry([SPANISH, ENGLISH])
    assert list(registry) == [SPANISH, ENGLISH]
    assert len(registry) == 2


def test_require_target_rejects_feedback_only_language() -> None:
    registry = default_registry()
    assert registry.require_target("en") == ENGLISH
    with pytest.raises(UnsupportedLanguage, match="target"):
        registry.require_target("es")


def test_require_feedback() -> None:
    registry = LanguageRegistry(
        [Language(LanguageCode("de"), "German", "Deutsch", as_target=True, as_feedback=False)]
    )
    with pytest.raises(UnsupportedLanguage, match="feedback"):
        registry.require_feedback("de")
    assert default_registry().require_feedback("es") == SPANISH


def test_role_checks_raise_for_unknown_language() -> None:
    with pytest.raises(UnsupportedLanguage):
        default_registry().require_target("fr")
