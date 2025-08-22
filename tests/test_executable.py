import logging
import os
import re
import shutil
import subprocess
import sys

import clangd

logger = logging.getLogger(__name__)


def test_executable_file_exists():
    exe = clangd._get_executable("clangd")
    assert os.path.exists(exe)
    assert os.access(exe, os.X_OK)


def test_executable_run_clangd_version(monkeypatch, capsys):
    exe = clangd._get_executable("clangd")
    result = subprocess.run(
        [str(exe), "--version"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    # Output should contain a version string, e.g., 'clangd version ...'
    assert re.search(r"^clangd version ", result.stdout)
    assert result.stderr == "", "Expected no error output on --version"


def test_package_script_clangd_version():
    result = subprocess.run(["clangd", "--version"], capture_output=True, text=True)
    logger.info(f"clangd version output: {result.stdout}")

    assert result.returncode == 0
    assert re.search(r"^clangd version ", result.stdout)
    assert result.stderr == "", "Expected no error output on --version"


def test_selected_clangd_in_venv():
    venv_bin = os.path.dirname(sys.executable)
    clangd_path = shutil.which("clangd")

    assert clangd_path is not None, "clangd not found in PATH"
    assert os.path.commonpath([clangd_path, venv_bin]) == venv_bin, (
        f"clangd in PATH is not from venv: {clangd_path}"
    )
