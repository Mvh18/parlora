import pytest
from hypothesis import given
from hypothesis import strategies as st

from parlora_core.cefr import CefrBand, CefrLevel
from parlora_core.errors import InvalidCefrLevel

pytestmark = pytest.mark.unit

ORDER = [CefrLevel.A1, CefrLevel.A2, CefrLevel.B1, CefrLevel.B2, CefrLevel.C1, CefrLevel.C2]


def test_levels_in_canonical_order() -> None:
    assert list(CefrLevel) == ORDER


@given(st.permutations(ORDER))
def test_sorting_yields_a1_to_c2(levels: list[CefrLevel]) -> None:
    assert sorted(levels) == ORDER


@given(st.sampled_from(ORDER), st.sampled_from(ORDER))
def test_total_ordering_follows_rank(a: CefrLevel, b: CefrLevel) -> None:
    i, j = ORDER.index(a), ORDER.index(b)
    assert (a < b) == (i < j)
    assert (a <= b) == (i <= j)
    assert (a > b) == (i > j)
    assert (a >= b) == (i >= j)
    assert (a == b) == (i == j)


def test_levels_do_not_compare_with_strings() -> None:
    with pytest.raises(TypeError):
        _ = CefrLevel.A1 < "B1"


@pytest.mark.parametrize(
    ("level", "band"),
    [
        (CefrLevel.A1, CefrBand.BASIC),
        (CefrLevel.A2, CefrBand.BASIC),
        (CefrLevel.B1, CefrBand.INDEPENDENT),
        (CefrLevel.B2, CefrBand.INDEPENDENT),
        (CefrLevel.C1, CefrBand.PROFICIENT),
        (CefrLevel.C2, CefrBand.PROFICIENT),
    ],
)
def test_bands(level: CefrLevel, band: CefrBand) -> None:
    assert level.band is band


def test_band_values() -> None:
    assert CefrLevel.B2.band == "independent"


@pytest.mark.parametrize("level", ORDER)
def test_only_a1_and_a2_are_beginners(level: CefrLevel) -> None:
    assert level.is_beginner == (level in {CefrLevel.A1, CefrLevel.A2})


def test_parse() -> None:
    assert CefrLevel.parse("b1") is CefrLevel.B1
    assert CefrLevel.parse("C2") is CefrLevel.C2


@pytest.mark.parametrize("raw", ["D1", "", "B", "B3", "a1 ", "basic"])
def test_parse_rejects_unknown_levels(raw: str) -> None:
    with pytest.raises(InvalidCefrLevel):
        CefrLevel.parse(raw)


def test_parse_rejects_non_strings() -> None:
    with pytest.raises(InvalidCefrLevel):
        CefrLevel.parse(1)  # type: ignore[arg-type]


@given(st.sampled_from(ORDER), st.lists(st.booleans(), min_size=2, max_size=2))
def test_parse_is_case_insensitive(level: CefrLevel, upper: list[bool]) -> None:
    raw = "".join(c.upper() if up else c.lower() for c, up in zip(level.value, upper, strict=True))
    assert CefrLevel.parse(raw) is level


@given(st.text(max_size=4))
def test_parse_accepts_only_level_names(raw: str) -> None:
    if raw.upper() in {level.value for level in ORDER} and raw.isascii():
        assert CefrLevel.parse(raw).value == raw.upper()
    else:
        with pytest.raises(InvalidCefrLevel):
            CefrLevel.parse(raw)
