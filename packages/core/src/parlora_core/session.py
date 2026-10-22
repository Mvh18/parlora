"""Session settings and the default feedback-language policy."""

from dataclasses import InitVar, dataclass

from parlora_core.cefr import CefrLevel
from parlora_core.errors import InvalidSessionSettings
from parlora_core.languages import LanguageCode, LanguageRegistry, default_registry
from parlora_core.learner import LearnerRef

MAX_TOPIC_LENGTH = 120


@dataclass(frozen=True, slots=True)
class SessionSettings:
    """What a conversation session practises, for whom and at which level.

    Languages are validated against `registry` (the default registry when
    omitted): the target must be a target language and the feedback language
    a feedback language. The topic is stored trimmed and must then be
    1-120 characters long.
    """

    learner_ref: LearnerRef
    target_language: LanguageCode
    feedback_language: LanguageCode
    level: CefrLevel
    topic: str
    registry: InitVar[LanguageRegistry | None] = None

    def __post_init__(self, registry: LanguageRegistry | None) -> None:
        languages = registry if registry is not None else default_registry()
        languages.require_target(self.target_language)
        languages.require_feedback(self.feedback_language)
        if not isinstance(self.topic, str):
            raise InvalidSessionSettings("the topic must be a string")
        topic = self.topic.strip()
        if not 1 <= len(topic) <= MAX_TOPIC_LENGTH:
            raise InvalidSessionSettings(
                f"the topic must be 1-{MAX_TOPIC_LENGTH} characters long after trimming"
            )
        object.__setattr__(self, "topic", topic)


def default_feedback_language(
    level: CefrLevel,
    native: LanguageCode,
    target: LanguageCode,
    registry: LanguageRegistry | None = None,
) -> LanguageCode:
    """Choose the language corrections are explained in when the learner has not.

    Beginners (A1-A2) get feedback in their native language when it is a
    supported feedback language; everyone else gets it in the target language.
    """
    languages = registry if registry is not None else default_registry()
    if level.is_beginner and native in languages and languages.get(native).as_feedback:
        return native
    return target
