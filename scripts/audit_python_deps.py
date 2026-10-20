"""Python dependency gate (ADR 0005): known vulnerabilities and licence policy.

1. Export the locked dependency set and audit it with pip-audit.
2. Check the licences of the installed environment with pip-licenses: GPL and
   AGPL of any version are denied (ADR 0004), and so is a missing licence.

Run after `uv sync --locked --all-packages --all-groups` so the installed
environment matches the lockfile. Exits non-zero when either check fails.
"""

import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Substrings of denied licence names, matched against unnormalised metadata.
# "GPL" also matches LGPL, which is allowed only for the reviewed packages below.
DENIED_LICENCES = ["General Public License", "GPL", "UNKNOWN"]

# Reviewed exceptions (ADR 0004). Adding one needs a documented review and an
# entry in NOTICE.
REVIEWED_LGPL = ["soxr", "num2words"]


def run(cmd: list[str]) -> int:
    print("$", " ".join(cmd), flush=True)
    return subprocess.run(cmd, cwd=REPO_ROOT, check=False).returncode


def audit_vulnerabilities(requirements: Path) -> int:
    export = run(
        [
            "uv",
            "export",
            "--frozen",
            "--all-packages",
            "--all-groups",
            "--no-hashes",
            "--no-emit-workspace",
            "--quiet",
            "--output-file",
            str(requirements),
        ]
    )
    if export != 0:
        return export
    # --no-deps: the export already holds the full resolved set.
    return run(
        [
            sys.executable,
            "-m",
            "pip_audit",
            "--requirement",
            str(requirements),
            "--disable-pip",
            "--no-deps",
            "--progress-spinner",
            "off",
        ]
    )


def check_licences() -> int:
    return run(
        [
            sys.executable,
            "-m",
            "piplicenses",
            "--partial-match",
            f"--fail-on={';'.join(DENIED_LICENCES)}",
            "--ignore-packages",
            *REVIEWED_LGPL,
        ]
    )


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        vulnerabilities = audit_vulnerabilities(Path(tmp) / "requirements.txt")
    licences = check_licences()
    if vulnerabilities or licences:
        print("Python dependency gate failed (see ADR 0005).", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
