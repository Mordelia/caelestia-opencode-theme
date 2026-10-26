# caelestia-opencode-theme

A dynamic colour theme for [OpenCode](https://opencode.ai) driven by
[Caelestia](https://github.com/caelestia-dots)'s Material You scheme.

Change your wallpaper (or scheme, or light/dark mode) and OpenCode's TUI
recolours itself — no restart, no manual selection.

## How it works

1. Caelestia applies a colour scheme and runs the hook configured in
   `~/.config/caelestia/cli.json` under `theme.postHook`, exporting
   `SCHEME_COLOURS` / `SCHEME_MODE`.
2. `caelestia-opencode-theme` maps Caelestia's Material roles onto the eight hue
   families an OpenCode V2 theme expects, builds the complete `base` token tree,
   and writes `~/.config/opencode/themes/caelestia.json`.
3. It then sends **SIGUSR2** to running OpenCode TUIs. OpenCode's `Theme` store
   subscribes to SIGUSR2 and re-scans the `themes/` directories about a second
   later, applying the new tokens live.

The signal is only sent to processes whose `/proc/<pid>/status` shows SIGUSR2
caught. OpenCode's background service (`opencode serve --service`) does *not*
catch it — signalling it would terminate it — so it is skipped.

## Requirements

- Caelestia dotfiles (`caelestia-cli`).
- OpenCode V2 (`opencode`).
- Python 3.9+.

Tested with `caelestia-cli` 1.1.3 and OpenCode 2.1.3 on Arch.

## Install

```sh
make install          # or: python3 install.py
```

`install.py` is idempotent and will:

1. symlink `caelestia-opencode-theme` into `~/.local/bin`;
2. set `theme.postHook` in `~/.config/caelestia/cli.json`;
3. set `theme.name = "caelestia"` in `~/.config/opencode/cli.json`;
4. generate the theme once.

Existing config files are backed up next to themselves (`*.bak-<epoch>`).

Restart OpenCode once so it picks up the new theme *name*; after that every
wallpaper/scheme change updates it live.

### Manual install

```sh
install -Dm755 caelestia-opencode-theme ~/.local/bin/caelestia-opencode-theme
```

```jsonc
// ~/.config/caelestia/cli.json
{ "theme": { "postHook": "/home/<you>/.local/bin/caelestia-opencode-theme" } }
```

```jsonc
// ~/.config/opencode/cli.json
{ "theme": { "name": "caelestia", "mode": "system" } }
```

## Colour mapping

Caelestia role | OpenCode hue family
--- | ---
`primary` | `purple` (the `accent` alias)
`term4` | `blue` (the `interactive` alias)
`secondary` | `cyan`
`tertiary` | `orange`
`success` | `green`
`error` | `red`
`surface`, `onSurface`, `outline`, containers | `gray` / `neutral`

`gray` is anchored on the real Material surface/on-surface tones so the TUI
background matches the rest of the desktop exactly. The coloured families are
9-step ramps (100→900) generated from a single seed colour each.

## Customise

Edit `HUE_SOURCES`, `ACCENT` and `INTERACTIVE` in `caelestia-opencode-theme`, or
tweak the `BASE` token tree directly. Re-run `make generate`.

## Validate

```sh
make validate                       # checks examples/caelestia.json
python3 validate.py path/to/theme.json
```

The validator checks the `base` tree, the nine steps of each hue family, the
aliases, and that every `$` reference resolves to a concrete colour.

## Uninstall

```sh
make uninstall
```

Removes the hook, the symlink and the generated theme, and points OpenCode back
at its built-in `opencode` theme.

## Notes and caveats

- SIGUSR2 is an internal, undocumented OpenCode mechanism. It works today; it
  could change in a future release. The fallback is the TUI theme picker
  (`<leader>t`) or a restart.
- The generated file only carries the mode Caelestia is currently in (dark or
  light). OpenCode uses that mode when the other is requested.
- If no OpenCode TUI is running when the scheme changes, the theme is still
  written to disk for the next launch.

## Layout

```
caelestia-opencode-theme   generator (the thing Caelestia's hook runs)
install.py                 idempotent installer
uninstall.py               reverse of install.py
validate.py                theme validator
examples/caelestia.json    sample output
Makefile                   convenience targets
```
