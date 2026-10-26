#!/usr/bin/env python3
"""Undo what install.py did.

Removes the ``theme.postHook`` from Caelestia, deletes the symlink and the
generated OpenCode theme, and points OpenCode back at its built-in ``opencode``
theme. Config files are backed up before being edited.
"""

from __future__ import annotations

import json
import os
import shutil
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent
GENERATOR = REPO / "caelestia-opencode-theme"
CONFIG = Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
BIN = Path(os.getenv("XDG_BIN_HOME", Path.home() / ".local" / "bin"))
LINK = BIN / "caelestia-opencode-theme"
CAELESTIA_CLI = CONFIG / "caelestia" / "cli.json"
OPENCODE_CLI = CONFIG / "opencode" / "cli.json"
THEME = CONFIG / "opencode" / "themes" / "caelestia.json"


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as exc:
        sys.exit(f"error: {path} is not valid JSON: {exc}")


def save_json(path: Path, data: dict) -> None:
    if not path.exists():
        return
    backup = path.with_name(path.name + f".bak-{int(time.time())}")
    shutil.copy2(path, backup)
    print(f"  backed up {path} -> {backup.name}")
    path.write_text(json.dumps(data, indent=2) + "\n")


def main() -> int:
    print("Uninstalling Caelestia -> OpenCode theme bridge")

    caelestia = load_json(CAELESTIA_CLI)
    hook = caelestia.get("theme", {}).get("postHook")
    if hook and str(LINK) in str(hook):
        del caelestia["theme"]["postHook"]
        if not caelestia["theme"]:
            del caelestia["theme"]
        save_json(CAELESTIA_CLI, caelestia)
        print(f"  {CAELESTIA_CLI}: removed theme.postHook")
    else:
        print(f"  {CAELESTIA_CLI}: nothing to remove")

    opencode = load_json(OPENCODE_CLI)
    if opencode.get("theme", {}).get("name") == "caelestia":
        opencode["theme"]["name"] = "opencode"
        save_json(OPENCODE_CLI, opencode)
        print(f"  {OPENCODE_CLI}: theme.name = opencode")

    if LINK.is_symlink() and LINK.resolve() == GENERATOR:
        LINK.unlink()
        print(f"  removed symlink {LINK}")

    if THEME.exists():
        THEME.unlink()
        print(f"  removed {THEME}")

    print("\nDone.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
