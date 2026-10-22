import dataclasses
import re

import pytest
from hypothesis import given
from hypothesis import strategies as st

from parlora_core.errors import InvalidLearnerRef
from parlora_core.learner import LearnerRef

pytestmark = pytest.mark.unit

VALID = re.compile(r"[A-Za-z0-9._:-]{1,128}")


@pytest.mark.parametrize(
    "raw",
    [
        "platform:user-42",
        "7f3c2a9e-1b4d-4c8a-9e21-5d6f0a8b3c11",
        "a",
        "x" * 128,
        "hub.learner_7:A",
    ],
)
def test_valid_references(raw: str) -> None:
    assert LearnerRef(raw).value == raw
    assert str(LearnerRef(raw)) == raw


def test_email_rejected_as_personal_data() -> None:
    with pytest.raises(InvalidLearnerRef, match="personal data"):
        LearnerRef("ana@example.com")


@pytest.mark.parametrize("raw", ["", "x" * 129])
def test_length_bounds(raw: str) -> None:
    with pytest.raises(InvalidLearnerRef, match="1-128"):
        LearnerRef(raw)


@pytest.mark.parametrize("raw", ["user 42", "user/42", "usér", "user\n", "#1"])
def test_characters_outside_the_charset(raw: str) -> None:
    with pytest.raises(InvalidLearnerRef):
        LearnerRef(raw)


def test_non_string_rejected() -> None:
    with pytest.raises(InvalidLearnerRef):
        LearnerRef(42)  # type: ignore[arg-type]


def test_reference_is_immutable() -> None:
    ref = LearnerRef("platform:user-42")
    with pytest.raises(dataclasses.FrozenInstanceError):
        ref.value = "other"  # type: ignore[misc]
    assert ref.value == "platform:user-42"


@given(st.text(max_size=140) | st.from_regex(VALID, fullmatch=True))
def test_accepts_exactly_the_documented_charset_and_length(raw: str) -> None:
    if VALID.fullmatch(raw):
        assert LearnerRef(raw).value == raw
    else:
        with pytest.raises(InvalidLearnerRef):
            LearnerRef(raw)


@given(st.text(max_size=60), st.text(max_size=60))
def test_anything_with_an_at_sign_is_rejected(local: str, domain: str) -> None:
    with pytest.raises(InvalidLearnerRef):
        LearnerRef(f"{local}@{domain}")
