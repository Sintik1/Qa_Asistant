"""The local launcher builds commands and does not start servers in tests."""

from __future__ import annotations

import os
from pathlib import Path

import run


def test_flask_command_binds_local_port():
    cmd = run.flask_command(Path("/usr/bin/python3"))
    assert cmd[:6] == ["/usr/bin/python3", "-m", "flask", "--app", "wsgi", "run"]
    assert cmd[cmd.index("--port") + 1] == "5001"
    assert "--no-reload" in cmd
    assert "127.0.0.1" in cmd


def test_npm_command_starts_vite(monkeypatch):
    monkeypatch.setattr(run.shutil, "which", lambda name: "/usr/bin/npm" if name == "npm" else None)
    cmd = run.npm_command()
    assert "dev" in cmd
    assert "5173" in cmd


def test_venv_python_missing(tmp_path: Path):
    assert run.venv_python(tmp_path) is None


def test_venv_python_found(tmp_path: Path):
    if os.name == "nt":
        bin_dir = tmp_path / ".venv" / "Scripts"
        name = "python.exe"
    else:
        bin_dir = tmp_path / ".venv" / "bin"
        name = "python"
    bin_dir.mkdir(parents=True)
    python = bin_dir / name
    python.write_text("", encoding="utf-8")
    assert run.venv_python(tmp_path) == python
