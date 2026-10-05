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
from core.rag_service import RagService
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
from infrastructure.rag_memory_store import (
    MemoryCaseChunkRepository,
    MemoryDocumentChunkRepository,
)
from infrastructure.rag_supabase_store import (
    SupabaseCaseChunkRepository,
    SupabaseDocumentChunkRepository,
)
from infrastructure.supabase_rest import SupabaseRestClient, SupabaseRestConfig
from infrastructure.supabase_store import (
    SupabaseDocumentRepository,
    SupabaseRunRepository,
    SupabaseSettingsRepository,
    SupabaseTestCaseRepository,
)
from integrations.ai_client import build_ai_client, load_ai_settings
from integrations.embedding_client import build_embedding_client, load_embedding_settings

PUBLIC_API_PATHS = frozenset(
    {
        "/api/health",
        "/api/ai/ping",
        "/api/auth/oauth/status",
        "/api/auth/oauth/yandex/start",
        "/api/auth/oauth/yandex/callback",
    }
)


def _is_public_or_production_env() -> bool:
    """True when AUTH_DEV_BYPASS must never apply (PaaS / explicit prod)."""
    for key in ("FLASK_ENV", "ENV", "APP_ENV"):
        if os.getenv(key, "").strip().lower() == "production":
            return True
    if os.getenv("PUBLIC_DEPLOY", "").strip() == "1":
        return True
    # Common hosted markers — treat as public even if AUTH_DEV_BYPASS leaked into env.
    if any(
        os.getenv(name)
        for name in (
            "RAILWAY_ENVIRONMENT",
            "RENDER",
            "FLY_APP_NAME",
            "VERCEL",
            "HEROKU_APP_NAME",
        )
    ):
        return True
    return False


def _auth_dev_bypass_enabled(testing: bool) -> bool:
    """Allow JWT bypass only in pytest or local non-public debug."""
    if testing:
        return True
    if os.getenv("AUTH_DEV_BYPASS", "").strip() != "1":
        return False
    if _is_public_or_production_env():
        return False
    return True


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


def _build_repositories(
    testing: bool,
) -> tuple[object, object, object, object, object | None, object | None, str]:
    """Return docs/runs/cases/settings/doc_chunks/case_chunks + persist mode."""
    backend = (os.getenv("PERSIST_BACKEND") or "auto").strip().lower()
    if testing or backend == "memory":
        return (
            MemoryDocumentRepository(),
            MemoryRunRepository(),
            MemoryTestCaseRepository(),
            MemorySettingsRepository(),
            MemoryDocumentChunkRepository(),
            MemoryCaseChunkRepository(),
            "memory",
        )

    config = SupabaseRestConfig.from_env()
    if config is None or backend not in {"supabase", "auto"}:
        return (
            MemoryDocumentRepository(),
            MemoryRunRepository(),
            MemoryTestCaseRepository(),
            MemorySettingsRepository(),
            MemoryDocumentChunkRepository(),
            MemoryCaseChunkRepository(),
            "memory",
        )

    client = SupabaseRestClient(config)
    return (
        SupabaseDocumentRepository(client),
        SupabaseRunRepository(client),
        SupabaseTestCaseRepository(client),
        SupabaseSettingsRepository(client),
        SupabaseDocumentChunkRepository(client),
        SupabaseCaseChunkRepository(client),
        "supabase",
    )


def create_app(testing: bool = False) -> Flask:
    load_dotenv()
    app = Flask(__name__)
    app.config["TESTING"] = testing
    logger = configure_logging(testing=testing)
    app.extensions["logger"] = logger

    if not testing and os.getenv("AUTH_DEV_BYPASS", "").strip() == "1" and _is_public_or_production_env():
        logger.warning(
            "AUTH_DEV_BYPASS=1 is set but ignored in public/production environment "
            "(FLASK_ENV/ENV/APP_ENV=production, PUBLIC_DEPLOY=1, or PaaS markers)."
        )

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

    (
        docs_repo,
        runs_repo,
        cases_repo,
        settings_repo,
        doc_chunks_repo,
        case_chunks_repo,
        persist_mode,
    ) = _build_repositories(testing)
    doc_storage = build_document_storage(testing=testing)
    ai_settings = load_ai_settings()
    ai_client = build_ai_client(ai_settings)
    embedding_settings = load_embedding_settings()
    # Tests use deterministic hash embeddings (no network).
    if testing:
        os.environ.setdefault("EMBEDDING_PROVIDER", "hash")
        embedding_settings = load_embedding_settings()
    embedding_client = build_embedding_client(embedding_settings)
    rag_service = RagService(
        doc_chunks=doc_chunks_repo,
        case_chunks=case_chunks_repo,
        embedder=embedding_client,
    )
    document_service = DocumentService(docs_repo, doc_storage, rag_service)

    app.extensions["persist_mode"] = persist_mode
    app.extensions["docs_repo"] = docs_repo
    app.extensions["runs_repo"] = runs_repo
    app.extensions["cases_repo"] = cases_repo
    app.extensions["settings_repo"] = settings_repo
    app.extensions["document_storage"] = doc_storage
    app.extensions["document_service"] = document_service
    app.extensions["run_service"] = RunService(runs_repo, docs_repo)
    app.extensions["testcase_service"] = TestCaseService(cases_repo, runs_repo, rag_service)
    app.extensions["settings_service"] = SettingsService(settings_repo)
    app.extensions["rag_service"] = rag_service
    app.extensions["generation_service"] = GenerationService(
        runs_repo,
        docs_repo,
        cases_repo,
        ai_client,
        document_service,
        rag_service=rag_service,
    )
    app.extensions["ai_settings"] = ai_settings
    app.extensions["ai_client"] = ai_client
    app.extensions["embedding_settings"] = embedding_settings
    app.extensions["embedding_client"] = embedding_client

    from app.oauth_routes import oauth_bp
    from app.routes import api_bp

    app.register_blueprint(api_bp)
    app.register_blueprint(oauth_bp)

    @app.before_request
    def bind_request_context() -> None:
        g.request_id = request.headers.get("X-Request-Id", "").strip() or str(uuid.uuid4())
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

        # Dev/test bypass — never on public/PaaS (see _auth_dev_bypass_enabled).
        if _auth_dev_bypass_enabled(testing):
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
    def security_headers(response):
        """Baseline browser hardening (B1a — no aggressive CSP yet)."""
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=()",
        )
        return response

    @app.after_request
    def access_log(response):
        if not request.path.startswith("/api/"):
            return response
        response.headers["X-Request-Id"] = getattr(g, "request_id", "")
        started = getattr(g, "request_started_at", None)
        duration_ms = round((time.perf_counter() - started) * 1000, 2) if started else None
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
