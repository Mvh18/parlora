"""CEFR proficiency levels (Common European Framework of Reference)."""

from enum import Enum, StrEnum
from functools import total_ordering
from typing import Self

from parlora_core.errors import InvalidCefrLevel


class CefrBand(StrEnum):
    """The three CEFR bands, each grouping two levels."""

    BASIC = "basic"
    INDEPENDENT = "independent"
    PROFICIENT = "proficient"


@total_ordering
class CefrLevel(Enum):
    """A CEFR level, ordered from A1 (lowest) to C2 (highest).

    Levels compare only with other levels, never with strings, so an ordering
    bug cannot hide behind lexicographic comparison.
    """

    A1 = "A1"
    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"

    @property
    def rank(self) -> int:
        return type(self)._member_names_.index(self.name)

    @property
    def band(self) -> CefrBand:
        return _BANDS[self.value[0]]

    @property
    def is_beginner(self) -> bool:
        """True for A1 and A2, where learners still need native-language support."""
        return self.band is CefrBand.BASIC

    @classmethod
    def parse(cls, raw: str) -> Self:
        """Parse a level name case-insensitively, e.g. ``"b1"`` → ``B1``."""
        if isinstance(raw, str) and raw.isascii() and raw.upper() in cls._member_names_:
            return cls[raw.upper()]
        raise InvalidCefrLevel(f"{raw!r} is not a CEFR level (A1, A2, B1, B2, C1, C2)")

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, CefrLevel):
            return NotImplemented
        return self.rank < other.rank


_BANDS = {"A": CefrBand.BASIC, "B": CefrBand.INDEPENDENT, "C": CefrBand.PROFICIENT}
