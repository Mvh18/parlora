import dataclasses

import pytest

from parlora_core.cefr import CefrLevel
from parlora_core.errors import InvalidSessionSettings, UnsupportedLanguage
from parlora_core.languages import Language, LanguageCode, LanguageRegistry
from parlora_core.learner import LearnerRef
from parlora_core.session import MAX_TOPIC_LENGTH, SessionSettings, default_feedback_language

pytestmark = pytest.mark.unit

EN, ES, DE, FR = (LanguageCode(c) for c in ("en", "es", "de", "fr"))
LEARNER = LearnerRef("platform:user-42")


def settings(**overrides: object) -> SessionSettings:
    values: dict[str, object] = {
        "learner_ref": LEARNER,
        "target_language": EN,
        "feedback_language": ES,
        "level": CefrLevel.A2,
        "topic": "travel",
    }
    values.update(overrides)
    return SessionSettings(**values)  # type: ignore[arg-type]


# ── SessionSettings ─────────────────────────────────────────────────────────


def test_valid_settings() -> None:
    created = settings()
    assert created.learner_ref == LEARNER
    assert created.target_language == EN
    assert created.feedback_language == ES
    assert created.level is CefrLevel.A2
    assert created.topic == "travel"


def test_feedback_only_language_as_target() -> None:
    with pytest.raises(UnsupportedLanguage, match="target"):
        settings(target_language=ES)


def test_target_only_language_as_feedback() -> None:
    registry = LanguageRegistry(
        [
            Language(EN, "English", "English", as_target=True, as_feedback=True),
            Language(DE, "German", "Deutsch", as_target=True, as_feedback=False),
        ]
    )
    with pytest.raises(UnsupportedLanguage, match="feedback"):
        settings(feedback_language=DE, registry=registry)
    assert (
        settings(target_language=DE, feedback_language=EN, registry=registry).target_language == DE
    )


def test_unknown_language() -> None:
    with pytest.raises(UnsupportedLanguage):
        settings(feedback_language=FR)


@pytest.mark.parametrize("topic", ["", "   ", "\t\n"])
def test_blank_topic(topic: str) -> None:
    with pytest.raises(InvalidSessionSettings, match="topic"):
        settings(topic=topic)


def test_topic_is_trimmed() -> None:
    assert settings(topic="  travel  ").topic == "travel"


def test_topic_length_bounds() -> None:
    assert len(settings(topic="x" * MAX_TOPIC_LENGTH).topic) == MAX_TOPIC_LENGTH
    assert settings(topic=f" {'x' * MAX_TOPIC_LENGTH} ").topic == "x" * MAX_TOPIC_LENGTH
    with pytest.raises(InvalidSessionSettings, match="topic"):
        settings(topic="x" * (MAX_TOPIC_LENGTH + 1))


def test_non_string_topic() -> None:
    with pytest.raises(InvalidSessionSettings, match="topic"):
        settings(topic=None)


def test_settings_are_immutable() -> None:
    created = settings()
    with pytest.raises(dataclasses.FrozenInstanceError):
        created.topic = "food"  # type: ignore[misc]
    assert created.topic == "travel"


def test_registry_is_not_part_of_the_value() -> None:
    assert [f.name for f in dataclasses.fields(SessionSettings)] == [
        "learner_ref",
        "target_language",
        "feedback_language",
        "level",
        "topic",
    ]
    assert settings() == settings()


# ── default_feedback_language ───────────────────────────────────────────────


def test_beginner_spanish_speaker() -> None:
    assert default_feedback_language(CefrLevel.A2, native=ES, target=EN) == ES


def test_intermediate_learner() -> None:
    assert default_feedback_language(CefrLevel.B1, native=ES, target=EN) == EN


def test_unsupported_native_language() -> None:
    assert default_feedback_language(CefrLevel.A1, native=DE, target=EN) == EN


@pytest.mark.parametrize("level", [CefrLevel.B2, CefrLevel.C1, CefrLevel.C2])
def test_advanced_learners_get_target_language(level: CefrLevel) -> None:
    assert default_feedback_language(level, native=ES, target=EN) == EN


def test_native_known_but_not_a_feedback_language() -> None:
    registry = LanguageRegistry(
        [
            Language(EN, "English", "English", as_target=True, as_feedback=True),
            Language(DE, "German", "Deutsch", as_target=True, as_feedback=False),
        ]
    )
    assert default_feedback_language(CefrLevel.A1, native=DE, target=EN, registry=registry) == EN
