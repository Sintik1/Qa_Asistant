"""Start Flask and the Vite UI together.

Usage from the repository root (after the venv and npm install):

    python run.py
"""

from __future__ import annotations

import os
import shutil
import signal
import subprocess
import sys
import threading
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FLASK_PORT = "5001"
VITE_PORT = "5173"


def venv_python(root: Path) -> Path | None:
    """Return the project virtualenv interpreter, if it has been created."""
    if os.name == "nt":
        candidate = root / ".venv" / "Scripts" / "python.exe"
    else:
        candidate = root / ".venv" / "bin" / "python"
    return candidate if candidate.is_file() else None


def flask_command(python: Path) -> list[str]:
    return [
        str(python),
        "-m",
        "flask",
        "--app",
        "wsgi",
        "run",
        "--host",
        "127.0.0.1",
        "--port",
        FLASK_PORT,
        "--no-reload",
    ]


def npm_command() -> list[str]:
    npm = shutil.which("npm")
    if not npm:
        raise SystemExit("npm не найден. Установите Node.js 20+ и повторите запуск.")
    args = ["run", "dev", "--", "--host", "127.0.0.1", "--port", VITE_PORT]
    if os.name == "nt":
        return ["cmd", "/c", npm, *args]
    return [npm, *args]


def _pipe(prefix: str, stream) -> None:
    try:
        for line in stream:
            print(f"[{prefix}] {line}", end="", flush=True)
    finally:
        stream.close()


def _spawn(argv: list[str], *, cwd: Path) -> subprocess.Popen[str]:
    kwargs: dict = {
        "cwd": cwd,
        "stdout": subprocess.PIPE,
        "stderr": subprocess.STDOUT,
        "text": True,
        "bufsize": 1,
    }
    if os.name != "nt":
        kwargs["start_new_session"] = True
    return subprocess.Popen(argv, **kwargs)


def _stop(proc: subprocess.Popen[str]) -> None:
    if proc.poll() is not None:
        return
    if os.name == "nt":
        proc.terminate()
    else:
        os.killpg(proc.pid, signal.SIGTERM)
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        if os.name == "nt":
            proc.kill()
        else:
            os.killpg(proc.pid, signal.SIGKILL)
        proc.wait(timeout=5)


def _ensure_ready(root: Path) -> Path:
    python = venv_python(root)
    if python is None:
        raise SystemExit(
            "Нет .venv. Из корня репозитория:\n"
            "  python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
        )
    if Path(sys.executable).resolve() != python.resolve():
        os.execv(str(python), [str(python), str(Path(__file__).resolve()), *sys.argv[1:]])
    if not (root / "qa-assistant" / "node_modules").is_dir():
        raise SystemExit("Нет зависимостей UI. Один раз: cd qa-assistant && npm install")
    if not (root / ".env").is_file():
        print("Нет .env. Скопируйте .env.example и заполните ключи, иначе вход и Leopold не заработают.")
    return python


def main() -> int:
    python = _ensure_ready(ROOT)
    frontend = ROOT / "qa-assistant"
    print(f"Flask  http://127.0.0.1:{FLASK_PORT}")
    print(f"UI     http://127.0.0.1:{VITE_PORT}")
    print("Остановка: Ctrl+C")

    flask = _spawn(flask_command(python), cwd=ROOT)
    vite = _spawn(npm_command(), cwd=frontend)
    procs = [("flask", flask), ("ui", vite)]
    for name, proc in procs:
        assert proc.stdout is not None
        threading.Thread(target=_pipe, args=(name, proc.stdout), daemon=True).start()

    exit_code = 0
    try:
        while True:
            for name, proc in procs:
                code = proc.poll()
                if code is not None:
                    print(f"{name} завершился с кодом {code}")
                    exit_code = code
                    return exit_code
            time.sleep(0.4)
    except KeyboardInterrupt:
        print("\nОстанавливаю Flask и UI...")
        exit_code = 0
    finally:
        for _, proc in procs:
            _stop(proc)
    return exit_code


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        raise SystemExit(0)
