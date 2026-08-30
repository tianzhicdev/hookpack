"""Tests for hookpack.py — stdlib unittest + subprocess against temp git repos."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
HOOKPACK = HERE / "hookpack.py"


def run(args, cwd, check: int | None = 0):
    """Run hookpack (or any command) in cwd; return CompletedProcess.

    check=None disables the assertion so callers can pass an explicit
    check value through wrapper methods.
    """
    r = subprocess.run(
        args,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@e",
             "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@e"},
    )
    if check is not None:
        assert r.returncode == check, (
            f"cmd {args} rc={r.returncode}\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
        )
    return r


def hp(*args, cwd):
    return run(["python3", str(HOOKPACK), *args], cwd=cwd, check=None)


class HookpackTestCase(unittest.TestCase):
    def setUp(self):
        self.repo = Path(tempfile.mkdtemp(prefix="hookpack-test-"))
        self.addCleanup(shutil.rmtree, self.repo, True)
        run(["git", "init", "-q", "."], cwd=self.repo, check=0)
        run(["git", "config", "user.email", "t@e"], cwd=self.repo, check=0)
        run(["git", "config", "user.name", "t"], cwd=self.repo, check=0)

    def hp(self, *args, check=None):
        r = hp(*args, cwd=self.repo)
        if check is not None:
            self.assertEqual(
                r.returncode, check,
                msg=f"hookpack {args} rc={r.returncode}\n{r.stdout}\n{r.stderr}",
            )
        return r

    def git(self, *args, check: int | None = 0):
        return run(["git", *args], cwd=self.repo, check=check)

    @property
    def gitdir(self):
        return self.repo / ".git"

    @property
    def hooks(self):
        return self.gitdir / "hooks"


class TestAddAndDispatch(HookpackTestCase):
    def test_add_writes_hook_and_dispatcher(self):
        self.hp("add", "trimtrail", check=0)
        hk = self.gitdir / "hookpack" / "trimtrail.hook"
        disp = self.hooks / "pre-commit"
        self.assertTrue(hk.is_file())
        self.assertTrue(os.access(hk, os.X_OK))
        self.assertIn("# hookpack:managed", hk.read_text())
        self.assertTrue(disp.is_file())
        self.assertTrue(os.access(disp, os.X_OK))
        self.assertIn("# hookpack:managed", disp.read_text())

    def test_dispatcher_runs_installed_hook(self):
        # Install a managed pre-commit hook that stamps a file when it runs.
        hkdir = self.gitdir / "hookpack"
        hkdir.mkdir(parents=True)
        hk = hkdir / "marker.hook"
        hk.write_text(
            "#!/usr/bin/env bash\n# hookpack:managed\n"
            f"touch '{self.repo / 'hook-ran'}'\n"
        )
        hk.chmod(0o755)
        self.hp("add", "trimtrail", check=0)  # triggers dispatcher sync
        (self.repo / "f.txt").write_text("hello\n")
        self.git("add", "f.txt")
        self.git("commit", "-m", "x", check=0)
        self.assertTrue((self.repo / "hook-ran").exists(),
                        "dispatcher did not execute installed hook")

    def test_hook_failure_blocks_commit(self):
        hkdir = self.gitdir / "hookpack"
        hkdir.mkdir(parents=True)
        hk = hkdir / "failer.hook"
        hk.write_text("#!/usr/bin/env bash\n# hookpack:managed\nexit 3\n")
        hk.chmod(0o755)
        self.hp("add", "trimtrail", check=0)
        (self.repo / "f.txt").write_text("hello\n")
        self.git("add", "f.txt")
        r = self.git("commit", "-m", "x", check=None)
        self.assertNotEqual(r.returncode, 0)
        self.git("log", "--oneline", check=128)  # no commits exist

    def test_add_secretscan(self):
        self.hp("add", "secretscan", check=0)
        hk = (self.gitdir / "hookpack" / "secretscan.hook").read_text()
        self.assertIn("secretgate.py", hk)
        self.assertIn(
            "https://raw.githubusercontent.com/tianzhicdev/secretgate/main/secretgate.py",
            hk,
        )
        self.assertIn("hookpack/cache", hk)

    def test_add_unknown_hook_fails(self):
        r = self.hp("add", "nope", check=1)
        self.assertIn("unknown hook", r.stderr)


class TestRefusal(HookpackTestCase):
    def test_refuses_pre_existing_unmanaged_hook(self):
        pre = self.hooks / "pre-commit"
        pre.parent.mkdir(parents=True, exist_ok=True)
        pre.write_text("#!/bin/sh\necho mine\n")
        pre.chmod(0o755)
        r = self.hp("add", "trimtrail", check=1)
        self.assertIn("refusing", r.stderr)
        self.assertIn("hookpack:managed", r.stderr)
        # original untouched
        self.assertEqual(pre.read_text(), "#!/bin/sh\necho mine\n")
        self.assertFalse((self.gitdir / "hookpack" / "trimtrail.hook").exists())


class TestRemove(HookpackTestCase):
    def test_remove_deletes_hook_and_dispatcher(self):
        self.hp("add", "trimtrail", check=0)
        self.assertTrue((self.hooks / "pre-commit").exists())
        self.hp("remove", "trimtrail", check=0)
        self.assertFalse((self.gitdir / "hookpack" / "trimtrail.hook").exists())
        self.assertFalse((self.hooks / "pre-commit").exists(),
                         "dispatcher should be removed when no hooks remain")

    def test_remove_one_keeps_dispatcher_for_other(self):
        self.hp("add", "trimtrail", check=0)
        self.hp("add", "secretscan", check=0)
        self.hp("remove", "trimtrail", check=0)
        disp = (self.hooks / "pre-commit").read_text()
        self.assertIn("secretscan.hook", disp)
        self.assertNotIn("trimtrail", disp)

    def test_remove_not_installed(self):
        r = self.hp("remove", "trimtrail", check=1)
        self.assertIn("not installed", r.stderr)


class TestList(HookpackTestCase):
    def test_list_shows_available_and_state(self):
        r = self.hp("list", check=0)
        self.assertIn("secretscan", r.stdout)
        self.assertIn("trimtrail", r.stdout)
        self.assertIn("not installed", r.stdout)
        self.hp("add", "trimtrail", check=0)
        r2 = self.hp("list", check=0)
        # line for trimtrail now says installed
        line = [l for l in r2.stdout.splitlines() if "trimtrail" in l][0]
        self.assertIn("installed", line)
        self.assertNotIn("not installed", line)


class TestTrimtrailBehavior(HookpackTestCase):
    def test_strips_trailing_whitespace_in_staged_file(self):
        self.hp("add", "trimtrail", check=0)
        f = self.repo / "a.txt"
        f.write_bytes(b"line one   \nline two\t\nkeep\n")
        self.git("add", "a.txt")
        self.git("commit", "-m", "x", check=0)
        # worktree file was fixed and re-staged
        self.assertEqual(f.read_bytes(), b"line one\nline two\nkeep\n")
        # committed blob is clean too
        shown = subprocess.run(
            ["git", "show", "HEAD:a.txt"], cwd=str(self.repo),
            capture_output=True, text=True,
        )
        self.assertEqual(shown.returncode, 0, shown.stderr)
        self.assertEqual(shown.stdout, "line one\nline two\nkeep\n")
        # nothing left dirty
        status = self.git("status", "--porcelain")
        self.assertEqual(status.stdout.strip(), "")

    def test_leaves_clean_files_alone(self):
        self.hp("add", "trimtrail", check=0)
        f = self.repo / "b.txt"
        f.write_text("clean\n")
        mtime = f.stat().st_mtime_ns
        self.git("add", "b.txt")
        self.git("commit", "-m", "x", check=0)
        self.assertEqual(f.stat().st_mtime_ns, mtime)


class TestDoctor(HookpackTestCase):
    def test_doctor_healthy(self):
        self.hp("add", "trimtrail", check=0)
        r = self.hp("doctor", check=0)
        self.assertIn(str(self.hooks), r.stdout)
        self.assertIn("git:", r.stdout)
        self.assertIn("python3:", r.stdout)
        self.assertIn("pre-commit: OK", r.stdout)
        self.assertIn("all managed hooks healthy", r.stdout)

    def test_doctor_flags_broken_shebang(self):
        self.hp("add", "trimtrail", check=0)
        disp = self.hooks / "pre-commit"
        disp.write_text("# hookpack:managed\nno shebang\n")
        r = self.hp("doctor", check=1)
        self.assertIn("ERROR missing shebang", r.stdout)

    def test_doctor_outside_repo(self):
        d = Path(tempfile.mkdtemp(prefix="hookpack-norepo-"))
        self.addCleanup(shutil.rmtree, d, True)
        r = hp("--work-dir", str(d), "doctor", cwd=self.repo)
        self.assertEqual(r.returncode, 1)
        self.assertIn("not a git repository", r.stderr)


class TestWorkDirFlag(HookpackTestCase):
    def test_work_dir_from_elsewhere(self):
        d = Path(tempfile.mkdtemp(prefix="hookpack-cwd-"))
        self.addCleanup(shutil.rmtree, d, True)
        r = run(["python3", str(HOOKPACK), "--work-dir", str(self.repo),
                 "add", "trimtrail"], cwd=d)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.gitdir / "hookpack" / "trimtrail.hook").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
