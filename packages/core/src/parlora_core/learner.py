"""Opaque learner identity (design D7).

Parlora has no users table: whoever integrates the tutor owns identity and
maps its users to a `LearnerRef`, for example ``platform:user-42`` or a UUID.
"""

import re
from dataclasses import dataclass

from parlora_core.errors import InvalidLearnerRef

MAX_LENGTH = 128
_ALLOWED = re.compile(r"[A-Za-z0-9._:-]+")


@dataclass(frozen=True, slots=True)
class LearnerRef:
    """An opaque reference to a learner: 1-128 characters from ``[A-Za-z0-9._:-]``.

    Values containing ``@`` are rejected so emails never become identifiers.
    """

    value: str

    def __post_init__(self) -> None:
        if not isinstance(self.value, str):
            raise InvalidLearnerRef("a learner reference must be a string")
        if "@" in self.value:
            raise InvalidLearnerRef(
                "a learner reference must be opaque; do not use emails or other personal data"
            )
        if not 1 <= len(self.value) <= MAX_LENGTH:
            raise InvalidLearnerRef(f"a learner reference must be 1-{MAX_LENGTH} characters long")
        if not _ALLOWED.fullmatch(self.value):
            raise InvalidLearnerRef(
                "a learner reference may only contain letters, digits, '.', '_', ':' and '-'"
            )

    def __str__(self) -> str:
        return self.value
