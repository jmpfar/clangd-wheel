import subprocess
import sys
from pathlib import Path
import functools
import os

from importlib.resources import files


@functools.cache
def _get_executable(name: str) -> Path:
    possibles = [
        Path(files("clangd") / f"data/bin/{name}{s}")
        for s in ("", ".exe", ".bin", ".dmg")
    ]
    for exe in possibles:
        if exe.exists():
            if os.environ.get("CLANGD_WHEEL_VERBOSE", None):
                print(f"Found binary: {exe} ")
            return exe

    raise FileNotFoundError(f"No executable found for {name} at\n{possibles}")


def _run(name, *args):
    command = [_get_executable(name)]
    if args:
        command += list(args)
    else:
        command += sys.argv[1:]
    return subprocess.call(command)


def clangd():
    raise SystemExit(_run("clangd"))
