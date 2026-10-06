"""AI-assisted analysis of application / Supabase log excerpts."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from core.errors import AppError, ValidationError
from infrastructure.logging_setup import log_file_path


class AiGenerator(Protocol):
    def generate(self, system_prompt: str, user_content: str) -> str: ...


# --- Scenario prompts (CI/CD ДЗ шаг 7). Checked for role / JSON fields / actionable output. ---

SCENARIO_PROMPTS: dict[str, str] = {
    "general": (
        "Роль: Senior Backend/SRE для QA Assistant (Flask + Supabase + Ollama).\n"
        "Вход: JSON-lines логи (поля ts, level, logger, service, env, event, msg, "
        "request_id, method, path, status, error_code, duration_ms).\n"
        "Задача:\n"
        "1) Сгруппируй события по error_code и HTTP status.\n"
        "2) Для топ-3 проблем укажи: симптомы, вероятный root cause, 1–2 request_id-примера.\n"
        "3) Дай 3–5 конкретных шагов исправления (файл/env/проверка).\n"
        "4) Отметь ложные тревоги (шум health/OPTIONS), если есть.\n"
        "Формат: короткий русский markdown, списки. Не выдумывай данные вне логов. "
        "Не цитируй токены/пароли."
    ),
    "auth": (
        "Роль: Security-minded Backend.\n"
        "Фокус только на auth: UNAUTHORIZED, FORBIDDEN, oauth_*, 401/403, missing Bearer, "
        "JWT verify fail.\n"
        "По логам ответь:\n"
        "- Это FE (нет/просрочен JWT), Flask (SUPABASE_JWT_SECRET / Auth API), или OAuth provider?\n"
        "- Есть ли всплеск после /auth/callback или /api/auth/oauth/*?\n"
        "- Чеклист проверки: .env ключи, redirect URI, clock skew, CORS.\n"
        "Выход: таблица «симптом | гипотеза | проверка». Без общих фраз. "
        "Не цитируй токены."
    ),
    "cors": (
        "Роль: FullStack.\n"
        "Ищи CORS, preflight OPTIONS, «Failed to fetch», status 0, Origin mismatch.\n"
        "Скажи: какой Origin виден, какой CORS_ORIGINS нужен, затронуты ли только browser-запросы.\n"
        "Дай точную правку env (CORS_ORIGINS=...) и как проверить curl vs браузер."
    ),
    "ai": (
        "Роль: AI integration engineer.\n"
        "Фокус: API_UNAVAILABLE, API_EMPTY, API_429, API_503, MISSING_TOKEN, "
        "долгий duration_ms на /generate или /ai/ping.\n"
        "Раздели: Ollama не запущен / модель не скачана / timeout / пустой ответ / rate limit.\n"
        "Для каждой гипотезы — одна команда проверки (curl health, ollama tags, model в логе)."
    ),
    "persist": (
        "Роль: Data engineer.\n"
        "Фокус: persist=supabase, PostgREST 401/403/500, RLS, upload/documents/runs failures.\n"
        "Ответь: JWT user vs service_role, какая таблица/операция вероятнее, "
        "нужен ли SUPABASE_SERVICE_ROLE_KEY только на сервере.\n"
        "Шаги: проверить /api/health.checks.db, один SQL/Table Editor check, "
        "не светить service_role в FE."
    ),
}

DEFAULT_SCENARIO = "general"

# Secrets / JWT-looking blobs must not reach the model.
_REDACT_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?i)(bearer\s+)[a-z0-9\-._~+/]+=*", re.IGNORECASE),
    re.compile(r"eyJ[a-zA-Z0-9_-]{10,}\.[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+"),
    re.compile(r"(?i)(sb_secret_[a-z0-9]+)"),
    re.compile(r"(?i)(service_role[\"']?\s*[:=]\s*[\"']?)[a-z0-9._\-]+"),
    re.compile(r"(?i)(api[_-]?key[\"']?\s*[:=]\s*[\"']?)[a-z0-9._\-]+"),
)


def list_scenarios() -> list[str]:
    return sorted(SCENARIO_PROMPTS.keys())


def resolve_scenario(name: str | None) -> str:
    key = (name or DEFAULT_SCENARIO).strip().lower() or DEFAULT_SCENARIO
    if key not in SCENARIO_PROMPTS:
        raise ValidationError(
            code="VALIDATION_ERROR",
            message=f"Unknown scenario '{key}'. Use one of: {', '.join(list_scenarios())}",
        )
    return key


def redact_secrets(text: str) -> str:
    out = text
    out = _REDACT_PATTERNS[0].sub(r"\1[REDACTED]", out)
    out = _REDACT_PATTERNS[1].sub("[REDACTED_JWT]", out)
    out = _REDACT_PATTERNS[2].sub("[REDACTED_SB_SECRET]", out)
    out = _REDACT_PATTERNS[3].sub(r"\1[REDACTED]", out)
    out = _REDACT_PATTERNS[4].sub(r"\1[REDACTED]", out)
    return out


@dataclass(frozen=True)
class LogAnalysisResult:
    source: str
    lines_used: int
    analysis: str
    scenario: str = DEFAULT_SCENARIO

    def to_dict(self) -> dict[str, object]:
        return {
            "source": self.source,
            "lines_used": self.lines_used,
            "scenario": self.scenario,
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
    scenario: str | None = None,
) -> LogAnalysisResult:
    cleaned = text.strip()
    if not cleaned:
        raise ValidationError(code="VALIDATION_ERROR", message="log text is empty")
    if ai is None:
        raise AppError(code="MISSING_TOKEN", status_code=503)

    scenario_key = resolve_scenario(scenario)
    system_prompt = SCENARIO_PROMPTS[scenario_key]

    lines_used = len(cleaned.splitlines())
    # Cap payload size for local small models.
    if len(cleaned) > 40_000:
        cleaned = cleaned[-40_000:]
        source = f"{source}+truncated"

    cleaned = redact_secrets(cleaned)

    analysis = ai.generate(
        system_prompt,
        f"Сценарий: {scenario_key}\nЛоги ({source}, ~{lines_used} строк):\n\n{cleaned}",
    ).strip()
    if not analysis:
        raise AppError(code="API_EMPTY", status_code=502)
    return LogAnalysisResult(
        source=source,
        lines_used=lines_used,
        analysis=analysis,
        scenario=scenario_key,
    )


def analyze_log_file(
    ai: AiGenerator | None,
    *,
    max_lines: int = 200,
    path: Path | None = None,
    scenario: str | None = None,
) -> LogAnalysisResult:
    text = read_log_tail(path, max_lines=max_lines)
    return analyze_log_text(
        text,
        ai,
        source=str(path or log_file_path()),
        scenario=scenario,
    )


# Back-compat alias for older imports / docs
ANALYZE_SYSTEM_PROMPT = SCENARIO_PROMPTS[DEFAULT_SCENARIO]
