"""The OpenAPI contract exactly as committed to `contracts/openapi.json` (design D8).

The committed file is the integration surface: the web client's types and any
integrator's client are generated from it, so the export and the drift test
share this one rendering.
"""

import json

from parlora_server.config import Settings
from parlora_server.main import create_app


def render_openapi() -> str:
    # Routes do not depend on configuration, so defaults render the same document.
    app = create_app(Settings(_env_file=None))
    return json.dumps(app.openapi(), indent=2, ensure_ascii=False) + "\n"
