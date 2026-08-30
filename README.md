# hookpack

A zero-dependency git hooks manager. One Python file, stdlib only.

hookpack installs declarative hooks into a repository and never touches a hook
file it did not create: every file it manages carries a `# hookpack:managed`
marker, and any pre-existing hook without that marker is refused with a clear
error.

## Requirements

- Python 3.9+
- git (bash, curl recommended for the `secretscan` hook)

## Install

Copy `hookpack.py` somewhere on your PATH (or run it directly):

```sh
python3 hookpack.py --help
```

## Commands

| Command | Description |
| --- | --- |
| `hookpack add NAME` | Install a hook into the current repo |
| `hookpack remove NAME` | Remove an installed hook |
| `hookpack list` | List available and installed hooks |
| `hookpack doctor` | Verify managed hooks, print hook dir, check PATH |

Pass `--work-dir DIR` before the subcommand to target another repository:

```sh
hookpack --work-dir ~/code/myrepo add trimtrail
```

## Available hooks

- **`secretscan`** (pre-commit) — Runs the
  [secretgate](https://github.com/tianzhicdev/secretgate) scanner
  (`python3 secretgate.py scan .`). It uses a local `secretgate.py` at the
  repo root if present, otherwise downloads the pinned copy to
  `.git/hookpack/cache/`. If neither works (e.g. no network), it prints a
  notice and skips gracefully instead of blocking your commit.
- **`trimtrail`** (pre-commit) — Strips trailing whitespace from staged text
  files (binary files are detected via `grep -I` and skipped), then re-stages
  the fixed files.

## How it works

- Each installed hook lives as an executable bash script at
  `.git/hookpack/<name>.hook`.
- A single dispatcher is generated at `.git/hooks/<event>` (e.g.
  `.git/hooks/pre-commit`). It starts with a `#!/usr/bin/env bash` shebang
  and the `# hookpack:managed` marker line, and runs every managed hook for
  that event. Any hook exiting non-zero fails the commit (the last non-zero
  status wins).
- `hookpack add` refuses (exit 1) if `.git/hooks/<event>` already exists
  without the marker. Fix or move your existing hook first.
- `hookpack remove` deletes the hook file and regenerates dispatchers; a
  dispatcher with no remaining managed hooks is deleted too.
- Linked git worktrees are supported (the shared `git-dir` hooks directory is
  resolved via `git rev-parse --git-path hooks`).

## Exit codes

- `0` success
- `1` error (unknown hook, refusal to touch unmanaged file, doctor issues)

## Tests

```sh
python3 -m unittest -v test_hookpack
```

## License

MIT — see [LICENSE](LICENSE).
