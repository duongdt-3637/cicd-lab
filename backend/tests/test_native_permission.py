"""Bắt sớm lỗi PermissionError như dự án thật (native/tesac bị commit với mode 100644)."""

import os
import shutil
import subprocess

import pytest

from api.common.native import NATIVE_HELLO_PATH


def test_native_hello_is_executable_on_disk():
    assert os.access(NATIVE_HELLO_PATH, os.X_OK), f"{NATIVE_HELLO_PATH} thiếu quyền chạy (chmod +x)"


def test_native_hello_mode_in_git_is_100755():
    if shutil.which("git") is None:
        pytest.skip("git not installed")
    result = subprocess.run(
        ["git", "ls-files", "-s", NATIVE_HELLO_PATH],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(NATIVE_HELLO_PATH),
    )
    if result.returncode != 0 or not result.stdout:
        pytest.skip("not a git checkout or file not tracked yet")
    mode = result.stdout.split()[0]
    assert mode == "100755", f"git mode của native/hello là {mode}, cần 100755 (git update-index --chmod=+x)"
