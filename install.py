#!/usr/bin/env python3
"""Install the Caelestia -> OpenCode theme bridge.

Idempotent. It:
  1. symlinks the generator into ``~/.local/bin``;
  2. adds ``theme.postHook`` to ``~/.config/caelestia/cli.json`` so the theme is
     regenerated on every Caelestia scheme/wallpaper change;
  3. selects the ``caelestia`` theme in ``~/.config/opencode/cli.json``;
  4. generates the theme once.

Config files are only rewritten (and backed up) when they actually change.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
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


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError as exc:
        sys.exit(f"error: {path} is not valid JSON: {exc}")


def save_json(path: Path, data: dict) -> bool:
    """Write ``data`` to ``path`` only if it differs. Returns whether it wrote."""
    if load_json(path) == data:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        backup = path.with_name(path.name + f".bak-{int(time.time())}")
        shutil.copy2(path, backup)
        print(f"  backed up {path} -> {backup.name}")
    path.write_text(json.dumps(data, indent=2) + "\n")
    return True


def link_generator() -> None:
    BIN.mkdir(parents=True, exist_ok=True)
    GENERATOR.chmod(0o755)
    if LINK.is_symlink() and LINK.resolve() == GENERATOR:
        print(f"  {LINK} already linked")
        return
    if LINK.exists() or LINK.is_symlink():
        backup = LINK.with_name(LINK.name + f".bak-{int(time.time())}")
        shutil.move(str(LINK), str(backup))
        print(f"  backed up {LINK} -> {backup.name}")
    LINK.symlink_to(GENERATOR)
    print(f"  linked {LINK} -> {GENERATOR}")


def main() -> int:
    print("Installing Caelestia -> OpenCode theme bridge")

    link_generator()

    caelestia = load_json(CAELESTIA_CLI)
    caelestia.setdefault("theme", {})["postHook"] = str(LINK)
    if save_json(CAELESTIA_CLI, caelestia):
        print(f"  {CAELESTIA_CLI}: theme.postHook = {LINK}")
    else:
        print(f"  {CAELESTIA_CLI}: theme.postHook already set")

    opencode = load_json(OPENCODE_CLI)
    theme = opencode.setdefault("theme", {})
    theme.setdefault("mode", "system")
    theme["name"] = "caelestia"
    if save_json(OPENCODE_CLI, opencode):
        print(f"  {OPENCODE_CLI}: theme.name = caelestia")
    else:
        print(f"  {OPENCODE_CLI}: theme.name already set")

    print("Generating the theme")
    subprocess.run([str(LINK)], check=False)

    print("\nDone. Restart OpenCode once to pick up the new theme name,")
    print("afterwards every wallpaper/scheme change updates it live.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
