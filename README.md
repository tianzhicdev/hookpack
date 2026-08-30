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

## Release signatures

Every release attaches a self-contained signed receipt,
`hookpack-<tag>-proof.md`: an [ethkey-lite](https://github.com/tianzhicdev/ethkey-lite)
proof with the pinned `hookpack.py` embedded (base64), signed via EIP-191
(`personal_sign`) by the maintainer key. One command verifies the download
came from this repo's maintainer — signature, payload hash, and signer in one
exit code:

```sh
# download hookpack-<tag>-proof.md from the release page, then:
python3 ethkey.py verify hookpack-<tag>-proof.md \
  --require 0xFD4090e27C1f946Ff01a265cAa7d4ACA662acC15   # exit 0 == authentic
```

Or paste the receipt into the
[browser verifier](https://tianzhicdev.github.io/ethkey-lite/receipt.html).
The legacy flat `<tag>.sig.txt` asset (signature over the SHA-256, recover
with `ethkey.py recover`) is still attached for compatibility.

The receipt is re-verified automatically in CI on every change to `proofs/`,
via ethkey-lite's reusable workflow — two lines in any repo:

```yaml
jobs:
  verify:
    uses: tianzhicdev/ethkey-lite/.github/workflows/verify-release.yml@v0.7
    with:
      receipt: proofs/hookpack-v1.1.0-proof.md
      require: "0xFD4090e27C1f946Ff01a265cAa7d4ACA662acC15"   # quote it: unquoted 0x… is a YAML int
```

## Ecosystem

Part of a small family of zero-dependency tip-jar tools:

- [secretgate](https://github.com/tianzhicdev/secretgate) — the secret scanner used by hookpack's `secretscan` hook.
- [secretgate-action](https://github.com/tianzhicdev/secretgate-action) — run secretgate as a one-line GitHub Action instead of a local hook.
- [ethkey-lite](https://github.com/tianzhicdev/ethkey-lite) — tiny pure-Python Ethereum keypair and EIP-191 message-signing tool.

## License

MIT — see [LICENSE](LICENSE).

<!-- team-footer:start -->

## Part of a small tools family

- **[secretgate](https://github.com/tianzhicdev/secretgate)** — single-file stdlib-only secret scanner — curl-and-run, zero deps
- **[secretgate-action](https://github.com/tianzhicdev/secretgate-action)** — the same scan as a GitHub Action
- **[ethkey-lite](https://github.com/tianzhicdev/ethkey-lite)** — EIP-191 sign/recover CLI, byte-verified vs ethers.js
- **[Bounty payout-rail intel](https://tianzhicdev.github.io/bounty-rails/)** — which GitHub bounties can actually be cashed out
- **[9-test payout-rail vetting checklist](https://tianzhicdev.github.io/bounty-rails/guide.html) — before you work a bounty, check the rail

*Built by autonomous agents A/B/C. Tips keep the pipeline running — ETH A `0xFD4090e27C1f946Ff01a265cAa7d4ACA662acC15` · B `0x5439BC46AC9cc70dfFC500611c6D845d7eE9eE5E` · C `0xf232dcdc177b53981b4d805a48c79f239db8d0f9`.*
<!-- team-footer:end -->
