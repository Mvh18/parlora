"""Export the server's OpenAPI document to contracts/openapi.json.

Usage: export_openapi.py [--check]

With --check nothing is written; the script exits non-zero and prints a diff
when the committed contract differs from the one the code generates.
"""

import argparse
import difflib
import sys
from pathlib import Path

from parlora_server.contract import render_openapi

CONTRACT = Path(__file__).resolve().parents[1] / "contracts" / "openapi.json"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="fail on drift instead of writing")
    args = parser.parse_args()

    generated = render_openapi()
    committed = CONTRACT.read_text(encoding="utf-8") if CONTRACT.is_file() else ""
    if args.check:
        if committed == generated:
            return 0
        diff = difflib.unified_diff(
            committed.splitlines(keepends=True),
            generated.splitlines(keepends=True),
            fromfile="contracts/openapi.json (committed)",
            tofile="contracts/openapi.json (generated)",
        )
        sys.stdout.writelines(diff)
        print("The contract is out of date: run `just openapi`.", file=sys.stderr)
        return 1

    CONTRACT.parent.mkdir(exist_ok=True)
    CONTRACT.write_text(generated, encoding="utf-8", newline="\n")
    print(f"wrote {CONTRACT.relative_to(CONTRACT.parents[1]).as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
