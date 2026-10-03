"""Flask application factory."""

from __future__ import annotations

import os
import time
import uuid

from dotenv import load_dotenv
from flask import Flask, g, jsonify, request
from flask_cors import CORS

from app.auth import verify_supabase_access_token
from core.errors import AppError, ForbiddenError, UnauthorizedError
from core.messages import ERROR_MESSAGES
from core.services import (
    DocumentService,
    GenerationService,
    RunService,
    SettingsService,
    TestCaseService,
)
from infrastructure.document_storage import build_document_storage
from infrastructure.logging_setup import configure_logging, get_logger
from infrastructure.memory_store import (
    MemoryDocumentRepository,
    MemoryRunRepository,
    MemorySettingsRepository,
    MemoryTestCaseRepository,
)
from infrastructure.supabase_rest import SupabaseRestClient, SupabaseRestConfig
from infrastructure.supabase_store import (
    SupabaseDocumentRepository,
    SupabaseRunRepository,
    SupabaseSettingsRepository,
    SupabaseTestCaseRepository,
)
from integrations.ai_client import build_ai_client, load_ai_settings

PUBLIC_API_PATHS = frozenset({"/api/health", "/api/ai/ping"})


def _cors_origins() -> list[str]:
    raw = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://localhost:8080")
    return [o.strip() for o in raw.split(",") if o.strip()]


def _error_body(code: str, status_code: int, message: str | None = None) -> dict:
    msg = message or ERROR_MESSAGES.get(code, ERROR_MESSAGES["INTERNAL_ERROR"])
    body: dict = {"error": {"code": code, "message": msg}}
    request_id = getattr(g, "request_id", None)
    if request_id:
        body["error"]["request_id"] = request_id
    return body


def _build_repositories(testing: bool) -> tuple[object, object, object, object, str]:
    """Return docs/runs/cases/settings repos + persistence mode label.

    Selection:
    - testing / PERSIST_BACKEND=memory → in-memory
    - PERSIST_BACKEND=supabase|auto + SUPABASE_URL(+anon/service) → PostgREST
    """
    backend = (os.getenv("PERSIST_BACKEND") or "auto").strip().lower()
    if testing or backend == "memory":
        return (
            MemoryDocumentRepository(),
            MemoryRunRepository(),
            MemoryTestCaseRepository(),
            MemorySettingsRepository(),
            "memory",
        )

    config = SupabaseRestConfig.from_env()
    if config is None or backend not in {"supabase", "auto"}:
        return (
            MemoryDocumentRepository(),
            MemoryRunRepository(),
            MemoryTestCaseRepository(),
            MemorySettingsRepository(),
            "memory",
        )

    client = SupabaseRestClient(config)
    return (
        SupabaseDocumentRepository(client),
        SupabaseRunRepository(client),
        SupabaseTestCaseRepository(client),
        SupabaseSettingsRepository(client),
        "supabase",
    )


def create_app(testing: bool = False) -> Flask:
    load_dotenv()
    app = Flask(__name__)
    app.config["TESTING"] = testing
    logger = configure_logging(testing=testing)
    app.extensions["logger"] = logger

    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": _cors_origins(),
                "methods": ["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
                "allow_headers": [
                    "Authorization",
                    "Content-Type",
                    "X-User-Id",
                    "X-Skip-Auth",
                    "X-Request-Id",
                    "X-Admin-Token",
                ],
                "expose_headers": ["Content-Type", "X-Request-Id"],
                "supports_credentials": True,
            }
        },
    )

    docs_repo, runs_repo, cases_repo, settings_repo, persist_mode = _build_repositories(
        testing
    )
    doc_storage = build_document_storage(testing=testing)
    ai_settings = load_ai_settings()
    ai_client = build_ai_client(ai_settings)
    document_service = DocumentService(docs_repo, doc_storage)

    app.extensions["persist_mode"] = persist_mode
    app.extensions["docs_repo"] = docs_repo
    app.extensions["runs_repo"] = runs_repo
    app.extensions["cases_repo"] = cases_repo
    app.extensions["settings_repo"] = settings_repo
    app.extensions["document_storage"] = doc_storage
    app.extensions["document_service"] = document_service
    app.extensions["run_service"] = RunService(runs_repo, docs_repo)
    app.extensions["testcase_service"] = TestCaseService(cases_repo, runs_repo)
    app.extensions["settings_service"] = SettingsService(settings_repo)
    app.extensions["generation_service"] = GenerationService(
        runs_repo, docs_repo, cases_repo, ai_client, document_service
    )
    app.extensions["ai_settings"] = ai_settings
    app.extensions["ai_client"] = ai_client

    from app.routes import api_bp

    app.register_blueprint(api_bp)

    @app.before_request
    def bind_request_context() -> None:
        g.request_id = (
            request.headers.get("X-Request-Id", "").strip() or str(uuid.uuid4())
        )
        g.request_started_at = time.perf_counter()
        g.user_id = None
        g.access_token = None
        g.user_email = None

    @app.before_request
    def load_user() -> None:
        if request.method == "OPTIONS":
            return
        if not request.path.startswith("/api/"):
            return
        if request.path in PUBLIC_API_PATHS:
            return

        auth = request.headers.get("Authorization", "")
        bearer = auth[7:].strip() if auth.startswith("Bearer ") else ""

        if bearer:
            try:
                user = verify_supabase_access_token(bearer)
            except UnauthorizedError:
                raise UnauthorizedError() from None
            g.user_id = user.user_id
            g.access_token = bearer
            g.user_email = user.email
            return

        # Dev/test bypass only — never trusted in production.
        if testing or os.getenv("AUTH_DEV_BYPASS", "").strip() == "1":
            if request.headers.get("X-Skip-Auth") == "1":
                raise UnauthorizedError()
            user_id = request.headers.get("X-User-Id", "").strip()
            # Default identity for local FE (no JWT) and pytest when header omitted.
            if not user_id:
                user_id = "00000000-0000-4000-8000-000000000001"
            g.user_id = user_id
            g.access_token = None
            g.user_email = None
            return

        raise UnauthorizedError()

    @app.after_request
    def access_log(response):
        if not request.path.startswith("/api/"):
            return response
        response.headers["X-Request-Id"] = getattr(g, "request_id", "")
        started = getattr(g, "request_started_at", None)
        duration_ms = (
            round((time.perf_counter() - started) * 1000, 2) if started else None
        )
        get_logger().info(
            "request",
            extra={
                "request_id": getattr(g, "request_id", None),
                "user_id": getattr(g, "user_id", None),
                "method": request.method,
                "path": request.path,
                "status": response.status_code,
                "duration_ms": duration_ms,
                "remote_addr": request.headers.get("X-Forwarded-For", request.remote_addr),
            },
        )
        return response

    @app.errorhandler(AppError)
    def handle_app_error(exc: AppError):
        level = logging_level_for_status(exc.status_code)
        get_logger().log(
            level,
            "app_error %s",
            exc.code,
            extra={
                "request_id": getattr(g, "request_id", None),
                "user_id": getattr(g, "user_id", None),
                "method": request.method,
                "path": request.path,
                "status": exc.status_code,
                "error_code": exc.code,
            },
        )
        return jsonify(_error_body(exc.code, exc.status_code, exc.message)), exc.status_code

    @app.errorhandler(404)
    def handle_404(_exc):
        get_logger().warning(
            "not_found",
            extra={
                "request_id": getattr(g, "request_id", None),
                "user_id": getattr(g, "user_id", None),
                "method": request.method,
                "path": request.path,
                "status": 404,
                "error_code": "NOT_FOUND",
            },
        )
        return jsonify(_error_body("NOT_FOUND", 404)), 404

    @app.errorhandler(403)
    def handle_http_403(_exc):
        return jsonify(_error_body("FORBIDDEN", 403)), 403

    @app.errorhandler(401)
    def handle_http_401(_exc):
        return jsonify(_error_body("UNAUTHORIZED", 401)), 401

    @app.errorhandler(405)
    def handle_405(_exc):
        return jsonify(_error_body("VALIDATION_ERROR", 405)), 405

    @app.errorhandler(Exception)
    def handle_unexpected(exc: Exception):
        get_logger().exception(
            "unhandled_exception",
            extra={
                "request_id": getattr(g, "request_id", None),
                "user_id": getattr(g, "user_id", None),
                "method": request.method,
                "path": request.path,
                "status": 500,
                "error_code": "INTERNAL_ERROR",
            },
        )
        if app.config.get("TESTING"):
            raise
        return jsonify(_error_body("INTERNAL_ERROR", 500)), 500

    if testing:

        @app.get("/api/__test__/forbidden")
        def _test_forbidden():
            raise ForbiddenError()

        @app.get("/api/__test__/internal")
        def _test_internal():
            raise AppError(code="INTERNAL_ERROR", status_code=500)

    return app


def logging_level_for_status(status_code: int) -> int:
    import logging

    if status_code >= 500:
        return logging.ERROR
    if status_code in {401, 403}:
        return logging.WARNING
    if status_code >= 400:
        return logging.INFO
    return logging.INFO
