import json
import subprocess
import sys

import pytest

from parlora_core import ports

pytestmark = pytest.mark.unit

PORTS = [ports.SpeechToText, ports.LanguageModel, ports.TextToSpeech, ports.SessionRepository]

# Lists the top-level modules that importing the ports adds to a fresh interpreter.
PROBE = """
import json, sys
before = set(sys.modules)
import parlora_core.ports
print(json.dumps(sorted({name.split(".")[0] for name in set(sys.modules) - before})))
"""


@pytest.mark.parametrize("port", PORTS)
def test_each_port_is_a_protocol(port: type) -> None:
    assert getattr(port, "_is_protocol", False), f"{port.__name__} is not a typing.Protocol"


def test_importing_the_ports_loads_no_third_party_module() -> None:
    result = subprocess.run(  # noqa: S603 — fixed arguments, current interpreter
        [sys.executable, "-c", PROBE], capture_output=True, text=True, check=True
    )
    loaded = set(json.loads(result.stdout))
    third_party = loaded - set(sys.stdlib_module_names) - {"parlora_core"}
    assert not third_party, f"ports import third-party modules: {sorted(third_party)}"


def test_message_is_a_value() -> None:
    assert ports.Message("user", "hello") == ports.Message("user", "hello")
