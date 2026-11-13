"""Read API keys from the environment or the local, git-ignored `env.secrets` file.

Values are never printed or logged. `env.secrets` holds `NAME=value` lines.
"""

from __future__ import annotations

import os
import re

from shockamp import ROOT

SECRETS_FILE = ROOT / "env.secrets"
_LINE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*['\"]?(.*?)['\"]?\s*$")


def get_secret(name: str, required: bool = False) -> str | None:
    """Environment variable first, then `env.secrets`. Raises only if `required` and absent."""
    val = os.environ.get(name)
    if not val and SECRETS_FILE.exists():
        for line in SECRETS_FILE.read_text(encoding="utf-8").splitlines():
            if line.lstrip().startswith("#"):
                continue
            m = _LINE.match(line)
            if m and m.group(1) == name and m.group(2):
                val = m.group(2)
                break
    if required and not val:
        raise RuntimeError(f"{name} not set (environment or env.secrets)")
    return val
