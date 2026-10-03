"""AI-assisted analysis of application / Supabase log excerpts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from core.errors import AppError, ValidationError
from infrastructure.logging_setup import log_file_path


class AiGenerator(Protocol):
    def generate(self, system_prompt: str, user_content: str) -> str: ...


ANALYZE_SYSTEM_PROMPT = (
    "Ты Senior Backend / SRE. Проанализируй логи QA Assistant (Flask JSON logs "
    "и/или фрагменты Supabase Logs). Найди вероятные root cause, сгруппируй "
    "ошибки по кодам (401/403/422/500, INVALID_*, UNAUTHORIZED, FORBIDDEN и т.д.), "
    "укажи request_id если есть, предложи 3–5 конкретных шагов исправления. "
    "Отвечай кратко на русском, маркированными списками."
)


@dataclass(frozen=True)
class LogAnalysisResult:
    source: str
    lines_used: int
    analysis: str

    def to_dict(self) -> dict[str, object]:
        return {
            "source": self.source,
            "lines_used": self.lines_used,
            "analysis": self.analysis,
        }


def read_log_tail(path: Path | None = None, *, max_lines: int = 200) -> str:
    target = path or log_file_path()
    if not target.is_file():
        raise ValidationError(
            code="VALIDATION_ERROR",
            message=f"Log file not found: {target}",
        )
    if max_lines < 1 or max_lines > 2000:
        raise ValidationError(
            code="VALIDATION_ERROR",
            message="max_lines must be between 1 and 2000",
        )
    lines = target.read_text(encoding="utf-8", errors="replace").splitlines()
    tail = lines[-max_lines:]
    return "\n".join(tail)


def analyze_log_text(
    text: str,
    ai: AiGenerator | None,
    *,
    source: str = "inline",
) -> LogAnalysisResult:
    cleaned = text.strip()
    if not cleaned:
        raise ValidationError(code="VALIDATION_ERROR", message="log text is empty")
    if ai is None:
        raise AppError(code="MISSING_TOKEN", status_code=503)

    lines_used = len(cleaned.splitlines())
    # Cap payload size for local small models.
    if len(cleaned) > 40_000:
        cleaned = cleaned[-40_000:]
        source = f"{source}+truncated"

    analysis = ai.generate(
        ANALYZE_SYSTEM_PROMPT,
        f"Логи ({source}, ~{lines_used} строк):\n\n{cleaned}",
    ).strip()
    if not analysis:
        raise AppError(code="API_EMPTY", status_code=502)
    return LogAnalysisResult(source=source, lines_used=lines_used, analysis=analysis)


def analyze_log_file(
    ai: AiGenerator | None,
    *,
    max_lines: int = 200,
    path: Path | None = None,
) -> LogAnalysisResult:
    text = read_log_tail(path, max_lines=max_lines)
    return analyze_log_text(text, ai, source=str(path or log_file_path()))
