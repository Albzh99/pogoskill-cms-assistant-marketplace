"""Locate plugin-version-independent, user-specific site profiles on either OS."""

import argparse
import os
from pathlib import Path


def profile_root(home=None, codex_home=None):
    raw = codex_home or os.environ.get("CODEX_HOME")
    base = Path(raw).expanduser() if raw else (Path(home) if home else Path.home()) / ".codex"
    if not base.is_absolute():
        raise ValueError("CODEX_HOME must be an absolute path")
    return base / "tenorshare-cms" / "site-profiles"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--create", action="store_true")
    args = parser.parse_args()
    root = profile_root()
    if args.create:
        root.mkdir(parents=True, exist_ok=True)
    print(root)


if __name__ == "__main__":
    main()
