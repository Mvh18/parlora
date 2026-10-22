"""The language and CEFR catalogues are derived from the domain core."""

import pytest
from fastapi.testclient import TestClient

from parlora_core.cefr import CefrLevel
from parlora_core.languages import default_registry

pytestmark = pytest.mark.unit


def test_languages_list_the_registry_with_their_roles(client: TestClient) -> None:
    response = client.get("/api/v1/languages")

    assert response.status_code == 200
    assert response.json() == {
        "languages": [
            {
                "code": "en",
                "english_name": "English",
                "native_name": "English",
                "as_target": True,
                "as_feedback": True,
            },
            {
                "code": "es",
                "english_name": "Spanish",
                "native_name": "español",
                "as_target": False,
                "as_feedback": True,
            },
        ]
    }


def test_languages_follow_the_core_registry(client: TestClient) -> None:
    codes = [language["code"] for language in client.get("/api/v1/languages").json()["languages"]]

    assert codes == [str(language.code) for language in default_registry()]


def test_cefr_levels_in_order_with_band_and_beginner_flag(client: TestClient) -> None:
    response = client.get("/api/v1/cefr-levels")

    assert response.status_code == 200
    levels = response.json()["levels"]
    assert [level["code"] for level in levels] == [level.value for level in CefrLevel]
    assert levels[0] == {"code": "A1", "band": "basic", "is_beginner": True}
    assert levels[1] == {"code": "A2", "band": "basic", "is_beginner": True}
    assert levels[2] == {"code": "B1", "band": "independent", "is_beginner": False}
    assert levels[5] == {"code": "C2", "band": "proficient", "is_beginner": False}
