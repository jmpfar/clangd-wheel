import os
import sys
import tempfile
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def ensure_clangd_from_wheel(monkeypatch):
    """test the installed clangd package, not the local one"""
    this_dir = Path(__file__).resolve().absolute().parent
    for pd in (this_dir, this_dir / ".."):
        try:
            new_path = sys.path.remove(pd)
            monkeypatch.setattr(sys, "path", new_path)
        except ValueError:
            pass
    monkeypatch.delitem(sys.modules, "clangd", raising=False)


def test_executable_file(capsys):
    import clangd

    clangd._get_executable.cache_clear()
    exe = clangd._get_executable("clangd")
    assert os.path.exists(exe)
    assert os.access(exe, os.X_OK)
    assert capsys.readouterr().out == ""

