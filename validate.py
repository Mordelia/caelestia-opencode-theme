#!/usr/bin/env python3
"""Validate a generated OpenCode V2 theme.

Checks that the file has a ``base`` token tree plus at least one mode palette,
that every mode hue family defines the nine steps, and that every ``$``
reference resolves to a concrete colour. Exits non-zero on any problem.

Usage: python3 validate.py [path/to/theme.json]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

DEFAULT = Path.home() / ".config" / "opencode" / "themes" / "caelestia.json"

HUE_FAMILIES = ["gray", "red", "orange", "yellow", "green", "cyan", "blue", "purple"]
ALIASES = ["accent", "interactive", "neutral"]
STEPS = [str(n) for n in range(100, 1000, 100)]


def deep_merge(dst: dict, src: dict) -> dict:
    for key, value in src.items():
        if isinstance(value, dict) and isinstance(dst.get(key), dict):
            deep_merge(dst[key], value)
        else:
            dst[key] = value
    return dst


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    theme = json.loads(path.read_text())

    if "base" not in theme:
        errors.append("missing `base` token tree")
        return errors

    modes = [m for m in ("light", "dark") if m in theme]
    if not modes:
        errors.append("theme defines neither `light` nor `dark`")
        return errors

    for mode in modes:
        hues = theme[mode].get("hue")
        if not isinstance(hues, dict):
            errors.append(f"[{mode}] missing `hue` palette")
            continue
        for family in HUE_FAMILIES:
            if family not in hues:
                continue  # not every family is required by the base tree
            value = hues[family]
            if isinstance(value, str):
                continue  # alias to another hue
            missing = [s for s in STEPS if s not in value]
            if missing:
                errors.append(f"[{mode}] hue `{family}` missing steps: {', '.join(missing)}")
        for alias in ALIASES:
            if alias not in hues:
                errors.append(f"[{mode}] missing alias `{alias}`")

        merged = deep_merge(json.loads(json.dumps(theme["base"])), theme[mode])
        merged["hue"] = hues
        errors += _check_refs(merged, mode)

    return errors


def _check_refs(merged: dict, mode: str) -> list[str]:
    errors: list[str] = []

    def resolve_hue(name: str, step: str | None = None):
        value = merged["hue"][name]
        if isinstance(value, str) and value.startswith("$hue."):
            parts = value[5:].split(".")
            return resolve_hue(parts[0], parts[1] if len(parts) > 1 else step)
        return value[step] if step is not None else value

    def resolve(value: str, depth: int = 0):
        if depth > 25:
            raise ValueError("reference cycle")
        if value.startswith("$hue."):
            parts = value[5:].split(".")
            return resolve_hue(parts[0], parts[1] if len(parts) > 1 else None)
        if value.startswith("$"):
            current = merged
            for part in value[1:].split("."):
                if not isinstance(current, dict) or part not in current:
                    raise KeyError(value)
                current = current[part]
            return resolve(current, depth + 1)
        return value

    def walk(node, trail: list[str]) -> None:
        for key, value in node.items():
            if key == "hue":
                continue
            if isinstance(value, dict):
                walk(value, trail + [key])
            elif isinstance(value, list):
                continue
            else:
                try:
                    resolved = resolve(value)
                    if not isinstance(resolved, str) or not (resolved.startswith("#") or resolved == "transparent"):
                        errors.append(f"[{mode}] {'.'.join(trail + [key])} -> {value!r} resolved to {resolved!r}")
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"[{mode}] {'.'.join(trail + [key])} -> {value!r}: {exc}")

    walk(merged, [])
    return errors


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else DEFAULT
    if not path.exists():
        print(f"error: {path} does not exist", file=sys.stderr)
        return 2
    errors = validate(path)
    if errors:
        print(f"INVALID: {path}")
        for error in errors:
            print(f"  - {error}")
        return 1
    print(f"OK: {path} is a valid OpenCode V2 theme")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
